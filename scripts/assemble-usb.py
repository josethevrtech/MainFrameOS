#!/usr/bin/env python3
"""Assemble regular image files only. Never opens a host block device."""
import hashlib
import json
import shutil
import subprocess
import uuid
from pathlib import Path
from build import ROOT, BUILD, OUT, container, digest

work = BUILD / 'usb-assembly'
work.mkdir(exist_ok=True)
rootfs = work / 'rootfs'
if rootfs.exists():
    raise SystemExit('Move build/usb-assembly aside before assembling a fresh image')
rootfs.mkdir()
image_id = (BUILD / 'usb-final/image-id').read_text().strip()
tools_id = (BUILD / 'usb-tools/image-id').read_text().strip()
name = container('create', image_id, capture_output=True).stdout.strip()
try:
    container('export', '-o', str(work / 'rootfs.tar'), name)
finally:
    container('rm', name)
root_uuid, disk_uuid = str(uuid.uuid4()), str(uuid.uuid4())
root_part_uuid = str(uuid.uuid4())
config = f'''set default=0
set timeout=12
terminal_output console
menuentry 'MainFrameOS USB preview' {{
    search --no-floppy --file --set=usb /EFI/MainFrameOS/Image
    linux ($usb)/EFI/MainFrameOS/Image root=UUID={root_uuid} rw rootwait clk_ignore_unused pd_ignore_unused cma=128M efi=noruntime console=tty0 panic=0 loglevel=4
    initrd ($usb)/EFI/MainFrameOS/initramfs.img
    devicetree ($usb)/EFI/MainFrameOS/device.dtb
}}
menuentry 'MainFrameOS USB troubleshooting console' {{
    search --no-floppy --file --set=usb /EFI/MainFrameOS/Image
    linux ($usb)/EFI/MainFrameOS/Image root=UUID={root_uuid} rw rootwait clk_ignore_unused pd_ignore_unused cma=128M efi=noruntime console=tty0 panic=0 loglevel=7 systemd.unit=multi-user.target pcie_aspm=off nvme_core.default_ps_max_latency_us=0
    initrd ($usb)/EFI/MainFrameOS/initramfs.img
    devicetree ($usb)/EFI/MainFrameOS/device.dtb
}}
'''
(work / 'grub.cfg').write_text(config)
(work / 'early.cfg').write_text('set prefix=(memdisk)/boot/grub\nsearch --no-floppy --file --set=usb /EFI/MainFrameOS/grub.cfg\nconfigfile ($usb)/EFI/MainFrameOS/grub.cfg\n')
# 16 GiB disk: 1 GiB ESP, remainder root, with a 1 MiB end gap for backup GPT.
sector = 512
esp_start, esp_size = 2048, 2097152
root_start = esp_start + esp_size
total_sectors = 16 * 1024**3 // sector
root_sectors = total_sectors - root_start - 2048
output = OUT / 'MainFrameOS-0.1-dev-aarch64-usb.img'
if output.exists():
    raise SystemExit('Output already exists; move it aside before a fresh assembly')
common=['run','--rm','--network=none','--cap-drop=ALL','--cap-add=CHOWN','--cap-add=FOWNER','--cap-add=DAC_OVERRIDE','--security-opt=no-new-privileges',
        '-v',f'{work}:/work:rw','-v',f'{OUT}:/out:rw']
# The rootless namespace preserves system ownership without host root or loop mounts.
container(*common, image_id, 'sh','-ec',f'''
tar --numeric-owner -xpf /work/rootfs.tar -C /work/rootfs
printf 'UUID={root_uuid} / ext4 defaults,noatime 0 1\\n' > /work/rootfs/etc/fstab
mkdir -p /work/esp/EFI/BOOT /work/esp/EFI/MainFrameOS
cp /work/rootfs/boot/Image-mainframeos /work/esp/EFI/MainFrameOS/Image
cp /work/rootfs/boot/initramfs-mainframeos.img /work/esp/EFI/MainFrameOS/initramfs.img
cp /work/rootfs/boot/mainframeos.dtb /work/esp/EFI/MainFrameOS/device.dtb
cp /work/grub.cfg /work/esp/EFI/MainFrameOS/grub.cfg
grub-script-check /work/grub.cfg
grub-mkstandalone -O arm64-efi --modules='part_gpt fat ext2 normal configfile search search_fs_file linux' -o /work/esp/EFI/BOOT/BOOTAA64.EFI 'boot/grub/grub.cfg=/work/early.cfg'
''')
container(*common, tools_id, 'sh','-ec',f'''
truncate -s {esp_size*sector} /work/esp.img
mkfs.vfat -F32 -n MAINFRAME /work/esp.img
mcopy -s -i /work/esp.img /work/esp/EFI ::/
truncate -s {root_sectors*sector} /work/root.img
mkfs.ext4 -F -L MainFrameOS -U {root_uuid} -d /work/rootfs /work/root.img
e2fsck -fn /work/root.img
truncate -s {total_sectors*sector} /out/{output.name}
sgdisk -U {disk_uuid} -n 1:{esp_start}:{root_start-1} -t 1:ef00 -c 1:MainFrameOS-EFI -n 2:{root_start}:{root_start+root_sectors-1} -t 2:8300 -u 2:{root_part_uuid} -c 2:MainFrameOS /out/{output.name}
dd if=/work/esp.img of=/out/{output.name} bs=4M oflag=seek_bytes seek={esp_start*sector} conv=notrunc,sparse status=none
dd if=/work/root.img of=/out/{output.name} bs=4M oflag=seek_bytes seek={root_start*sector} conv=notrunc,sparse status=none
sgdisk -v /out/{output.name}
''')
manifest={'schema_version':1,'image':output.name,'sha256':digest(output),'size':output.stat().st_size,
          'root_uuid':root_uuid,'root_partuuid':root_part_uuid,'root_offset':root_start*sector,
          'root_length':root_sectors*sector,'desktop_image':image_id,'tools_image':tools_id,
          'kernel':json.loads((OUT/'usb-kernel/build.json').read_text()),
          'firmware':json.loads((BUILD/'usb-stage/firmware-inputs.json').read_text()),
          'physical_boot_tested':False,'redistributable':False,'scope':'personal USB hardware test; no internal disk installer'}
(OUT/'usb-image.json').write_text(json.dumps(manifest,indent=2)+'\n')
(OUT/(output.name+'.sha256')).write_text(manifest['sha256']+'  '+output.name+'\n')
print(output)
