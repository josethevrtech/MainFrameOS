# MainFrameOS engineering instructions

- Product base: Arch Linux ARM AArch64. Never add SteamOS/Holo binary repositories or use the developer's installed OS as the root filesystem input.
- Keep third-party source origin, immutable revision, hashes and licenses with each import. Change lock files deliberately; never disable source/package verification to make a build pass.
- Run `make check` and the affected isolated package/kernel build. Do not install development packages or replace host boot artifacts as part of a build.
- Keep model matching strict. Mark hardware as supported only with release-specific physical test evidence.
- Distinguish compiled packages, compiled DTBs, bootable images and physically validated releases. Never equate one with another.
- Preserve `sources/` reference files if working from a ChatGPT project mirror.
- Keep secrets, raw personal logs, firmware binaries, generated packages and build caches out of Git.
- Update source attribution, engineering limitations and build evidence when implementation changes.
- Use pull requests and required CI once branch protection is enabled. Do not bypass or weaken repository protection to publish changes.
