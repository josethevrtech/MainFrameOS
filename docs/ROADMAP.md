# Roadmap and initial backlog

Milestones are ordered by dependency, not calendar promises. Package-build infrastructure and candidate DTB compilation are now implemented. No bootable-image milestone is complete.

## M0 — Capture the initial test platform

- [x] Define product scope and identify the reference laptop.
- [x] Record a sanitized summary of the existing hardware evidence.
- [ ] Recover exact kernel sources, configuration and patch provenance.
- [ ] Identify active boot artifacts and required firmware with hashes.
- [ ] Inventory custom audio, power and service configuration.
- [ ] Re-run unresolved baseline tests after the final fixes.

**Exit:** another developer can explain how this board boots and which changes its working hardware needs, using recorded sources and configuration.

## M1 — Shared installer and Arch Linux ARM desktop prototype

- [x] Establish an isolated Arch Linux ARM build environment with signed bootstrap and recorded toolchain inventory.
- [ ] Package the board's required kernel, audio, firmware integration and power configuration.
- [ ] Implement the [shared installer design](INSTALLER.md): detection, compatibility report and boot adapters.
- [ ] Assemble a common system payload with versioned configuration profiles.
- [ ] Exercise the installer end to end on the initial test laptop.
- [ ] Boot into accelerated Plasma Wayland.
- [ ] Complete core input, storage, network, audio and display checks.

**Exit:** a repeatable image boots the reference machine and supports basic productivity, with explicit gaps and a recovery method.

## M2 — Application proof

- [ ] Verify representative native/Flatpak productivity workflows.
- [ ] Bring up ARM64 Waydroid and complete an Android workflow.
- [ ] Package and validate Wine/FEX and complete a Windows `.exe` workflow.
- [ ] Record per-app versions, limitations and reproducible results.
- [ ] Validate runtime startup, idle overhead, suspend and file exchange.

**Exit:** meaningful tasks complete in all three requested app categories on the reference image. Failures produce documented compatibility limits.

## M3 — MainFrameOS 0.1 development preview

- [ ] Produce image manifests, checksums and source/patch inventory.
- [ ] Document installation and recovery for the exact board.
- [ ] Run the hardware/productivity test plan.
- [ ] Package branding, desktop defaults and app launch integration.
- [ ] Publish the image only after its support status and known issues are explicit.

**Exit:** an experimental shared-installer preview is available with an explicit list of tested configurations. It is not a promise of broad device support or production reliability.

## M4 — Reliable update foundation

- [ ] Select and implement a deployment/rollback mechanism.
- [ ] Validate boot success detection and fallback behavior.
- [ ] Define persistent configuration and migration policy.
- [ ] Establish signing, testing/stable promotion and security-fix workflow.
- [ ] Pass interrupted/failed-update and regression checks.

**Exit:** repeatable update and recovery evidence supports a daily-use release candidate.

## M5 — Closely related device

- [ ] Select another Snapdragon laptop configuration with a tester and viable upstream support; no brand relationship is required.
- [ ] Add its distinct hardware profile.
- [ ] Re-run complete acceptance checks and publish limitations.

**Exit:** the same installer demonstrably handles two validated configurations and selects their correct profiles.

## Headsets — Shared platform, distinct boot and XR requirements

Headsets are part of the product scope. Develop their boot/recovery adapters and XR session within the same installation framework. Validate graphics, tracking and input on accessible hardware before claiming a supported headset. Laptop-first testing does not require a separate headset distribution.

## First implementation work items

| ID | Work item | Completion evidence |
| --- | --- | --- |
| [MF-001](https://github.com/josethevrtech/MainFrameOS/issues/2) | Reconstruct reference kernel and DTB provenance | Source commit, patch series, config and boot artifact mapping |
| [MF-002](https://github.com/josethevrtech/MainFrameOS/issues/3) | Package detected platform audio integration | Clean package install, outputs/mic and repeated hotplug/suspend tests |
| [MF-003](https://github.com/josethevrtech/MainFrameOS/issues/4) | Package power and platform services | Service ownership, profile behavior, charge limit and energy measurements |
| [MF-004](https://github.com/josethevrtech/MainFrameOS/issues/5) | Build shared Snapdragon installer and desktop payload | Clean build manifest and physical boot result |
| [MF-005](https://github.com/josethevrtech/MainFrameOS/issues/6) | Validate Android runtime | Exact image/kernel prerequisites and completed Android workflow |
| [MF-006](https://github.com/josethevrtech/MainFrameOS/issues/7) | Validate Wine/FEX runtime | Reproducible packages and completed Windows workflow |
| [MF-007](https://github.com/josethevrtech/MainFrameOS/issues/8) | Design recovery/update prototype | Written boot-state model and tested failure/fallback cases |

Each work item links to a GitHub issue with acceptance criteria. The MF identifiers remain stable roadmap references.

## Engineering bootstrap completed

- Verified ALARM bootstrap and isolated package compilation.
- MainFrameOS support package and strict device profile.
- Collabora source recipe compilation with upstream tests.
- Pinned candidate kernel source and device-tree build.
- Contract/unit CI, manual ARM64 builds, upstream drift reports and repository maintenance policies.

See [Build evidence](BUILD-EVIDENCE.md). These results do not mark M1 hardware/image acceptance complete.
