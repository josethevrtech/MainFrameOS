# Personal internal installation

Status: an offline deployment procedure for the reviewed development machine. This is not the shared installer and does not certify another machine. The owner has authorized a 150 GiB MainFrameOS partition alongside the existing installation. Physical internal boot remains pending.

The prepared USB contains a private `plan.json`, a compressed snapshot of its working ALARM based system, and the installation script under `/opt/mainframeos-install`. The plan fixes the disk identity, hardware identity, original GPT, filesystem identities, payload checksum and existing EFI file checksums. It is deliberately excluded from Git along with device firmware, credentials and installation logs.

## Run the prepared installation

Back up irreplaceable personal files to another drive. Keep external power connected. Boot the prepared MainFrameOS USB, open Konsole and run:

```sh
sudo mainframeos-install
```

The command runs the already reviewed plan without another approval prompt. It refuses to run from the internal operating system, against a mounted destination, with changed disk geometry or identities, without external power, or with a mismatched payload. Do not mount the internal partitions in the file manager before running it. If it stops, retain the error and return for inspection. Do not format partitions or rerun a partial attempt manually.

After the completion message, shut down, remove the USB and select MainFrameOS in the existing GRUB menu. The original operating system remains the default entry. MainFrameOS opens its own submenu and boots the new root filesystem. Both systems need physical boot verification before this installation can be considered successful.

## Storage and boot procedure

The current 2 GiB EFI partition keeps its contents. The existing ext4 partition becomes approximately 801.9 GiB. A new 150 GiB ext4 partition receives MainFrameOS with a unique filesystem UUID and partition UUID.

The procedure checks the existing filesystem, shrinks it before changing its partition boundary, verifies that it fits, then writes and verifies the reviewed GPT. It expands the filesystem to fill its smaller partition and checks it again. Existing partition starts and identities are preserved. This follows the [filesystem resize ordering](https://man7.org/linux/man-pages/man8/resize2fs.8.html) and uses [sfdisk locking and verification](https://man7.org/linux/man-pages/man8/sfdisk.8.html).

Before storage changes, the procedure saves the GPT sectors, a textual partition table and the existing EFI files on the USB. These are boot and metadata backups, not a backup of personal files. They cannot undo a power interruption during filesystem relocation. Automatic partition table rollback is deliberately absent because a restored boundary can overlap the newly installed filesystem.

Deployment extracts the verified USB snapshot, writes a new fstab, resets the machine identity and copies the verified kernel, initramfs and device tree into `EFI/MainFrameOS-Internal`. Its entry is appended to the active standalone GRUB configuration. The EFI executable, original menu entries, firmware variables and boot order are preserved. The USB boot files use a separate directory and remain available for recovery.

The installation retains the preview account, its password and passwordless administration. Set a personal password after first boot and replace preview account policy before treating this as a secured personal installation. Audio is not yet validated. The kernel remains a development build; automatic synchronization of future kernel updates into the EFI boot directory is not implemented. Keep the USB for recovery when developing updates.

## Verification and failure records

`make check` tests the layout invariants and malformed plan rejection. The optional privileged integration test operates only on a freshly created disposable loop disk:

```sh
sudo python3 tests/integration/personal-install-loop.py
```

It exercises real ext4 shrinking, GPT changes, deployment and GRUB configuration, and verifies existing file preservation and mounted disk refusal. Its fixture bypasses machine specific preflight checks; it does not prove the target's internal boot or replace the actual USB preflight. Run it on a development host with e2fsprogs, util-linux, dosfstools, GNU tar, zstd and GRUB tools available.

The installation writes `install.log`, `in-progress.json` and, only after finishing, `complete.json` beside its private plan. A partial attempt is stopped for inspection instead of automatically formatting or replaying storage operations. Files copied to EFI and filesystem checks must pass before the completion record is written.
