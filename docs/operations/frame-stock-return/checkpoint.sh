#!/bin/bash
set -euo pipefail
[[ $(findmnt -no SOURCE /) == /dev/sda5 ]]
[[ $(sudo -n steamos-bootconf this-image) == B ]]
base=/home/steamos/MainFrameOS/stock-return-20260927
mkdir -m 700 "$base"
sudo -n steamos-bootconf dump-config > "$base/boot-before.txt"
lsblk -o NAME,SIZE,FSTYPE,LABEL,PARTLABEL,PARTUUID,MOUNTPOINTS > "$base/partitions.txt"
cp /proc/cmdline "$base/cmdline-before.txt"
cp /etc/os-release "$base/os-release-before.txt"
sudo -n sfdisk --dump /dev/sda > "$base/sda-partitions.sfdisk"
sudo -n btrfs subvolume snapshot -r / /mainframeos-pre-stock-20260927
sudo -n btrfs send /mainframeos-pre-stock-20260927 | zstd -T2 -3 -o "$base/root-B.btrfs.zst"
zstd -t "$base/root-B.btrfs.zst"
zstd -dc "$base/root-B.btrfs.zst" | sudo -n btrfs receive --dump > /dev/null
sudo -n dd if=/dev/disk/by-partsets/B/efi bs=4M status=none | zstd -T2 -3 -o "$base/efi-B.img.zst"
# Shared user settings are private; preserve without publishing their contents.
tar --xattrs --acls -C /home/steamos -cpf - .config .bashrc .bash_profile .local/share/applications | zstd -T2 -3 -o "$base/shared-settings.tar.zst"
sha256sum "$base"/*.zst > "$base/SHA256SUMS"
echo "$base"
