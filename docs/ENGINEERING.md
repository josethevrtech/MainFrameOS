# Engineering and maintenance contract

MainFrameOS uses **Arch Linux ARM AArch64** as its base. SteamOS is neither a package repository nor an image input. The current laptop installation supplies hardware observations only. Collabora source recipes are evaluated and rebuilt against the chosen base; importing another distribution's binary repository is not the integration strategy.

## What is implemented

- Signed, SHA-256-locked upstream bootstrap verification, using an isolated keyring.
- Rootless Podman builder with a recorded image ID and complete installed-package inventory.
- Unprivileged package builds; source retrieval separated from offline compilation/tests.
- A source-recipe compatibility test imported from Collabora's preview, preserving its license and pinned origin.
- Read-only hardware identification with strict board matching and automated negative tests.
- CI for repository contracts and tests; manual native ARM64 package build workflow.
- Ownership, contribution templates, security reporting policy and dependency-update configuration.

These are implemented controls, not a certification. Read the latest [build evidence](BUILD-EVIDENCE.md) for results and limits.

## Required before a supported OS release

| Requirement | Acceptance evidence | Current state |
| --- | --- | --- |
| Source provenance | Kernel commit, patches, config, firmware manifest and licenses | Partial; candidate source identified |
| Complete image | Clean installation with correct identity, boot artifacts and package manifest | Not implemented |
| Hardware reliability | Reference-board test matrix, repeated suspend/dock tests | Baseline evidence only |
| Application promises | Completed native/Flatpak, Android and Windows workflows | Pending on MainFrameOS |
| Rebuildability | Archived builder + package/source inputs, independent rebuild result | Package-level work started |
| Update/recovery | Failed-update and boot-fallback tests on hardware | Design only |
| Supply-chain publication | Release signatures, provenance and inventory tied to final artifacts | Development hashes only |
| Support staffing | Named backup maintainer/tester and response process | Owner assigned; backup not assigned |
| Repository enforcement | Required checks and protected release branches configured in GitHub | `main` protected with required CI; release controls pending; see [verified settings](REPOSITORY-SETTINGS.md) |

## Maintenance responsibilities

The initial owner and code owner is `@josethevrtech`. Hardware profile, kernel, packaging, applications and release duties currently roll up to that owner. Do not describe this as round-the-clock staffed support. Recruit an additional maintainer/tester before promising a service level or promoting a broadly supported release.

For each release candidate: review upstream advisories and package changes, rebuild affected dependencies together, run regression tests, document migration/recovery effects, and retain the prior working deployment and its inputs. Fix urgent security issues through the same traceable process with focused testing. Publish actual response performance rather than an unsupported SLA.

Supported versions: none yet. Development artifacts can change and carry no daily-use support promise. When a stable line exists, publish its support window, upgrade path and end-of-life date before release. An unfixed critical issue, missing tester or unreproducible kernel can demote a profile to experimental.

## Quality goals relative to other distributions

The owner's “better than Omarchy” objective becomes measurable requirements: documented inputs, isolation, CI, update/recovery evidence, strict hardware scope, app-level testing, and a clear maintenance lifecycle. No superiority claim is made without a dated comparative study using equivalent hardware and workloads. MainFrameOS should learn from other projects without depending on their branding or copying unrelated defaults.

## Development host boundary

Builds do not repartition storage, change the running kernel, replace boot entries or install packages onto the host. Containers receive only build/output directories, not the developer's home or container socket. Compilation is capped at two CPUs and 3 GiB by default so the laptop remains usable.

Pacman's Landlock filesystem download restriction is disabled **only for the package-install command inside the rootless builder** because the reference host rejected that nested restriction. Container isolation, TLS, package signatures and syscall restrictions remain. This is recorded here and in the Containerfile; no host pacman configuration is changed. Re-evaluate this workaround on updated Podman/kernel versions. [Pacman option documentation](https://man.archlinux.org/man/pacman.8.en).

## Reproducibility limits

The root filesystem tarball is pinned. Initial builder creation performs a full update against rolling ALARM repositories, so recreating that builder later is not guaranteed identical. The resulting image ID and package inventory freeze a local build environment; preserving its OCI archive and source cache is necessary for replay. Do not call the whole OS reproducible until archived inputs and independent rebuilds demonstrate it.

Package manifests and `.BUILDINFO` support dependency inventory; they are not yet a complete SPDX/CycloneDX OS SBOM. Release signing, source attestation, image generation and a binary repository are still explicit milestones.
