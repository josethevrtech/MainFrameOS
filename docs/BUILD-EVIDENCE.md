# Engineering bootstrap evidence — 2026-09-23

## Base and compilation

The builder uses the upstream-signed Arch Linux ARM AArch64 root filesystem and ALARM package repositories. No SteamOS/Holo package repository or installed host package is an input.

| Check | Result |
| --- | --- |
| ALARM bootstrap signature | Verified against `68B3537F39A313B3E574D06777193F152BDBE6A6`, fingerprint published by ALARM |
| Bootstrap SHA-256 | `42a4eeaa038994ffd31fa173256ef2f0ef511358eeb41b9ea1f8626391b9b319` |
| Rootless builder | Created successfully; full ALARM package update performed inside container |
| MainFrameOS support package | Built successfully |
| Collabora json-c 0.18-2 recipe | Compiled as AArch64 against ALARM; 25/25 upstream tests passed |
| Kernel candidate | Pinned jglathe source tag matching local version string; exact installed equivalence remains unproven |
| OmniBook candidate DTB | Compiled successfully from source with upstream ARM64 defconfig |
| Repository tests | 15/15 unit tests passed; contracts, Python syntax and shell syntax checks passed |
| Reference identity probe | Matched HP OmniBook 5 / 8E33 and correctly reported bring-up, not release-ready |
| Package lifecycle | Installed, checked all files, exercised help and removed support package in a disposable ALARM container |
| Repeat package builds | Both package archives matched SHA-256 across two clean builds in the same frozen toolchain |

## Artifacts and provenance

Generated files remain under local `out/`; no unsigned package or candidate DTB was installed into the running OS. GitHub's manual build workflow can upload development artifacts for inspection, without publishing an OS release.

- [Package/toolchain inventory](evidence/2026-09-23/builder-packages.txt)
- [Support package manifest](evidence/2026-09-23/mainframeos-support.build.json)
- [Collabora recipe build manifest](evidence/2026-09-23/compat-json-c.build.json)
- [DTB build manifest](evidence/2026-09-23/kernel-dtb.build.json)
- [Repeat-build comparison](evidence/2026-09-23/rebuild-comparison.json)
- [Frozen builder archive](evidence/2026-09-23/builder-archive.json) — saved and hashed locally; remote retention remains pending

The package manifests record clean committed input `e2cfe78802cb76d4d0dd773ce4eb2fe2d3a8af8a`; those builds also matched the earlier package hashes. The candidate DTB manifest records the earlier development working tree. These are development evidence, not signed release attestations. Source hashes and the frozen toolchain are recorded; release builds must use a clean committed tree. GitHub contract/test CI also passed for the engineering pull request.

## Fresh hosted ARM64 build

[GitHub Actions run 35925713854](https://github.com/josethevrtech/MainFrameOS/actions/runs/35925713854) completed successfully from merged commit `5abe9aeb844977d7bf3812aa315ea2971c392b62` on a fresh `ubuntu-24.04-arm` runner. It verified the bootstrap, created a new rootless builder, passed 15 regression tests and 25 upstream json-c tests, built both packages and the candidate DTB, and uploaded development artifacts.

Both package SHA-256 values, the DTB SHA-256 and the installed-package inventory hash match the local results. This establishes matching results on two separate ARM64 hosts for these specific inputs, not whole-OS reproducibility or future replay of rolling repositories. See the [hosted manifests and artifact record](evidence/2026-09-23/hosted-build.json). The downloadable workflow artifact expires on 2026-10-07; permanent release retention remains pending.

## Issues found and resolved during bootstrap

- The generic download hostname's HTTPS certificate did not match. Used an ALARM mirror with valid TLS, then verified the upstream signature and pinned hashes.
- Nested Landlock download restrictions failed inside the rootless builder. Applied the container-only exception documented in [Engineering](ENGINEERING.md).
- An initially future-dated source timestamp caused Ninja to repeatedly regenerate. Corrected the epoch and made the build entry point reject future timestamps.
- The kernel source archive contains an Ubuntu-packaging absolute symlink. Omitted the Debian/Ubuntu packaging directories while retaining safe extraction for Kbuild sources.

## Review-driven build integrity fixes

The automated PR review identified stale package staging files and a missing bootstrap-lock check on the kernel path. Package staging now starts from a fresh generated directory; package and kernel builds share the same builder validation. Regression tests cover deleted inputs and rejection of an outdated builder by both entry points.

## What this does not establish

At the package-bootstrap milestone, no kernel Image/modules or disk image had been produced. The subsequent [USB preview](USB-PREVIEW.md) adds a compiled kernel and a disk image with a passing virtual boot test. A general installer, Android runtime integration, Windows runtime integration, image updater, release signatures and a hardware-certified MainFrameOS release remain pending. The DTB is unbooted and must not replace the current working one based on compilation alone. Repeat builds on one frozen builder are narrower evidence than independent reproducibility.
