import sys, tempfile, subprocess, json, uuid, shutil
from pathlib import Path
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[2]/'scripts'))
import personal_install as m
root=Path(tempfile.mkdtemp(prefix='mainframeos-loop-test-'))
print('Disposable test directory:', root, flush=True)
image=root/'disk.img'
with image.open('wb') as f:f.truncate(4*m.GIB)
disk=m.run('losetup','--find','--show','--partscan',str(image))
assert disk.startswith('/dev/loop')
mount=root/'mount';mount.mkdir(exist_ok=True)
try:
 m.run('sfdisk','--wipe=never',disk,input='label: gpt\nstart=2048,size=524288,type=U,name="Test EFI"\nstart=526336,size=7860224,type=L,name="Existing"\n')
 m.run('udevadm','settle')
 original=m.table(disk);esp=m.uuid_device(original['partitions'][0]['uuid']);old=m.uuid_device(original['partitions'][1]['uuid'])
 m.run('mkfs.vfat','-F','32',esp);m.run('mkfs.ext4','-q',old)
 m.run('mount',old,str(mount))
 (mount/'preserve.txt').write_text('Original installation sentinel\n')
 try:
  m.assert_unmounted(disk)
  raise AssertionError('Mounted device accepted')
 except RuntimeError:pass
 m.run('umount',str(mount))
 m.run('mount',esp,str(mount))
 for name,value in {'EFI/ArchOmniBook/grub.cfg':"set default=0\nmenuentry 'Existing' { echo Existing; }\n",'EFI/BOOT/BOOTAA64.EFI':'existing loader'}.items():
  p=mount/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(value)
 hashes={name:m.sha(mount/name) for name in ('EFI/ArchOmniBook/grub.cfg','EFI/BOOT/BOOTAA64.EFI')}
 m.run('umount',str(mount))
 payload=root/'payload';payload.mkdir()
 for name in ('boot/Image-mainframeos','boot/initramfs-mainframeos.img','boot/mainframeos.dtb','etc/os-release'):
  p=payload/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text('MainFrameOS USB Development Preview\n')
 (payload/'usr/share/mainframeos').mkdir(parents=True)
 m.run('tar','-I','zstd','-cpf',str(root/'rootfs.tar.zst'),'-C',str(payload),'.')
 plan=dict(original_table=original,allocation_bytes=512*1024**2,new_part_uuid=str(uuid.uuid4()),new_root_uuid=str(uuid.uuid4()),esp_uuid=m.run('blkid','-s','UUID','-o','value',esp),esp_checksums=hashes,grub_config='EFI/ArchOmniBook/grub.cfg',boot_bytes=1024,payload_sha256=m.sha(root/'rootfs.tar.zst'),boot_checksums={str(p.relative_to(payload)):m.sha(p) for p in (payload/'boot').iterdir()})
 (root/'plan.json').write_text(json.dumps(plan))
 proposed=m.layout(original,plan['allocation_bytes'],plan['new_part_uuid'])
 with patch.object(m,'preflight',return_value=(disk,proposed)):
  m.install(plan,root,True)
 assert (root/'complete.json').exists()
 assert not (root/'in-progress.json').exists()
 m.run('mount','-o','ro',old,str(mount))
 assert (mount/'preserve.txt').read_text()=='Original installation sentinel\n'
 m.run('umount',str(mount))
 new=m.uuid_device(plan['new_part_uuid'])
 m.run('mount','-o','ro',new,str(mount))
 assert plan['new_root_uuid'] in (mount/'etc/fstab').read_text()
 assert (mount/'etc/machine-id').read_text()==''
 m.run('umount',str(mount))
 m.run('mount','-o','ro',esp,str(mount))
 assert m.sha(mount/'EFI/BOOT/BOOTAA64.EFI')==hashes['EFI/BOOT/BOOTAA64.EFI']
 assert "menuentry 'Existing'" in (mount/plan['grub_config']).read_text()
 assert m.MENU_MARKER in (mount/plan['grub_config']).read_text()
 assert plan['new_root_uuid'] in (mount/m.BOOT_DIR/'grub.cfg').read_text()
 m.run('umount',str(mount))
 print('PASS: mounted disk refused; real shrink, GPT update, deployment, existing file preservation and GRUB append verified on disposable loop disk')
finally:
 subprocess.run(['umount',str(mount)],capture_output=True)
 subprocess.run(['losetup','-d',disk],check=True)
