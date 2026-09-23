#!/usr/bin/env python3
"""Build a personal USB preview image. This command never writes a physical drive."""
import argparse
import json
import os
import platform
import shutil
import subprocess
import sys
from pathlib import Path
from build import ROOT, BUILD, OUT, LOCK, container, digest, verify_bootstrap, validate_builder
from usb_support import cache_inputs, verify_cache, verify_firmware_provenance

p=argparse.ArgumentParser(description=__doc__)
p.add_argument('--firmware-directory', type=Path, required=True,
               help='Personally provisioned firmware directory for the initial test profile')
p.add_argument('--firmware-provenance', type=Path, required=True, help='Origin, revision, license status and exact file hashes')
a=p.parse_args()
provenance=json.loads(a.firmware_provenance.read_text())
firmware_files={str(f.relative_to(a.firmware_directory)):digest(f) for f in sorted(a.firmware_directory.rglob('*')) if f.is_file()}
verify_firmware_provenance(provenance,firmware_files)
if os.geteuid()==0 or platform.machine()!='aarch64':
    p.error('Use native AArch64 as a normal user with rootless Podman')
if container('info','--format','{{.Host.Security.Rootless}}',capture_output=True).stdout.strip()!='true':
    p.error('Rootless Podman is required')
required=('qcadsp8380.mbn','adsp_dtbs.elf','qcdxkmsucpurwa.mbn')
if any(not (a.firmware_directory / name).is_file() for name in required):
    p.error('Missing required test platform firmware')
lock=json.loads(LOCK.read_text())
archive=verify_bootstrap(lock)
state=validate_builder(lock)
for name,base in [('tools',state['image']),('desktop',None)]:
    state_dir=BUILD/('usb-'+name);state_dir.mkdir(exist_ok=True)
    recipe = ROOT/f'images/usb/{name.title()}.Containerfile'
    expected=cache_inputs(recipe,lock['bootstrap']['sha256'],base or 'alarm-archive:'+lock['bootstrap']['sha256'])
    if (state_dir/'image-id').exists():
        verify_cache(state_dir,expected)
        continue
    if base is None:
        base=container('import','--arch','arm64','--os','linux',str(archive),capture_output=True).stdout.strip()
    container('build','--build-arg',f'BASE={base}','--iidfile',str(state_dir/'image-id'),
              '-f',str(ROOT/f'images/usb/{name.title()}.Containerfile'),str(ROOT/'images/usb'))
    (state_dir/'inputs.json').write_text(json.dumps({'inputs':expected,'base_image':base,'image':(state_dir/'image-id').read_text().strip()},indent=2)+'\n')
subprocess.run([sys.executable,str(ROOT/'scripts/build-kernel-image.py')],check=True)
stage=BUILD/'usb-stage'
if stage.exists():
    p.error('Move the previous build/usb-stage aside before a fresh staged build')
stage.mkdir()
shutil.copytree(OUT/'usb-kernel',stage/'kernel',symlinks=True)
# Kernel build links point into a disposable builder and have no place in the image.
for name in ('build','source'):
    for link in (stage/'kernel/lib/modules').glob('*/'+name):
        if link.is_symlink(): link.unlink()
shutil.copytree(a.firmware_directory,stage/'firmware',symlinks=False)
firmware=dict(provenance)
verify_firmware_provenance(firmware,{str(f.relative_to(stage/'firmware')):digest(f) for f in sorted((stage/'firmware').rglob('*')) if f.is_file()})
(stage/'firmware-inputs.json').write_text(json.dumps(firmware,indent=2)+'\n')
shutil.copytree(ROOT/'images/usb/overlay',stage/'overlay')
shutil.copyfile(ROOT/'images/usb/mkinitcpio.conf',stage/'mkinitcpio.conf')
shutil.copyfile(OUT/'mainframeos-support-0.1.0-1-any.pkg.tar.xz',stage/'support.pkg.tar.xz')
final=BUILD/'usb-final';final.mkdir(exist_ok=True)
container('build','--build-arg','BASE='+(BUILD/'usb-desktop/image-id').read_text().strip(),
          '--iidfile',str(final/'image-id'),'-f',str(ROOT/'images/usb/Final.Containerfile'),str(stage))
subprocess.run([sys.executable,str(ROOT/'scripts/assemble-usb.py')],check=True)
