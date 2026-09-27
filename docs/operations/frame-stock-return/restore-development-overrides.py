#!/usr/bin/env python3
from pathlib import Path
import hashlib,json,shutil
base=Path(__file__).resolve().parent
home=base.parent.parent
rows=json.loads((base/'overrides.json').read_text())
for row in rows:
 src=base/'saved-overrides'/row['path']; dst=home/row['path']
 assert hashlib.sha256(src.read_bytes()).hexdigest()==row['sha256'], 'Backup hash mismatch'
 assert not dst.exists() or (dst.is_file() and hashlib.sha256(dst.read_bytes()).hexdigest()==row['sha256']), 'Destination changed: '+str(dst)
for row in rows:
 src=base/'saved-overrides'/row['path']; dst=home/row['path']
 dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(src,dst)
print('Development overrides restored. Select slot B and reboot; no services restarted.')
