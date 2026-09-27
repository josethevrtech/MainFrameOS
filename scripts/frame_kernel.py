#!/usr/bin/env python3
"""Read-only Frame kernel reference capture and drift comparison; never update locks."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import platform
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
REFERENCE = ROOT / 'kernels/frame/reference.lock.json'


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def compare(reference, observed):
    # Source access/commit is deliberately not inferred from a binary's version string.
    fields = ['compatible', 'kernel_release', 'kernel_sha256', 'dtb_sha256',
              'config_sha256', 'packages', 'modules']
    changed = {k: {'reference': reference.get(k), 'observed': observed.get(k)}
               for k in fields if reference.get(k) != observed.get(k)}
    return {'schema_version': 1, 'changed': bool(changed), 'changes': changed,
            'action': 'Review new hardware reference and rebuild/test before adoption' if changed
                      else 'Installed reference unchanged; upstream publication status not checked',
            'automatic_adoption': False}


def capture(destination):
    compatible = Path('/sys/firmware/devicetree/base/compatible').read_bytes().rstrip(b'\0').decode().split('\0')
    if compatible != ['qcom,sm8650-dv1', 'qcom,sm8650']:
        raise ValueError('unrecognized hardware; refusing a misleading Frame reference')
    if destination.exists() or destination.is_symlink():
        raise ValueError('destination must not exist')
    release = platform.release()
    if '/' in release or release in ('.', '..'):
        raise ValueError('invalid kernel release')
    module_root = Path('/usr/lib/modules') / release
    if not module_root.is_dir():
        raise ValueError('matching installed modules missing')
    modules = {str(p.relative_to(module_root)): sha(p) for p in sorted(module_root.rglob('*.ko*')) if p.is_file()}
    if not modules:
        raise ValueError('no kernel modules found')
    config = gzip.decompress(Path('/proc/config.gz').read_bytes())
    packages = {}
    for name in ('linux-618-deckard', 'linux-firmware-deckard', 'deckard-uboot', 'deckard-uboot-splctl'):
        query = subprocess.run(['pacman', '-Q', name], capture_output=True, text=True)
        packages[name] = query.stdout.strip().partition(' ')[2] if query.returncode == 0 else None
    record = {'schema_version': 1, 'compatible': compatible, 'kernel_release': release,
              'kernel_sha256': sha(Path('/boot/Image')), 'dtb_sha256': sha(Path('/boot/maindtb.dtb')),
              'config_sha256': hashlib.sha256(config).hexdigest(), 'packages': packages, 'modules': modules}
    destination.mkdir(parents=True)
    (destination / 'kernel.config').write_bytes(config)
    (destination / 'reference.json').write_text(json.dumps(record, indent=2) + '\n')
    print(f'Read-only reference captured in {destination}')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    p = sub.add_parser('capture')
    p.add_argument('destination', type=Path)
    p = sub.add_parser('compare')
    p.add_argument('observed', type=Path)
    p.add_argument('--reference', type=Path, default=REFERENCE)
    args = parser.parse_args()
    if args.command == 'capture':
        capture(args.destination)
    else:
        print(json.dumps(compare(json.loads(args.reference.read_text()),
                                 json.loads(args.observed.read_text())), indent=2))


if __name__ == '__main__':
    try:
        main()
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        sys.exit(f'Frame kernel reference failed: {error}')
