#!/usr/bin/env python3
"""Generate device-specific Monado optical reference data, without a runtime OpenVR dependency."""
import json,math,sys,hashlib
from pathlib import Path
src=Path(sys.argv[1]);out=Path(sys.argv[2]);d=json.loads(src.read_text());n=d['cells'];assert n==128
assert len(d['eyes'])==2 and d['render_size']==[1728,1728]
def ff(v):
 assert math.isfinite(v)
 return f'{float(v):.9e}f'
text=['/* Generated device-specific optical reference; regenerate with generate-optics.py. */',f'/* Input SHA256: {hashlib.sha256(src.read_bytes()).hexdigest()} */',f'#define FRAME_OPTICS_CELLS {n}']
fovs=[];positions=[]
for e in d['eyes']:
 assert len(e['grid'])==(n+1)**2
 m=e['eye_to_head'];assert len(m)==12
 for i in range(3):
  for j in range(3):assert abs(m[i*4+j]-(i==j))<1e-6,'Nonidentity eye rotation requires implementation'
 positions.append([m[3],m[7],m[11]])
 l,r,t,b=e['projection_tangents'];assert l<0<r and t<0<b
 fovs.append([math.atan(l),math.atan(r),math.atan(b),math.atan(t)])
 assert e['midpoint_check']['max_inside_uv_error']<.0006
assert .05 < positions[1][0]-positions[0][0] < .08
for name,rows in [('frame_fovs',fovs),('frame_eye_positions',positions)]:
 text.append(f'static const float {name}[2][{len(rows[0])}] = {{')
 for row in rows:text.append('{'+','.join(ff(v) for v in row)+'},')
 text.append('};')
text.append(f'static const float frame_uv[2][{(n+1)**2}][6] = {{')
for e in d['eyes']:
 text.append('{')
 for row in e['grid']:
  assert len(row)==6
  text.append('{'+','.join(ff(v) for v in row)+'},')
 text.append('},')
text.append('};\n');out.write_text('\n'.join(text))
print('Generated optical map',n+1,'x',n+1,'per eye; IPD metres',positions[1][0]-positions[0][0])
