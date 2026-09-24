# One installer for Snapdragon laptops and headsets

Status: product requirement and proposed architecture. A general installer has not been implemented. A separate [personal offline deployment procedure](PERSONAL-INSTALL.md) is available for the reviewed development machine; physical internal boot is pending.

## User experience

Use one MainFrameOS installation entry point. Detect the connected or booted device, show its compatibility status and known limitations, let the user select storage and installation options, and install the appropriate system configuration. Users should not need to choose a laptop-brand edition or manually assemble drivers.

The product shares an Arch Linux ARM base, package repositories, release channels, application strategy and support policy. Laptop desktop and headset XR sessions select different components from the same maintained system.

## Installation sequence

1. Identify architecture, Snapdragon platform, board/configuration and boot capabilities using an allowlist of non-personal identifiers.
2. Resolve a versioned hardware profile. Match exact identifiers where required; do not select a profile from CPU branding alone.
3. Report supported, experimental or unknown status, required firmware, missing features and recovery prerequisites before changing storage.
4. Select a tested boot/install adapter. A bootable laptop installer and a host-assisted headset installation may use different transports within the same installer framework.
5. Present the actual destination, partition changes and data-preservation choices for confirmation.
6. Verify release signatures and payload hashes, deploy the shared ARM64 system, and select the matching kernel, firmware and configuration packages.
7. Configure the platform's tested boot and recovery path, validate installed artifacts, and record the release/profile manifest.
8. Run first-boot checks and publish a useful compatibility report without collecting personal logs by default.

## Implementation boundaries

The installer core handles UI, planning, verification, deployment records and error handling. Hardware profiles are data describing compatible identities, package sets, firmware requirements, boot adapter and acceptance evidence. Boot adapters implement platform-specific loading, storage and recovery behavior.

Prefer a common kernel and common platform packages. Allow an explicitly maintained kernel track where upstream readiness requires one. Keep device quirks out of global defaults. A new profile should expand the same installer instead of producing a new branded distribution.

One installer experience is not a promise that one USB image can boot every headset. Locked bootloaders, device-specific image formats, unavailable firmware or missing tracking support can prevent installation on individual devices. The installer must explain such limits and stop before destructive operations. Unknown hardware can be inspected through a separate read-only developer workflow; it must not inherit the first laptop's profile.

## Acceptance criteria

- The same installer release handles at least two distinct Snapdragon laptop configurations and selects the correct settings.
- Unknown, ambiguous and unsupported hardware produce clear results without storage writes.
- Profile selection, signature failure, incompatible firmware, interrupted installation and recovery paths have meaningful tests.
- A headset adapter is accepted only after device access, deployment, recovery and XR functionality are physically tested.
- Release support lists identify tested configurations and limitations; chip-level driver announcements alone never mark a profile supported.

The existing support utility provides the first strict identification profile only. It is a starting component, not proof that this installer already exists. See [Roadmap](ROADMAP.md).
