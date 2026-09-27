# Executed checkpoint helpers

These are the device-specific helpers used on 2026-09-27, retained for audit.
Do not run them blindly on another device or rerun the checkpoint after it exists.
`checkpoint.sh` captures root/EFI and user settings; it is **not the entire backup**.
The additional development-tree and var archives were captured separately using:

```sh
systemctl --user stop steamvr-plasma.service mainframeos-host-apps.service
sudo tar --one-file-system --xattrs --acls --numeric-owner \
  --exclude=MainFrameOS/stock-return-20260927 -C /home/steamos -cpf - MainFrameOS \
  | zstd -T2 -3 -o /home/steamos/MainFrameOS/stock-return-20260927/development-home.tar.zst
sudo tar --one-file-system --xattrs --acls --numeric-owner -C /var -cpf - . \
  | zstd -T2 -3 -o /home/steamos/MainFrameOS/stock-return-20260927/var-B.tar.zst
```

The executed archive commands skipped Unix sockets, which are recreated at runtime.
Each compressed tar was subsequently decoded and read through to completion.
The root stream was decoded and parsed by `btrfs receive --dump`.
Private copies are checked against the generated SHA256 manifest.

`set-aside.py` saves the exact three overrides in the existing checkpoint before
removing them from shared home. `restore-development-overrides.py` belongs inside
the device checkpoint directory beside `overrides.json` and `saved-overrides/`.
It validates hashes and all destination conflicts before restoring files. It does
not select a slot or reboot. See [the recovery record](../../FRAME-STOCK-RETURN.md).
