from pathlib import Path
import shutil,hashlib,json
home=Path('/home/steamos')
base=home/'MainFrameOS/stock-return-20260927'
paths=['.config/systemd/user/steamvr-plasma.service.d/90-mainframeos.conf','.config/systemd/user/gamescope-session.service.d/90-mainframeos-ultrawide.conf','.config/autostart/steam.desktop']
rows=[]
for rel in paths:
 src=home/rel; dst=base/'saved-overrides'/rel
 assert src.is_file() and not dst.exists(),rel
 dst.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(src,dst)
 digest=hashlib.sha256(src.read_bytes()).hexdigest()
 assert hashlib.sha256(dst.read_bytes()).hexdigest()==digest
 rows.append({'path':rel,'sha256':digest})
(base/'overrides.json').write_text(json.dumps(rows,indent=2)+'\n')
for row in rows: (home/row['path']).unlink()
print('Saved and set aside three shared-home overrides.')
