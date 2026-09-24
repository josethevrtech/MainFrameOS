#!/usr/bin/env python3
"""Build initial audio topology and stage personally provisioned wireless board data."""
import argparse
import json
import shutil
import tarfile
from pathlib import Path
from build import ROOT, BUILD, OUT, fetch, digest, container
from usb_support import verify_firmware_provenance

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--board',type=Path,required=True)
p.add_argument('--provenance',type=Path,required=True)
p.add_argument('--builder',required=True)
a=p.parse_args()
meta=json.loads(a.provenance.read_text())
verify_firmware_provenance(meta,{'board-2.bin':digest(a.board)})
key=b'bus=pci,vendor=17cb,device=1103,subsystem-vendor=103c,subsystem-device=8d9a,qmi-chip-id=18,qmi-board-id=255'
if key not in a.board.read_bytes():
    raise SystemExit('Wireless board database lacks the initial profile exact calibration key')
lock=json.loads((ROOT/'upstream/audio-source.lock.json').read_text())
archive=BUILD/'downloads'/('audioreach-'+lock['commit']+'.tar.gz')
fetch(lock['url'],archive,lock['sha256'])
work=BUILD/'audio-source'
if work.exists(): raise SystemExit('Move previous build/audio-source aside before rebuilding')
work.mkdir()
with tarfile.open(archive) as t:t.extractall(work,filter='data')
source=work/('audioreach-topology-'+lock['commit'])
out=OUT/'platform-inputs';out.mkdir(exist_ok=True)
container('run','--rm','--network=none','--cap-drop=ALL','--security-opt=no-new-privileges',
          '-v',f'{source}:/src:ro','-v',f'{out}:/dest:rw',a.builder,'sh','-ec',
          'm4 -I /src /src/X1E80100-LENOVO-Thinkpad-T14s.m4 > /dest/topology.conf; '
          'alsatplg -c /dest/topology.conf -o /dest/X1P42100-HP-OMNIBOOK-5-tplg.bin; '
          'alsatplg -d /dest/X1P42100-HP-OMNIBOOK-5-tplg.bin -o /dest/topology-decoded.conf')
shutil.copyfile(a.board,out/'board-2.bin')
shutil.copyfile(source/'LICENSE.BSD-3-Clause',out/'LICENSE.audio')
report={'audio_source':lock,'builder':a.builder,'wireless':meta,
        'files':{name:digest(out/name) for name in ['board-2.bin','X1P42100-HP-OMNIBOOK-5-tplg.bin','LICENSE.audio']},
        'physical_wireless_and_audio_tested':False,'internal_speakers_enabled':False}
(out/'build.json').write_text(json.dumps(report,indent=2)+'\n')
