#!/usr/bin/env python3
"""Boot only the generated image in QEMU with temporary disk writes and no network."""
import json
import subprocess
from build import BUILD, OUT, container

state=json.loads((OUT/'usb-image.json').read_text())
image=OUT/state['image']
if image.parent!=OUT or not image.is_file() or image.is_symlink():
    raise SystemExit('Expected a generated regular image file')
command=['podman','run','--rm','--name','mainframeos-usb-smoke','--network=none','--cap-drop=ALL','--security-opt=no-new-privileges',
         '--memory=2g','--cpus=2','--pids-limit=256','-v',f'{OUT}:/artifacts:ro',
         '-v',f'{BUILD / "usb-assembly/esp"}:/bootfiles:ro',
         (BUILD/'usb-tools/image-id').read_text().strip(),
         'qemu-system-aarch64','-machine','virt','-cpu','max','-m','1536','-smp','2',
         '-nographic','-no-reboot','-nic','none',
         '-kernel','/bootfiles/EFI/MainFrameOS/Image','-initrd','/bootfiles/EFI/MainFrameOS/initramfs.img',
         '-append',f'root=UUID={state["root_uuid"]} rw rootwait console=ttyAMA0 mainframeos.smoke=1 systemd.unit=multi-user.target',
         '-drive',f'file=/artifacts/{image.name},format=raw,if=virtio,snapshot=on']
log=BUILD/'usb-smoke.log'
with log.open('w') as stream:
    try:
        result=subprocess.run(command,stdout=stream,stderr=subprocess.STDOUT,timeout=300)
    except subprocess.TimeoutExpired:
        subprocess.run(['podman','stop','--time','2','mainframeos-usb-smoke'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        raise SystemExit('Virtual boot exceeded five minutes; inspect build/usb-smoke.log')
passed=result.returncode==0 and 'MAINFRAMEOS_BOOT_SMOKE_PASS' in log.read_text()
report={'passed':passed,'scope':'QEMU virt kernel, initramfs and root filesystem boot; not laptop hardware or EFI validation',
        'image_sha256':state['sha256'],'physical_boot_tested':False}
(OUT/'usb-smoke.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
if not passed: raise SystemExit('Virtual boot failed; inspect build/usb-smoke.log')
