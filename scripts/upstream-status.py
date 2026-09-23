#!/usr/bin/env python3
"""Read-only source drift report; never automatically updates a source lock."""
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request

root = Path(__file__).resolve().parents[1]
lock = json.loads((root / 'upstream/sources.lock.json').read_text())
report = {}
for name, ref in [('collabora', 'HEAD'), ('kernel_candidate', 'refs/tags/' + lock['kernel_candidate']['tag'])]:
    value = lock[name]
    result = subprocess.run(['git', 'ls-remote', value['repository'], ref], check=True, capture_output=True, text=True, timeout=60)
    observed = result.stdout.split()[0]
    report[name] = {'locked': value['commit'], 'observed': observed, 'changed': observed != value['commit']}
with urllib.request.urlopen(lock['bootstrap']['signature_url'], timeout=60) as response:
    if not response.url.startswith('https://'):
        raise ValueError('insecure redirect')
    content = response.read(65537)
    if len(content) > 65536:
        raise ValueError('signature unexpectedly large')
    sha = hashlib.sha256(content).hexdigest()
    report['bootstrap_signature'] = {'locked': lock['bootstrap']['signature_sha256'], 'observed': sha,
                                     'changed': sha != lock['bootstrap']['signature_sha256']}
print(json.dumps(report, indent=2))
