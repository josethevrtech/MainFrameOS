# Roadmap and initial backlog

Milestones are ordered by dependency, not calendar promises. No build milestone is complete at project initialization.

## M0 — Capture the reference platform

- [x] Define product scope and identify the reference laptop.
- [x] Record a sanitized summary of the existing hardware evidence.
- [ ] Recover exact kernel sources, configuration and patch provenance.
- [ ] Identify active boot artifacts and required firmware with hashes.
- [ ] Inventory custom audio, power and service configuration.
- [ ] Re-run unresolved baseline tests after the final fixes.

**Exit:** another developer can explain how this board boots and which changes its working hardware needs, using recorded sources and configuration.

## M1 — Arch Linux ARM desktop prototype

- [ ] Establish a consistent ARM64 package source and build environment.
- [ ] Package the board's required kernel, audio, firmware integration and power configuration.
- [ ] Assemble a model-specific development image.
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

**Exit:** an experimental, reproducibly configured preview is available for the named reference profile. It is not a promise of broad device support or production reliability.

## M4 — Reliable update foundation

- [ ] Select and implement a deployment/rollback mechanism.
- [ ] Validate boot success detection and fallback behavior.
- [ ] Define persistent configuration and migration policy.
- [ ] Establish signing, testing/stable promotion and security-fix workflow.
- [ ] Pass interrupted/failed-update and regression checks.

**Exit:** repeatable update and recovery evidence supports a daily-use release candidate.

## M5 — Closely related device

- [ ] Select a second actual board with a tester and viable upstream support.
- [ ] Add its distinct hardware profile.
- [ ] Re-run complete acceptance checks and publish limitations.

**Exit:** shared components demonstrably support two validated profiles without assuming they are interchangeable.

## Later — Snapdragon PCs and VR

Evaluate each new platform independently. Headsets need a boot/recovery and tracking feasibility study before promises of a standalone MainFrameOS edition. Keep laptop reliability ahead of expansion.

## First implementation work items

| ID | Work item | Completion evidence |
| --- | --- | --- |
| MF-001 | Reconstruct reference kernel and DTB provenance | Source commit, patch series, config and boot artifact mapping |
| MF-002 | Package OmniBook audio integration | Clean package install, outputs/mic and repeated hotplug/suspend tests |
| MF-003 | Package power and platform services | Service ownership, profile behavior, charge limit and energy measurements |
| MF-004 | Build minimal ARM64 desktop image | Clean build manifest and physical boot result |
| MF-005 | Validate Android runtime | Exact image/kernel prerequisites and completed Android workflow |
| MF-006 | Validate Wine/FEX runtime | Reproducible packages and completed Windows workflow |
| MF-007 | Design recovery/update prototype | Written boot-state model and tested failure/fallback cases |

These identifiers are backlog references, not GitHub issue numbers.
