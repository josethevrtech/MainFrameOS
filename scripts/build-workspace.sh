#!/bin/bash
# Compile the pinned WayVR source/vendor bundle in a separate ALARM build root.
set -euo pipefail
[[ $# == 4 ]] || { echo 'Usage: build-workspace.sh ALARM_ROOT SOURCE_TAR_GZ VENDOR_TAR_XZ NEW_OUTPUT'; exit 2; }
[[ $(uname -m) == aarch64 && $(id -u) != 0 ]] || exit 1
repo=$(cd -- "$(dirname -- "$0")/.." && pwd)
root=$(realpath -- "$1")
source_archive=$(realpath -- "$2")
vendor_archive=$(realpath -- "$3")
out=$(realpath -m -- "$4")
[[ ! -e "$out" && ! -L "$out" ]] || { echo 'Output must be new'; exit 1; }
case "$out/" in "$root/"*) echo 'Output must be outside builder root'; exit 1;; esac
python3 - "$repo" "$source_archive" "$vendor_archive" "$out" <<'PY'
import hashlib,json,shutil,subprocess,sys,tarfile
from pathlib import Path
repo,source,vendor,out=map(Path,sys.argv[1:])
lock=json.loads((repo/'upstream/workspace.lock.json').read_text())
for archive,expected in [(source,lock['source_archive_sha256']),(vendor,lock['vendor_archive']['sha256'])]:
 with archive.open('rb') as f:
  if hashlib.file_digest(f,'sha256').hexdigest()!=expected:raise SystemExit('Source archive hash mismatch')
(out/'source').mkdir(parents=True)
for archive in (source,vendor):
 with tarfile.open(archive) as tf:tf.extractall(out/'source',filter='data')
if hashlib.sha256((out/'source/Cargo.lock').read_bytes()).hexdigest()!=lock['cargo_lock_sha256']:
 raise SystemExit('Cargo lock mismatch')
(out/'source/.cargo').mkdir(exist_ok=True)
shutil.copyfile(out/'source/vendor/vendor-config.toml',out/'source/.cargo/config.toml')
# Keep the verified vendor source unchanged; patch explicit local dependencies.
for crate in ('vulkano','vulkano-macros'):
 shutil.copytree(out/'source/vendor'/crate,out/'source/mainframe-patches'/crate)
for entry in lock['patches']:
 patch=repo/entry['path']
 if hashlib.sha256(patch.read_bytes()).hexdigest()!=entry['sha256']:
  raise SystemExit('Workspace patch hash mismatch')
 subprocess.run(['patch','--batch','--fuzz=0','-p1','-i',str(patch.resolve())],cwd=out/'source',check=True)
if hashlib.sha256((out/'source/Cargo.lock').read_bytes()).hexdigest()!=lock['patched_cargo_lock_sha256']:
 raise SystemExit('Patched Cargo lock mismatch')
(out/'source-lock.json').write_text(json.dumps(lock,indent=2)+'\n')
PY
systemd-run --user --wait --pipe --collect --quiet -p MemoryMax=3G -p CPUQuota=200% -p TasksMax=256 \
 bwrap --die-with-parent --new-session --unshare-all --ro-bind "$root" / \
 --bind "$out" /mnt --proc /proc --dev /dev --tmpfs /tmp --tmpfs /run --clearenv \
 --setenv PATH /usr/bin --setenv HOME /tmp --setenv LANG C.UTF-8 \
 --setenv CARGO_HOME /mnt/cargo --setenv CARGO_TARGET_DIR /mnt/target --chdir /mnt/source \
 /bin/bash -euo pipefail -c '
 grep -qx "ID=archarm" /etc/os-release
 pacman -Q > /mnt/builder-packages.txt
 rustc --version > /mnt/toolchain.txt
 cargo --version >> /mnt/toolchain.txt
 cargo build --frozen --profile plain -j2 -p wayvr --no-default-features --features openxr,wayland,x11
 cargo build --frozen --profile plain -j2 -p wayvrctl
 '
sha256sum "$out/target/plain/wayvr" "$out/target/plain/wayvrctl" > "$out/artifacts.sha256"
