#!/usr/bin/env python3
"""Offline repository contract checks; no third-party Python dependencies."""
import hashlib
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(root=ROOT):
    lock = json.loads((root / 'upstream/sources.lock.json').read_text())
    assert lock['schema_version'] == 1 and lock['base'] == 'archlinuxarm'
    assert lock['architecture'] == 'aarch64'
    assert re.fullmatch('[0-9a-f]{40}', lock['collabora']['commit'])
    assert re.fullmatch('[0-9A-F]{40}', lock['bootstrap']['signer_fingerprint'])
    for key in ('sha256', 'signature_sha256'):
        assert re.fullmatch('[0-9a-f]{64}', lock['bootstrap'][key])
    for key in ('url', 'signature_url'):
        assert lock['bootstrap'][key].startswith('https://')
    for path, checksum in lock['collabora']['files'].items():
        assert sha(root / 'packages/compat-json-c' / path) == checksum, path
    package = root / 'packages/mainframeos-support'
    assert (package / 'LICENSE').read_bytes() == (root / 'LICENSE').read_bytes()
    assert (package / 'hp-omnibook5-8e33.json').read_bytes() == (root / 'devices/hp-omnibook5-8e33.json').read_bytes()
    sums = re.search(r'sha256sums=\((.*?)\)', (package / 'PKGBUILD').read_text(), re.S).group(1)
    assert re.findall(r"'([0-9a-f]{64})'", sums) == [sha(package / p) for p in ('mainframeos-support', 'LICENSE', 'hp-omnibook5-8e33.json')]
    for p in (root / 'devices').glob('*.json'):
        device = json.loads(p.read_text())
        assert device['schema_version'] == 1 and device['architecture'] == 'aarch64'
        assert device['status'] in ('candidate', 'bring-up', 'experimental', 'supported', 'regressed')
        assert set(device['match']) == {'sys_vendor', 'product_name', 'board_name', 'compatible'}
        assert all(isinstance(v, str) and v and '*' not in v for v in device['match'].values())
        assert isinstance(device['release_ready'], bool)
        if device['release_ready']:
            assert device['status'] == 'supported' and not device['blockers']
            assert re.fullmatch('[0-9a-f]{40}', device['kernel']['source_commit'])
            assert all(re.fullmatch('[0-9a-f]{64}', device['kernel'][k]) for k in ('config_sha256', 'dtb_sha256'))
            assert device['firmware']['redistribution_review_complete'] is True
    for p in list(root.glob('*.md')) + list((root / 'docs').rglob('*.md')):
        for target in re.findall(r'\]\(([^)]+)\)', p.read_text()):
            if '://' not in target and not target.startswith('#'):
                assert (p.parent / target.split('#')[0]).exists(), f'{p}: {target}'
    for p in (root / '.github/workflows').glob('*.yml'):
        for action in re.findall(r'uses:\s*(\S+)', p.read_text()):
            assert re.fullmatch(r'[\w-]+/[\w-]+@[0-9a-f]{40}', action), f'unpinned action: {action}'
    print('Repository contracts passed: ALARM base, hashes, profiles, package inputs, links, action pins')


if __name__ == '__main__':
    try:
        check()
    except (AssertionError, KeyError, ValueError, OSError) as error:
        sys.exit(f'Contract check failed: {error}')
