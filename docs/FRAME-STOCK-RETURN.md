# Frame development checkpoint and return to stock — 2026-09-27

The owner requested a temporary return to the stock SteamOS slot after the
COSMIC/Monado wearer test failed stereo alignment and apparent screen size.
**Stock slot A boot succeeded**: `/dev/sda4`, `rauc.slot=A`, SteamOS 0.5.0
build 20260925.6142658. SSH, sudo, SteamVR and gamescope-session are working.
All five private archive copies on the PC matched their device SHA256 hashes.
Development is paused, not discarded. This record is device-specific; it is
not a generic partition-switching or flashing guide.

## What is preserved

| Work | State at checkpoint |
| --- | --- |
| Original OS recovery | Approximately 28 GiB private PC and dedicated USB backups, with partition/boot/firmware-relevant records and offline non-game home archive. Matching manifests, temporary root-image restores, filesystem checks and USB boot were previously verified. No full destructive reimage-and-boot test was performed. |
| Owner-controlled slot B | Writable root, passwordless sudo, disabled vendor updater services, username `josethevrtech`, hostname `SteamFrameJS`; home path remains `/home/steamos`. Saved root snapshot/send stream plus var overlay and EFI partition. |
| Desktop work | Plasma compatibility baseline, original terminal/settings integration and fastfetch; separate ALARM COSMIC 1.9.0 lab, application bridge and launch/default scripts. Both lab environments are retained. |
| Ultrawide desktop | User-confirmed curved 3840×1440 COSMIC workspace on the existing SteamVR/Gamescope recovery runtime; custom Gamescope upload-buffer change and rollback scripts retained. This is distinct from the small experimental Monado desktop. |
| Independent recording | Linux KMS recorder source/binary, optical mapping, GUI, native player integration and scripts retained privately. It does not depend on the Steam recording API. Personal recordings are not published. |
| Monado/OpenXR | Pinned source, patches, isolated build recipe and evidence in this PR and its base PR #19. Tabletop upright images and ~88.49 presentation returns/s do not override the failed wearer test. |
| Kernel direction | Planned `-mainframeos-regulator1` suffix and captured stock reference/configuration. Matching complete vendor kernel source is not available to the build; no new kernel has been compiled or installed. |

The full device-local `MainFrameOS` development directory is archived, including
sources, build artifacts, isolated roots and scripts. The checkpoint directory
itself is excluded to avoid recursion. Runtime Unix sockets are intentionally
not archived; services recreate them. Private archives also contain vendor
references and potentially credentials: they must not be committed to Git.
Source recipes already integrated into the repository remain publicly reviewable;
device-local prototypes are preserved privately and are not yet all packaged as
reproducible distribution components.

## Checkpoint layout and validation

Device directory: `/home/steamos/MainFrameOS/stock-return-20260927`.
PC directory: the task's `outputs/stock-return/stock-return-20260927`.

- `root-B.btrfs.zst`: read-only Btrfs snapshot sent from development root B.
- `var-B.tar.zst`: numeric-owner, ACL/xattr-preserving archive of B's var filesystem,
  including the **etc overlay**. Root alone does not contain the active `/etc`.
- `efi-B.img.zst`: raw 64 MiB EFI B partition, compressed. The device uses its
  vendor boot-selection mechanism; this file alone is not a bootable recovery disk.
- `development-home.tar.zst`: the complete device-local development tree.
- `shared-settings.tar.zst`: user configuration, shell startup and application entries.
- `sda-partitions.sfdisk`, partition identities, OS/cmdline and pre-switch boot state.
- `saved-overrides/`, `overrides.json`, and `restore-development-overrides.py`:
  exact shared-home changes and hash-checked restoration helper.
- `SHA256SUMS`: private archive checksums; sanitized receipt is linked below.

The root stream passed zstd decoding and `btrfs receive --dump` parsing.
This is not a physical restore test. Archives and copied-file checksums are
verified separately; original stock recovery backups remain the deeper rollback.
A live var/config capture is not an atomic whole-machine snapshot. Development
services were stopped for the development-tree archive. Games are not added to
this checkpoint. Unrelated shared-home data remains in place.

## Slot selection and exact shared-home changes

Verified layout: A = root `/dev/sda4`, var `/dev/sda6`, EFI `/dev/sda2`;
B = root `/dev/sda5`, var `/dev/sda7`, EFI `/dev/sda3`.
Both share `/dev/sda8` as home. Before switching, both slots reported good/valid;
primary was B, firmware slot A. Stock A is SteamOS 0.5.0 build 20260925.6142658.
Its account is `steamos`, with the same UID 1000 and home as development B.

Three user overrides were copied, hash-checked, then removed from their active paths:

1. `.config/systemd/user/steamvr-plasma.service.d/90-mainframeos.conf`
2. `.config/systemd/user/gamescope-session.service.d/90-mainframeos-ultrawide.conf`
3. `.config/autostart/steam.desktop` (the MainFrameOS Steam-autostart suppression)

No development root, partition table or firmware is erased. Shared application
settings and files remain; stock-slot boot is not a factory reset. The stock
updater may eventually reuse B as its inactive update slot, so retained B alone
must not be treated as the backup.

After completing the checkpoint, select stock using the installed vendor helper:

```sh
sudo steamos-bootconf --image A set-mode reboot
sudo steamos-bootconf selected-image  # must print A
sudo systemctl reboot
```

After boot, verify `steamos-bootconf this-image`, `findmnt /`, `/proc/cmdline`
and `/etc/os-release`. Use the stock account `steamos` for SSH. Do not interpret
an unavailable SSH connection as proof of either boot success or failure.

## Resume development while B remains intact

On stock A, as UID 1000, restore the saved three overrides without overwriting
new divergent files. The helper checks every destination before changing any:

```sh
python3 /home/steamos/MainFrameOS/stock-return-20260927/restore-development-overrides.py
sudo steamos-bootconf --image B set-mode reboot
sudo steamos-bootconf selected-image  # must print B
sudo systemctl reboot
```

Do not restart user desktop services on A after restoring the B overrides.
On B the account is again `josethevrtech`; verify root B and normal COSMIC before
resuming experiments. Monado remains a bounded test candidate, not the default.

## Recovery if B is overwritten

First boot the previously tested dedicated recovery USB and verify physical disk
identities against the saved partition record. Keep all internal targets offline.
The original stock backup and its private `RESTORE.md` remain the verified
reference for partition geometry, original root/var images and home restoration.

The new Btrfs send stream must be received into a suitable Btrfs filesystem;
it is **not** a raw image to write with `dd`. Receiving creates a read-only
subvolume. A bootable reconstruction needs a writable root snapshot/default
subvolume matched to the existing boot configuration, restored B var/overlay
and EFI, and the shared development tree/settings. Validate that reconstruction
in a temporary image before any internal partition replacement. No such fresh
checkpoint reconstruction has yet been boot-tested. Do not replay the partition
table or firmware images merely to switch slots.

[Checkpoint verification receipt](evidence/frame-stock-return-2026-09-27.json).

[Latest wearer result](evidence/frame-workspace-wearer-2026-09-27.json).
