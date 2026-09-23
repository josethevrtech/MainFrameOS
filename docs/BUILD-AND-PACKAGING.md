# Build and packaging plan

There are no functioning build or installation scripts in this repository yet. This document defines the intended work and avoids placeholder commands that could be mistaken for a usable installer.

## Proposed source layout as implementation begins

| Area | Responsibility |
| --- | --- |
| `packages/` | PKGBUILDs, patches, configuration and package tests |
| `devices/` | Machine-readable board profiles and firmware requirements |
| `images/` | Root filesystem and boot artifact assembly definitions |
| `tests/` | Meaningful smoke checks and hardware acceptance tooling |
| `docs/` | Design, test procedures and release-specific findings |

Create these implementation areas when real content is ready. A directory tree is not a completed build system.

## Proposed package boundaries

- `mainframeos-release`: OS identity, release metadata and update-channel configuration.
- `mainframeos-desktop`: supported Plasma session dependencies and restrained defaults.
- `mainframeos-device-hp-omnibook5-8e33`: board matching and model-specific hardware configuration.
- Kernel package: pinned source, required patches, configuration, modules and matching device-tree artifacts; name finalized with the kernel maintenance plan.
- Firmware package or provisioning manifest: only distributable firmware included; otherwise a documented acquisition step.
- Android integration: Waydroid configuration and explicit runtime/image management.
- Windows integration: tested Wine/FEX packaging and app-profile support.

These are suggested names and boundaries, not packages available for installation.

## Build sequence

1. Establish exact sources and inputs for the working hardware stack.
2. Build required custom packages in a clean ARM64 environment.
3. Assemble a root filesystem from one recorded repository snapshot.
4. Apply the selected device profile and desktop/runtime packages.
5. Generate matched boot artifacts and a complete manifest.
6. Produce a model-specific test image with checksums.
7. Run automated smoke checks and physical-hardware acceptance.
8. Sign and promote a passing release candidate.

A clean build must not depend on the developer's home directory, host package cache, private credentials or undocumented manual edits. Archive necessary package inputs so repository churn does not make a past release impossible to reconstruct.

## Reproducibility levels

First require repeatable configuration and recorded binary inputs. Then work toward bit-for-bit reproducibility where toolchains and image formats allow it. Do not claim identical hashes until independent rebuilds demonstrate them.

## CI and physical testing

Documentation checks and package builds can run without laptop access. Emulated ARM or generic ARM runners can check userspace logic but cannot certify the OmniBook's audio, GPU, suspend, display or firmware. Use a dedicated test machine for those checks.

Keep signing and release publishing separate from untrusted contribution builds. Choose runners, artifact retention and release infrastructure when the first build pipeline is ready; do not imply a free hosting capacity or cost estimate yet.

## Source and redistribution inventory

For each component retain upstream URL, revision, license, patch origin, hash and maintainer notes. Existing SteamOS branding, proprietary firmware, vendor applications and binary components must not be copied into a new image merely because they exist on the reference laptop. Preserve required notices and source availability for redistributed components. Project-wide licensing remains an explicit maintainer decision.
