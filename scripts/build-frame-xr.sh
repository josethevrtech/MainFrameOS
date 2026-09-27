#!/bin/bash
# Native ARM64, existing verified ALARM build root. No package/boot installation.
set -euo pipefail
[[ $# == 3 ]] || { echo 'Usage: build-frame-xr.sh ALARM_ROOT PREPARED_SOURCE NEW_OUTPUT'; exit 2; }
[[ $(uname -m) == aarch64 && $(id -u) != 0 ]] || { echo 'Use a normal ARM64 user'; exit 1; }
recipe=$(cd -- "$(dirname -- "$0")/.." && pwd)
root=$(realpath -- "$1")
source=$(realpath -- "$2")
dest=$(realpath -m -- "$3")
[[ ! -e "$dest" && ! -L "$dest" ]] || { echo 'Output must not exist'; exit 1; }
case "$dest/" in "$source/"*|"$root/"*) echo 'Output must be outside source and builder root'; exit 1;; esac
python3 "$recipe/scripts/frame_xr.py" verify "$source"
mkdir -p -- "$dest"
# Read-only root/source, no network, no display, no host home, no host boot devices.
# Build resources are bounded by the user service manager without affecting the desktop.
systemd-run --user --quiet --wait --pipe --collect \
 -p MemoryMax=3G -p CPUQuota=200% -p TasksMax=256 \
 bwrap --die-with-parent --new-session --unshare-all \
 --ro-bind "$root" / --ro-bind "$source" /mnt --bind "$dest" /opt \
 --proc /proc --dev /dev --tmpfs /tmp --tmpfs /run --clearenv \
 --setenv HOME /tmp --setenv PATH /usr/bin --setenv LANG C.UTF-8 \
 --setenv SOURCE_DATE_EPOCH 1790380800 --chdir /opt \
 /bin/bash -euo pipefail -c '
 grep -qx "ID=archarm" /etc/os-release
 pacman -Q > /opt/builder-packages.txt
 cmake --version > /opt/toolchain.txt
 cc --version >> /opt/toolchain.txt
 cmake -G Ninja -S /mnt -B /opt/obj -DCMAKE_BUILD_TYPE=Release \
   -DCMAKE_INSTALL_PREFIX=/usr -DBUILD_TESTING=OFF \
   -DXRT_FEATURE_STEAMVR_PLUGIN=OFF -DXRT_BUILD_DRIVER_STEAMVR_LIGHTHOUSE=OFF \
   -DXRT_FEATURE_OPENVR=OFF
 cmake --build /opt/obj -j2
 DESTDIR=/opt/stage cmake --install /opt/obj
 '
python3 "$recipe/scripts/frame_xr.py" verify "$source"
python3 - "$source" "$dest" "$recipe/scripts/build-frame-xr.sh" <<'PY'
import hashlib,json,sys
from pathlib import Path
source,dest,script=map(Path,sys.argv[1:])
sha=lambda p: hashlib.sha256(p.read_bytes()).hexdigest()
record=json.loads((source/'.mainframeos-source.json').read_text())
files={str(p.relative_to(dest)):sha(p) for p in sorted((dest/'stage').rglob('*')) if p.is_file()}
if not files: raise SystemExit('No staged artifacts')
report={'schema_version':1,'source_lock_sha256':record['lock_sha256'],'source_commit':record['commit'],
        'artifacts':files,'build_script_sha256':sha(script),'cmake_cache_sha256':sha(dest/'obj/CMakeCache.txt'),
        'builder_packages_sha256':sha(dest/'builder-packages.txt'),
        'scope':'Clean isolated build in recorded ALARM environment; not a complete reproducible OS',
        'hardware_validated':False,'bootable_image':False,'release_signed':False}
(dest/'build.json').write_text(json.dumps(report,indent=2)+'\n')
print('Built staged Frame XR artifacts; no host installation or runtime switch')
PY
