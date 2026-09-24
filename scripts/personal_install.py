#!/usr/bin/env python3
"""Offline deployment of one reviewed personal USB preview. Not a general installer."""
import argparse
import copy
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import uuid

GIB = 1024 ** 3
LINUX = '0FC63DAF-8483-4772-8E79-3D69D8477DE4'
ESP = 'C12A7328-F81F-11D2-BA4B-00A0C93EC93B'
BOOT_DIR = 'EFI/MainFrameOS-Internal'
MENU_MARKER = '# MainFrameOS personal installation'


def require(ok, message):
    if not ok:
        raise RuntimeError(message)


def run(*args, input=None, accepted=(0,)):
    result = subprocess.run(args, input=input, text=True, stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT, env={**os.environ, 'LC_ALL': 'C'})
    if result.returncode not in accepted:
        raise RuntimeError(f'{args[0]} failed ({result.returncode}): {result.stdout}')
    return result.stdout.strip()


def sha(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def table(disk):
    return json.loads(run('sfdisk', '--json', disk))['partitiontable']


def normalized(value):
    value = copy.deepcopy(value)
    value.pop('device', None)
    value['id'] = value['id'].lower()
    for part in value['partitions']:
        part.pop('node', None)
        part['uuid'] = part['uuid'].lower()
        part['type'] = part['type'].lower()
    return value


def layout(original, allocation, new_part_uuid):
    require(original['label'] == 'gpt' and original['sectorsize'] == 512,
            'Only the reviewed GPT with 512 byte sectors is supported')
    parts = original['partitions']
    require(len(parts) == 2 and parts[0]['type'].upper() == ESP and
            parts[1]['type'].upper() == LINUX, 'Unexpected partition layout')
    require(parts[0]['start'] + parts[0]['size'] <= parts[1]['start'], 'Overlapping partitions')
    require(parts[1]['start'] + parts[1]['size'] <= original['lastlba'] + 1,
            'Partition extends beyond GPT usable space')
    require(all(set(p) <= {'node', 'start', 'size', 'type', 'uuid', 'name'} for p in parts),
            'Partition attributes require a separate review')
    require(all(re.fullmatch(r'[A-Za-z0-9 _]+', p.get('name', '')) for p in parts),
            'Unexpected partition label')
    require(all(str(uuid.UUID(p['uuid'])) for p in parts), 'Invalid partition UUID')
    uuid.UUID(new_part_uuid)
    require(new_part_uuid.lower() not in {p['uuid'].lower() for p in parts}, 'Partition UUID is already used')
    require(allocation >= 1024**2 and allocation % (1024**2) == 0, 'Allocation must use whole MiB')
    sectors = allocation // 512
    require(parts[1]['size'] > sectors + 1024**2 // 512, 'Insufficient space')
    updated = copy.deepcopy(original)
    updated['partitions'][1]['size'] -= sectors
    start = parts[1]['start'] + updated['partitions'][1]['size']
    require(start % 2048 == 0, 'New partition is not MiB aligned')
    updated['partitions'].append(dict(start=start, size=sectors, type=LINUX,
                                      uuid=new_part_uuid, name='MainFrameOS'))
    return updated


def table_text(value):
    lines = ['label: gpt', 'label-id: ' + value['id'], 'unit: sectors',
             'first-lba: ' + str(value['firstlba']), 'last-lba: ' + str(value['lastlba'])]
    for p in value['partitions']:
        lines.append(f'start={p["start"]}, size={p["size"]}, type={p["type"]}, uuid={p["uuid"]}, name="{p.get("name", "")}"')
    return '\n'.join(lines) + '\n'


def uuid_device(identifier):
    return str((Path('/dev/disk/by-partuuid') / identifier.lower()).resolve(strict=True))


def assert_unmounted(disk):
    entries = json.loads(run('lsblk', '--json', '--paths', '-o', 'NAME,MOUNTPOINTS', disk))['blockdevices']
    def visit(entry):
        require(not any(entry.get('mountpoints') or []), f'{entry["name"]} is mounted; boot the USB first')
        holders = Path('/sys/class/block') / Path(entry['name']).name / 'holders'
        require(not holders.exists() or not list(holders.iterdir()), 'Device has active holders')
        for child in entry.get('children', []):
            visit(child)
    for entry in entries:
        visit(entry)
    swaps = run('swapon', '--noheadings', '--raw', '--show=NAME').splitlines()
    require(not any(str(Path(s).resolve()).startswith(disk) for s in swaps), 'Disk is used for swap')


def fs_bytes(device):
    info = run('dumpe2fs', '-h', device)
    count = int(re.search(r'^Block count:\s+(\d+)$', info, re.M)[1])
    size = int(re.search(r'^Block size:\s+(\d+)$', info, re.M)[1])
    free = int(re.search(r'^Free blocks:\s+(\d+)$', info, re.M)[1])
    return count * size, (count - free) * size, size


def check_fs(device):
    print(f'Checking filesystem on {device}', flush=True)
    print(run('e2fsck', '-f', '-p', device, accepted=(0, 1)), flush=True)


def shrink_and_partition(disk, original, proposed, safety_margin=GIB):
    """Filesystem first, then partition table. Called only after all preflight checks."""
    assert_unmounted(disk)
    require(normalized(table(disk)) == normalized(original), 'Disk layout changed before shrink')
    old = uuid_device(original['partitions'][1]['uuid'])
    check_fs(old)
    target_bytes = proposed['partitions'][1]['size'] * 512
    _, used, block_size = fs_bytes(old)
    require(used + safety_margin < target_bytes - safety_margin, 'Insufficient filesystem free space')
    print('Shrinking the existing filesystem. Keep external power connected.', flush=True)
    print(run('resize2fs', old, str((target_bytes - safety_margin) // block_size)), flush=True)
    check_fs(old)
    require(fs_bytes(old)[0] <= target_bytes, 'Filesystem is still larger than proposed partition')
    assert_unmounted(disk)
    run('sfdisk', '--lock=yes', '--wipe=never', '--wipe-partitions=never', disk,
        input=table_text(proposed))
    run('udevadm', 'settle')
    require(normalized(table(disk)) == normalized(proposed), 'Written GPT differs from the plan')
    require(int(run('blockdev', '--getsize64', old)) == target_bytes, 'Kernel has stale partition size')
    run('sfdisk', '--verify', disk)
    print(run('resize2fs', old), flush=True)
    check_fs(old)


def menu(esp_uuid, root_uuid):
    require(re.fullmatch(r'[A-Fa-f0-9]{4}-[A-Fa-f0-9]{4}', esp_uuid), 'Invalid ESP UUID')
    uuid.UUID(root_uuid)
    entry = f'''{MENU_MARKER}
menuentry 'MainFrameOS' {{
    search --no-floppy --fs-uuid --set=mainframe_esp {esp_uuid}
    configfile ($mainframe_esp)/{BOOT_DIR}/grub.cfg
}}
'''
    config = f'''set default=0
set timeout=8
terminal_output console
menuentry 'MainFrameOS internal installation' {{
    search --no-floppy --fs-uuid --set=mainframe_esp {esp_uuid}
    linux ($mainframe_esp)/{BOOT_DIR}/Image root=UUID={root_uuid} rw rootwait clk_ignore_unused pd_ignore_unused cma=128M efi=noruntime console=tty0 panic=0 loglevel=4
    initrd ($mainframe_esp)/{BOOT_DIR}/initramfs.img
    devicetree ($mainframe_esp)/{BOOT_DIR}/device.dtb
}}
'''
    return entry, config


def atomic_text(path, text):
    path = Path(path)
    temp = path.with_name(path.name + '.mainframeos-tmp')
    with temp.open('w') as stream:
        stream.write(text)
        stream.flush()
        os.fsync(stream.fileno())
    os.replace(temp, path)


def preflight(plan, directory):
    require(os.geteuid() == 0, 'Run using sudo')
    require(plan['schema_version'] == 1 and plan['allocation_bytes'] == 150 * GIB,
            'Only the reviewed 150 GiB personal plan is supported')
    for name in ('sfdisk', 'blockdev', 'e2fsck', 'resize2fs', 'dumpe2fs', 'mkfs.ext4',
                 'tar', 'zstd', 'udevadm', 'grub-script-check', 'lsblk', 'mount', 'umount'):
        require(shutil.which(name), 'Missing tool: ' + name)
    require(run('findmnt', '-n', '-o', 'UUID', '/') == plan['usb_root_uuid'],
            'Boot the prepared MainFrameOS USB before running the installation')
    require(run('findmnt', '-n', '-o', 'UUID', '--target', str(directory)) == plan['usb_root_uuid'],
            'Installation files and backups must stay on the USB')
    for name, value in plan['hardware'].items():
        require((Path('/sys/class/dmi/id') / name).read_text().strip() == value,
                'This plan does not match this machine')
    disk = str(Path(plan['disk_by_id']).resolve(strict=True))
    require(int(run('blockdev', '--getsize64', disk)) == plan['disk_bytes'], 'Disk size differs')
    require(int(run('blockdev', '--getss', disk)) == 512, 'Sector size differs')
    assert_unmounted(disk)
    require(normalized(table(disk)) == normalized(plan['original_table']), 'Disk layout differs from reviewed plan')
    require(run('blkid', '-s', 'UUID', '-o', 'value', uuid_device(plan['original_table']['partitions'][1]['uuid'])) == plan['old_root_uuid'], 'Existing root UUID differs')
    require(run('blkid', '-s', 'TYPE', '-o', 'value', uuid_device(plan['original_table']['partitions'][1]['uuid'])) == 'ext4', 'Existing root is not ext4')
    require(shutil.disk_usage(directory).free > GIB, 'At least 1 GiB free USB space is required for backups')
    require(not (directory / 'in-progress.json').exists(), 'A previous attempt needs inspection. Do not repeat automatically.')
    require(not (directory / 'complete.json').exists(), 'This installation already completed')
    print('Verifying installation payload...', flush=True)
    require(sha(directory / 'rootfs.tar.zst') == plan['payload_sha256'], 'Payload checksum differs')
    run('zstd', '-t', str(directory / 'rootfs.tar.zst'))
    proposed = layout(plan['original_table'], plan['allocation_bytes'], plan['new_part_uuid'])
    run('sfdisk', '--no-act', '--wipe=never', '--wipe-partitions=never', disk, input=table_text(proposed))
    require(any((p / 'type').exists() and (p / 'type').read_text().strip() in ('Mains', 'USB') and (p / 'online').exists() and
                (p / 'online').read_text().strip() == '1' for p in Path('/sys/class/power_supply').iterdir()),
            'Connect external power before installation')
    return disk, proposed


def install(plan, directory, apply):
    disk, proposed = preflight(plan, directory)
    esp_device = uuid_device(plan['original_table']['partitions'][0]['uuid'])
    with tempfile.TemporaryDirectory(prefix='mainframeos-install-', dir='/run') as work:
        esp = Path(work) / 'efi'; esp.mkdir()
        run('mount', '-o', 'ro', esp_device, str(esp))
        try:
            require(run('blkid', '-s', 'UUID', '-o', 'value', esp_device) == plan['esp_uuid'], 'ESP UUID differs')
            require(not (esp / BOOT_DIR).exists(), 'MainFrameOS boot directory already exists')
            for path, expected in plan['esp_checksums'].items():
                require(sha(esp / path) == expected, 'Existing boot file changed: ' + path)
            require(shutil.disk_usage(esp).free > plan['boot_bytes'] + 128 * 1024**2, 'Insufficient EFI space')
            old_menu = (esp / plan['grub_config']).read_text()
            require(MENU_MARKER not in old_menu, 'MainFrameOS entry already exists')
            entry, config = menu(plan['esp_uuid'], plan['new_root_uuid'])
            candidate = Path(work) / 'grub.cfg'; candidate.write_text(old_menu + '\n' + entry)
            run('grub-script-check', str(candidate))
            candidate.write_text(config); run('grub-script-check', str(candidate))
            if not apply:
                print('Preflight passed. No internal disk changes made.'); return
            backups = directory / 'backup'; backups.mkdir(mode=0o700, exist_ok=False)
            (backups / 'partition-table.sfdisk').write_text(run('sfdisk', '--dump', disk) + '\n')
            run('sfdisk', '--backup-pt-sectors', '--backup-file', str(backups / 'gpt'), disk)
            run('tar', '-cpf', str(backups / 'efi.tar'), '-C', str(esp), '.')
            shutil.copyfile(directory / 'plan.json', backups / 'plan.json')
            run('sync', '-f', str(directory))
        finally:
            run('umount', str(esp))
        atomic_text(directory / 'in-progress.json', json.dumps({'stage': 'shrink', 'disk': disk}))
        shrink_and_partition(disk, plan['original_table'], proposed)
        new_device = uuid_device(plan['new_part_uuid'])
        require(int(run('blockdev', '--getsize64', new_device)) == plan['allocation_bytes'], 'New partition size differs')
        require(not run('blkid', '-p', '-s', 'TYPE', '-o', 'value', new_device, accepted=(0, 2)), 'New partition contains a filesystem signature; stop for inspection')
        atomic_text(directory / 'in-progress.json', json.dumps({'stage': 'deploy', 'disk': disk}))
        run('mkfs.ext4', '-U', plan['new_root_uuid'], '-L', 'MainFrameOS', new_device)
        dest = Path(work) / 'root'; dest.mkdir()
        run('mount', new_device, str(dest))
        try:
            print('Installing the verified MainFrameOS system...', flush=True)
            run('tar', '--numeric-owner', '--acls', '--xattrs', '-I', 'zstd', '-xpf',
                str(directory / 'rootfs.tar.zst'), '-C', str(dest))
            for path, expected in plan['boot_checksums'].items():
                require(sha(dest / path) == expected, 'Installed boot file checksum differs')
            (dest / 'etc/fstab').write_text(f'UUID={plan["new_root_uuid"]} / ext4 defaults,noatime 0 1\nUUID={plan["esp_uuid"]} /efi vfat defaults,umask=0077,nofail 0 2\n')
            (dest / 'efi').mkdir(exist_ok=True)
            (dest / 'etc/machine-id').write_text('')
            os_release = dest / 'etc/os-release'
            os_release.write_text(os_release.read_text().replace('MainFrameOS USB Development Preview', 'MainFrameOS Development'))
            (dest / 'usr/share/mainframeos/internal-install.json').write_text(json.dumps({
                'root_uuid': plan['new_root_uuid'], 'payload_sha256': plan['payload_sha256'],
                'boot_directory': BOOT_DIR, 'automatic_kernel_boot_sync': False}, indent=2) + '\n')
            run('sync', '-f', str(dest))
        finally:
            run('umount', str(dest))
        check_fs(new_device)
        atomic_text(directory / 'in-progress.json', json.dumps({'stage': 'boot-entry', 'disk': disk}))
        run('mount', '-o', 'ro', new_device, str(dest))
        try:
            run('mount', esp_device, str(esp))
            try:
                for path, expected in plan['esp_checksums'].items():
                    require(sha(esp / path) == expected, 'Existing boot file changed before deployment')
                boot = esp / BOOT_DIR; boot.mkdir()
                for source, name in [('boot/Image-mainframeos', 'Image'),
                                     ('boot/initramfs-mainframeos.img', 'initramfs.img'),
                                     ('boot/mainframeos.dtb', 'device.dtb')]:
                    shutil.copyfile(dest / source, boot / name)
                    require(sha(boot / name) == plan['boot_checksums'][source], 'EFI file copy failed')
                atomic_text(boot / 'grub.cfg', config)
                run('grub-script-check', str(boot / 'grub.cfg'))
                run('sync', '-f', str(esp))
                atomic_text(esp / plan['grub_config'], old_menu + '\n' + entry)
                run('grub-script-check', str(esp / plan['grub_config']))
                require(sha(esp / 'EFI/BOOT/BOOTAA64.EFI') == plan['esp_checksums']['EFI/BOOT/BOOTAA64.EFI'], 'Existing EFI loader changed')
                run('sync', '-f', str(esp))
            finally:
                run('umount', str(esp))
        finally:
            run('umount', str(dest))
        atomic_text(directory / 'complete.json', json.dumps({'root_uuid': plan['new_root_uuid'],
                    'physical_boot_pending': True, 'allocation_bytes': plan['allocation_bytes']}, indent=2))
        (directory / 'in-progress.json').unlink()
        run('sync', '-f', str(directory))
        print('Installation completed. Shut down, remove the USB, then select MainFrameOS in GRUB.')
        print('The existing system remains the default. MainFrameOS still uses the preview account.')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--plan', type=Path, required=True)
    parser.add_argument('--apply', action='store_true', help='Apply the reviewed installation plan')
    args = parser.parse_args()
    directory = args.plan.resolve().parent
    require(args.plan.name == 'plan.json', 'Expected plan.json')
    try:
        install(json.loads(args.plan.read_text()), directory, args.apply)
    except (RuntimeError, OSError, ValueError) as error:
        sys.exit(f'Stopped: {error}\nDo not manually format or repeat a partial installation. Keep the USB for inspection.')


if __name__ == '__main__':
    main()
