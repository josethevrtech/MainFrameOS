# Build and packaging plan

The repository now contains a verified ALARM bootstrap, rootless package builder, support package, source-recipe compatibility build and candidate device-tree build. Image installation and OS update tooling remain unimplemented.

## Running the current pipeline

Requirements: native AArch64 Linux, Python 3.12 or later, Git, GNU Make, GnuPG, rootless Podman with working subordinate UID/GID mappings, network access and approximately 15 GiB free for builder/source caches. No host package installation or boot modification occurs in these commands.

```sh
make check
make bootstrap
make package-support
make package-canary
make kernel-dtb
```

Run as a normal user. `make bootstrap` downloads an upstream-signed root filesystem, checks locked SHA-256 values and the pinned signer fingerprint, imports it into Podman, and builds a fully updated ALARM toolchain. Package builds use the resulting immutable local image ID. The only mount inputs are task-owned build/output directories.

`build/` holds caches, sources, logs and the builder state. `out/` contains packages and manifests; `out/kernel-candidate/` contains the compiled DTB/configuration and its report. Nothing here is a bootable image. No package is automatically installed on the host.

A repeated `kernel-dtb` build requires moving its existing `build/kernel-candidate` directory aside first; extraction fails closed on an existing source tree. The kernel archive's Ubuntu packaging directories are omitted because an absolute symlink there is unnecessary for upstream Kbuild. Safe archive filtering remains enabled.

The imported json-c recipe is a compilation/integration test, not a product dependency selection. It retains upstream source checksum checks and runs all upstream tests. MainFrameOS support inputs have explicit SHA-256 checksums; update them deliberately with `python3 scripts/update-package-checksums.py` after editing their sources.

## Updating locked inputs

Review the new upstream revision and license changes, download and authenticate it, update `upstream/sources.lock.json`, run contract/tests, rebuild in a fresh environment and record hardware impact. A mutable upstream `latest` URL changing causes verification to fail; do not bypass the check. Keep the verified tarball and frozen builder in durable artifact storage before a production release.

The weekly upstream workflow reports source drift without updating locks. Dependabot proposes GitHub Actions updates; it does not monitor the entire OS package graph or merge updates automatically. ALARM security/package review remains a maintainer responsibility.

## Preserving and replaying the toolchain

`build/builder.json` records the immutable local image ID and package inventory hash. Preserve that image with `podman save --format oci-archive`, the inventory, verified bootstrap archive and source caches. Record the archive's SHA-256. Load it with `podman load` for replay; verify the expected image ID before building. Fresh `make bootstrap` uses current rolling repositories, so it is not a historical replay mechanism. See [Engineering limitations](ENGINEERING.md).


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

For each component retain upstream URL, revision, license, patch origin, hash and maintainer notes. Existing SteamOS branding, proprietary firmware, vendor applications and binary components must not be copied into a new image merely because they exist on the reference laptop. Preserve required notices and source availability for redistributed components. Original MainFrameOS code/documentation is MIT licensed; imported material retains its own license.
