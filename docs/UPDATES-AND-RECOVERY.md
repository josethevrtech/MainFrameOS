# Updates and recovery

Status: requirements and proposed design; no updater has been implemented.

## Fresh software with a recoverable system

Track Arch Linux ARM and upstream releases, then promote a coherent tested snapshot. Updating only selected libraries against an older base is not the release strategy. The initial reference port's custom kernel, held packages and manually built components show why MainFrameOS needs an explicit maintenance process.

Proposed channels:

| Channel | Purpose | Promotion condition |
| --- | --- | --- |
| Development | New kernels, Mesa, desktop and packaging work | Build and basic automated checks |
| Testing | Release candidate on named hardware | Boot and core integration checks |
| Stable | Daily-use deployment | Full required hardware/app checks and recovery validation |

Publish actual component versions and known regressions. Accelerate security fixes through focused testing, without inventing a response-time guarantee before maintainers and infrastructure exist.

## Proposed deployment model

Use complete, signed system deployments with a previous known-good boot option. Keep user files persistent and separate from the replaceable base. Flatpaks and compatibility runtimes can have their own versioned update paths, with a documented compatibility boundary.

Evaluate A/B root deployments or another image-based mechanism against the actual firmware/bootloader. Selection is pending. Filesystem snapshots alone do not prove that an unbootable kernel or broken EFI loader can be recovered.

## Required update transaction

1. Verify metadata and artifact authenticity and check device-profile compatibility.
2. Ensure sufficient storage and suitable power conditions.
3. Stage the new root and matching kernel, initramfs, modules and device tree without replacing the active deployment.
4. Set a bounded trial boot and retain a known-good entry.
5. Mark success only after defined boot/session health checks.
6. Return to the prior deployment after failed trials or allow explicit selection from recovery.

The exact boot-counting and fallback mechanism must be proven for each supported boot adapter and hardware configuration. Automatic fallback is a requirement to evaluate and implement, not a current capability.

## Persistent state

Document ownership of `/home`, system configuration, app data and runtime state. Version configuration migrations and define backward compatibility. Rolling back the OS does not automatically roll back application documents or database formats. A backup and a rollback solve different problems.

Do not design a factory reset until its deletion boundaries and recovery behavior are explicit. Firmware updates require their own supported path and must not be implied by successful OS updates.

## Release evidence

Every candidate records sources, package manifest, firmware manifest, hashes/signatures, device profiles, checks performed, known issues and recovery instructions. Validate interrupted download, corrupted artifact, insufficient space, failed boot and manual fallback. Signing keys belong outside the repository.
