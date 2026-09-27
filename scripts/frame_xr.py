#!/usr/bin/env python3
"""Prepare pinned Frame XR sources. No downloads, installation or headset access."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile
import tempfile

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / 'packages/mainframeos-frame-xr'
LOCK = ROOT / 'upstream/frame-xr.lock.json'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def inputs():
    lock = json.loads(LOCK.read_text())
    if lock['schema_version'] != 1:
        raise ValueError('unsupported source lock')
    for name, expected in lock['files'].items():
        if Path(name).name != name or sha(RECIPE / name) != expected:
            raise ValueError(f'recipe input changed: {name}')
    if not set(lock['patches']).issubset(lock['files']):
        raise ValueError('unhashed patch')
    return lock


def inventory(root):
    result = {}
    for p in sorted(root.rglob('*')):
        if p.name == '.mainframeos-source.json':
            continue
        if p.is_symlink():
            raise ValueError(f'unexpected source symlink: {p.relative_to(root)}')
        if p.is_file():
            result[str(p.relative_to(root))] = sha(p)
    return result


def verify(source):
    lock = inputs()
    record = json.loads((source / '.mainframeos-source.json').read_text())
    if record['lock_sha256'] != sha(LOCK) or record['commit'] != lock['commit']:
        raise ValueError('prepared source uses a different lock')
    if inventory(source) != record['files']:
        raise ValueError('prepared source was changed after reconstruction')
    return record


def prepare(repo, optics, destination):
    lock = inputs()
    if destination.exists() or destination.is_symlink():
        raise ValueError('destination must not exist; existing builds are never overwritten')
    if sha(optics) != lock['optics']['sha256']:
        raise ValueError('optical reference differs from the validated experiment')
    tree = subprocess.check_output(['git', '-C', str(repo), 'rev-parse',
                                    lock['commit'] + '^{tree}'], text=True).strip()
    if tree != lock['tree']:
        raise ValueError('source tree mismatch')
    destination.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='frame-xr-', dir=destination.parent) as tmp:
        tmp = Path(tmp)
        archive = tmp / 'source.tar'
        subprocess.run(['git', '-C', str(repo), 'archive', '--format=tar',
                        '-o', str(archive), lock['commit']], check=True)
        stage = tmp / 'source'
        stage.mkdir()
        with tarfile.open(archive) as tf:
            tf.extractall(stage, filter='data')
        for name in lock['patches']:
            patch = RECIPE / name
            subprocess.run(['git', 'apply', '--check', str(patch)], cwd=stage, check=True,
                           env={**os.environ, 'GIT_CEILING_DIRECTORIES': str(tmp)})
            subprocess.run(['git', 'apply', str(patch)], cwd=stage, check=True,
                           env={**os.environ, 'GIT_CEILING_DIRECTORIES': str(tmp)})
        subprocess.run([sys.executable, str(RECIPE / 'generate-optics.py'), str(optics),
                        str(stage / 'src/xrt/drivers/remote/r_frame_optics.h')], check=True)
        record = {'schema_version': 1, 'commit': lock['commit'], 'tree': tree,
                  'lock_sha256': sha(LOCK), 'archive_sha256': sha(archive),
                  'files': inventory(stage), 'hardware_validated': False}
        (stage / '.mainframeos-source.json').write_text(json.dumps(record, indent=2) + '\n')
        stage.rename(destination)
    print(f'Prepared {len(record["files"])} verified files in {destination}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('check-inputs')
    p = sub.add_parser('prepare')
    p.add_argument('--repository', type=Path, required=True)
    p.add_argument('--optics', type=Path, required=True)
    p.add_argument('--destination', type=Path, required=True)
    p = sub.add_parser('verify')
    p.add_argument('source', type=Path)
    args = parser.parse_args()
    if args.command == 'prepare':
        prepare(args.repository.resolve(), args.optics.resolve(), args.destination.absolute())
    elif args.command == 'verify':
        verify(args.source.resolve())
        print('Prepared source inventory verified')
    else:
        inputs()
        print('Frame XR recipe inputs verified')


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, KeyError, subprocess.CalledProcessError) as error:
        sys.exit(f'Frame XR preparation failed: {error}')
