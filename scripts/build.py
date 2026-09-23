#!/usr/bin/env python3
"""Verified ALARM bootstrap and isolated package builds. Does not install on host."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import time
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
BUILD = ROOT / 'build'
OUT = ROOT / 'out'
LOCK = ROOT / 'upstream/sources.lock.json'


def run(*args, **kwargs):
    return subprocess.run(args, check=True, text=True, **kwargs)


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def fetch(url, path, expected):
    if path.exists():
        if digest(path) != expected:
            raise ValueError(f'checksum mismatch: {path}; remove the bad cached file explicitly')
        return
    if not url.startswith('https://'):
        raise ValueError('HTTPS source required')
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_suffix(path.suffix + '.part')
    try:
        with urllib.request.urlopen(url, timeout=60) as response, temp.open('wb') as dest:
            if not response.url.startswith('https://'):
                raise ValueError('insecure redirect')
            shutil.copyfileobj(response, dest)
        if digest(temp) != expected:
            raise ValueError('download checksum mismatch; upstream latest may have changed; review the lock')
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def verify_bootstrap(lock):
    b = lock['bootstrap']
    archive = BUILD / 'downloads' / b['filename']
    sig = archive.with_name(archive.name + '.sig')
    fetch(b['url'], archive, b['sha256'])
    fetch(b['signature_url'], sig, b['signature_sha256'])
    with tempfile.TemporaryDirectory(prefix='mainframeos-gpg-') as tmp:
        run('gpg', '--homedir', tmp, '--batch', '--import', str(ROOT / b['key_file']), capture_output=True)
        result = run('gpg', '--homedir', tmp, '--batch', '--status-fd', '1', '--verify', str(sig), str(archive), capture_output=True)
        valid = [line.split() for line in result.stdout.splitlines() if line.startswith('[GNUPG:] VALIDSIG ')]
        if not any(row[2] == b['signer_fingerprint'] or row[-1] == b['signer_fingerprint'] for row in valid):
            raise ValueError('bootstrap signature did not match pinned upstream signing key')
    return archive


def container(*args, **kwargs):
    return run('podman', *args, **kwargs)


def bootstrap(lock):
    if platform.machine() != 'aarch64':
        raise ValueError('native aarch64 builder required; cross-architecture host setup is not automatic')
    if os.geteuid() == 0:
        raise ValueError('run as a normal user with rootless Podman')
    if container('info', '--format', '{{.Host.Security.Rootless}}', capture_output=True).stdout.strip() != 'true':
        raise ValueError('rootless Podman required')
    archive = verify_bootstrap(lock)
    base = container('import', '--arch', 'arm64', '--os', 'linux', str(archive), capture_output=True).stdout.strip()
    container('build', '--build-arg', f'BASE={base}', '--file', str(ROOT / 'build-support/Containerfile'),
              '--iidfile', str(BUILD / 'builder-id'), str(ROOT / 'build-support'))
    image = (BUILD / 'builder-id').read_text().strip()
    packages = container('run', '--rm', '--network=none', image, 'cat',
                         '/usr/share/mainframeos-build/packages.txt', capture_output=True).stdout
    (BUILD / 'builder-packages.txt').write_text(packages)
    (BUILD / 'builder.json').write_text(json.dumps({'schema_version': 1, 'image': image,
        'bootstrap_sha256': lock['bootstrap']['sha256'], 'package_inventory_sha256': digest(BUILD / 'builder-packages.txt'),
        'containerfile_sha256': digest(ROOT / 'build-support/Containerfile')}, indent=2) + '\n')
    print('Builder created; freeze/reuse its image ID. A fresh bootstrap resolves current ALARM packages.')


def validate_builder(lock):
    state = json.loads((BUILD / 'builder.json').read_text())
    if state['containerfile_sha256'] != digest(ROOT / 'build-support/Containerfile'):
        raise ValueError('builder recipe changed; rebuild explicitly')
    if state['bootstrap_sha256'] != lock['bootstrap']['sha256']:
        raise ValueError('bootstrap lock changed; rebuild explicitly')
    return state


def stage_recipe(source, work):
    # Only the generated package workspace is disposable; never overlay old inputs.
    if work.is_symlink():
        raise ValueError('package workspace must not be a symlink')
    if work.exists():
        shutil.rmtree(work)
    shutil.copytree(source, work, ignore=shutil.ignore_patterns('__pycache__'))


def build_package(lock, package):
    if package not in ('mainframeos-support', 'compat-json-c'):
        raise ValueError('unknown package')
    state = validate_builder(lock)
    OUT.mkdir(exist_ok=True)
    work = BUILD / 'packages' / package
    source = ROOT / 'packages' / package
    stage_recipe(source, work)
    if package == 'compat-json-c':
        expected = lock['collabora']['files']
        for path, checksum in expected.items():
            if digest(source / path) != checksum:
                raise ValueError(f'vendored upstream recipe changed: {path}')
    common = ['run', '--rm', '--userns=keep-id:uid=1000,gid=1000', '--user', '1000:1000',
              '--cap-drop=ALL', '--security-opt=no-new-privileges',
              '--pids-limit=256', '--memory=3g', '--cpus=2',
              '-e', 'HOME=/tmp', '-e', 'LC_ALL=C.UTF-8', '-e', 'TZ=UTC',
              '-e', f"SOURCE_DATE_EPOCH={lock['source_date_epoch']}", '-e', 'PACKAGER=MainFrameOS build pipeline',
              '-v', f'{work}:/work:rw', '-v', f'{OUT}:/out:rw', '-w', '/work']
    # Network is available only during source retrieval/verification.
    container(*common, state['image'], 'makepkg', '--verifysource', '--noconfirm')
    container(*common, '--network=none', '-e', 'PKGDEST=/out', state['image'],
              'makepkg', '--cleanbuild', '--holdver', '--force', '--noconfirm')
    listed = container(*common, '--network=none', '-e', 'PKGDEST=/out', state['image'],
                       'makepkg', '--packagelist', capture_output=True).stdout.splitlines()
    if not listed or any(Path(p).parent != Path('/out') for p in listed):
        raise ValueError('unexpected package output paths')
    artifacts = [OUT / Path(p).name for p in listed]
    if not artifacts:
        raise ValueError('no built package found')
    report = {'schema_version': 1, 'package_recipe': package, 'architecture': 'aarch64',
              'builder': state, 'source_lock_sha256': digest(LOCK),
              'source_date_epoch': lock['source_date_epoch'],
              'recipe_sha256': digest(source / 'PKGBUILD'),
              'recipe_inputs': {str(p.relative_to(source)): digest(p) for p in sorted(source.rglob('*'))
                                if p.is_file() and '__pycache__' not in p.parts},
              'build_script_sha256': digest(Path(__file__)),
              'git_commit': run('git', '-C', str(ROOT), 'rev-parse', 'HEAD', capture_output=True).stdout.strip(),
              'working_tree_dirty': bool(run('git', '-C', str(ROOT), 'status', '--porcelain', capture_output=True).stdout),
              'artifacts': {p.name: digest(p) for p in artifacts},
              'release_signed': False, 'bootable_image': False}
    (OUT / f'{package}.build.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('command', choices=['verify-bootstrap', 'bootstrap', 'package'])
    p.add_argument('package', nargs='?', choices=['mainframeos-support', 'compat-json-c'])
    args = p.parse_args()
    BUILD.mkdir(exist_ok=True)
    lock = json.loads(LOCK.read_text())
    if not isinstance(lock['source_date_epoch'], int) or not 0 < lock['source_date_epoch'] <= time.time():
        raise ValueError('SOURCE_DATE_EPOCH must be a positive timestamp in the past')
    if args.command == 'verify-bootstrap':
        print(verify_bootstrap(lock))
    elif args.command == 'bootstrap':
        bootstrap(lock)
    elif args.package:
        build_package(lock, args.package)
    else:
        p.error('package name required')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f'build failed: {error}')
