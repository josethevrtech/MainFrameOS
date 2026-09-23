#!/usr/bin/env python3
"""Compile a pinned candidate device tree; never write host boot files."""
import json
import os
from pathlib import Path
import shutil
import sys
import tarfile
import tempfile

from build import ROOT, BUILD, OUT, LOCK, container, digest, fetch, validate_builder


def main():
    lock = json.loads(LOCK.read_text())
    source = lock['kernel_candidate']
    builder = validate_builder(lock)
    archive = BUILD / 'downloads' / source['filename']
    fetch(source['url'], archive, source['sha256'])
    work = BUILD / 'kernel-candidate'
    work.mkdir(exist_ok=True)
    tree = work / ('linux_ms_dev_kit-' + source['commit'])
    if tree.exists():
        raise ValueError(f'{tree} already exists; move the previous build directory before a clean rebuild')
    # Ubuntu packaging includes an absolute symlink unrelated to Kbuild.
    # Omit that packaging layer; keep Python's safe data filter for kernel files.
    with tempfile.TemporaryDirectory(dir=work, prefix='extract-') as temp:
        with tarfile.open(archive) as tar:
            def kernel_filter(member, destination):
                parts = Path(member.name).parts
                if len(parts) > 1 and parts[1] in ('debian', 'debian.master', 'debian.qcom-x1e'):
                    return None
                return tarfile.data_filter(member, destination)
            tar.extractall(temp, filter=kernel_filter)
        (Path(temp) / tree.name).rename(tree)
    if not (tree / 'Makefile').is_file():
        raise ValueError('unexpected kernel archive layout')
    common = ['run', '--rm', '--network=none', '--userns=keep-id:uid=1000,gid=1000',
              '--user', '1000:1000', '--cap-drop=ALL',
              '--security-opt=no-new-privileges', '--memory=3g', '--cpus=2', '--pids-limit=256',
              '-e', 'KBUILD_BUILD_USER=mainframeos', '-e', 'KBUILD_BUILD_HOST=builder',
              '-e', 'KBUILD_BUILD_TIMESTAMP=2026-09-23 00:00:00 UTC',
              '-v', f'{work}:/work:rw', '-w', '/work/' + tree.name, builder['image']]
    container(*common, 'make', 'O=/work/obj', 'ARCH=arm64', 'defconfig')
    container(*common, 'make', '-j2', 'O=/work/obj', 'ARCH=arm64', source['dtb_target'])
    result = work / 'obj/arch/arm64/boot/dts' / source['dtb_target']
    output = OUT / 'kernel-candidate'
    output.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(result, output / result.name)
    shutil.copyfile(work / 'obj/.config', output / 'kernel.config')
    report = {'schema_version': 1, 'source_commit': source['commit'], 'source_sha256': source['sha256'],
              'builder': builder, 'target': source['dtb_target'],
              'dtb_sha256': digest(result), 'config_sha256': digest(output / 'kernel.config'),
              'configuration': 'upstream arm64 defconfig; not recovered installed kernel config',
              'boot_tested': False, 'release_ready': False,
              'scope': 'device-tree compiler and candidate DTB compilation only; no kernel Image or modules'}
    (output / 'build.json').write_text(json.dumps(report, indent=2) + '\n')
    print(json.dumps(report, indent=2))


if __name__ == '__main__':
    try:
        main()
    except (ValueError, OSError) as error:
        sys.exit(f'kernel build failed: {error}')
