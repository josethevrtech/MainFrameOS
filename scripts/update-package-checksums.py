#!/usr/bin/env python3
"""Synchronize local package inputs and checksums; never run downloaded code."""
import hashlib
from pathlib import Path
import re
import shutil

root = Path(__file__).resolve().parents[1]
package = root / 'packages/mainframeos-support'
shutil.copyfile(root / 'LICENSE', package / 'LICENSE')
shutil.copyfile(root / 'devices/hp-omnibook5-8e33.json', package / 'hp-omnibook5-8e33.json')
names = ['mainframeos-support', 'LICENSE', 'hp-omnibook5-8e33.json']
checksums = ['  ' + repr(hashlib.sha256((package / name).read_bytes()).hexdigest()) for name in names]
p = package / 'PKGBUILD'
p.write_text(re.sub(r'sha256sums=\([^)]*\)', 'sha256sums=(\n' + '\n'.join(checksums) + '\n)', p.read_text()))
