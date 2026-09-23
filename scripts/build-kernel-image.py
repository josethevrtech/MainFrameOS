#!/usr/bin/env python3
"""Build a development kernel, modules and DTB without installing on the host."""
import json
import shutil
import re
from pathlib import Path
from build import ROOT, BUILD, OUT, LOCK, container, digest, validate_builder
from usb_support import cache_inputs, verify_cache

lock = json.loads(LOCK.read_text())
source = BUILD / 'kernel-candidate' / ('linux_ms_dev_kit-' + lock['kernel_candidate']['commit'])
if not source.is_dir():
    raise SystemExit('Run make kernel-dtb to prepare the verified source first')
archive = BUILD / 'downloads' / lock['kernel_candidate']['filename']
if digest(archive) != lock['kernel_candidate']['sha256']:
    raise SystemExit('Kernel source archive does not match its lock')
base = validate_builder(lock)
expected = cache_inputs(ROOT/'images/usb/Tools.Containerfile',lock['bootstrap']['sha256'],base['image'])
image = verify_cache(BUILD/'usb-tools',expected)['image']
obj, dest = BUILD / 'usb-kernel', OUT / 'usb-kernel'
obj.mkdir(exist_ok=True)
dest.mkdir(exist_ok=True)
# Use the pinned source's upstream ARM64 defconfig plus explicit preview features.
common = ['run', '--rm', '--network=none', '--userns=keep-id:uid=1000,gid=1000',
          '--user', '1000:1000', '--cap-drop=ALL', '--security-opt=no-new-privileges',
          '--memory=3g', '--cpus=4', '--pids-limit=256',
          '-e', 'KBUILD_BUILD_USER=mainframeos', '-e', 'KBUILD_BUILD_HOST=builder',
          '-e', 'KBUILD_BUILD_TIMESTAMP=2026-09-23 00:00:00 UTC',
          '-v', f'{source}:/src:ro', '-v', f'{obj}:/obj:rw', '-v', f'{dest}:/dest:rw', '-w', '/src', image]
container(*common, 'make', 'O=/obj', 'ARCH=arm64', 'defconfig')
config = (obj / '.config').read_text()
for line in (ROOT / 'images/usb/kernel.fragment').read_text().splitlines():
    match = re.match(r'(?:# )?(CONFIG_[A-Z0-9_]+)(?:=| is not set)', line)
    if match:
        key = match.group(1)
        config = re.sub(r'^(?:' + key + r'=.*|# ' + key + r' is not set)\n', '', config, flags=re.M)
        config += line + '\n'
(obj / '.config').write_text(config)
container(*common, 'sh', '-ec', '''
make O=/obj ARCH=arm64 olddefconfig
make -j4 O=/obj ARCH=arm64 Image modules qcom/x1p42100-hp-omnibook-5.dtb
make O=/obj ARCH=arm64 INSTALL_MOD_PATH=/dest INSTALL_MOD_STRIP=1 modules_install
cp /obj/arch/arm64/boot/Image /dest/Image
cp /obj/arch/arm64/boot/dts/qcom/x1p42100-hp-omnibook-5.dtb /dest/device.dtb
cp /obj/.config /dest/kernel.config
make -s O=/obj ARCH=arm64 kernelrelease > /dest/kernelrelease
''')
report = {'source': lock['kernel_candidate'], 'builder': image,
          'configuration': 'ARM64 defconfig with preview feature overrides; not the installed kernel configuration',
          'kernelrelease': (dest / 'kernelrelease').read_text().strip(),
          'files': {str(p.relative_to(dest)): digest(p) for p in sorted(dest.rglob('*')) if p.is_file() and p.name != 'build.json'},
          'hardware_boot_tested': False}
(dest / 'build.json').write_text(json.dumps(report, indent=2) + '\n')
