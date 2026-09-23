# Collabora integration decision

Decision: use **Arch Linux ARM** as the product base; selectively evaluate source-level work from Collabora's Holo Core AArch64 preview.

Collabora's announcement describes an Arch AArch64 preview, including package sources and a development container. Its build orchestration was not yet published in that announcement. This is distinct from the established Arch Linux ARM distribution. [Announcement](https://www.collabora.com/news-and-blog/news-and-events/building-an-arch-linux-aarch64-port-for-holo-core.html).

The source repository at commit `67f0d559c82cdc5c94317bad53ae45409720ef59` identifies its base as Arch's 2025-11-18 packaging snapshot and describes itself as a technology preview rather than a production OS. [Preview source](https://gitlab.steamos.cloud/holo/holo-core-aarch64-preview).

## First integrated recipe

`packages/compat-json-c` preserves the preview's `core-aarch64/j/json-c/0.18-2` recipe and licensing files byte-for-byte. `upstream/sources.lock.json` records repository, commit, path and each file's SHA-256. The library sources retain the recipe's BLAKE2 checksum check. Source retrieval runs before offline compilation and upstream tests.

This is a small C compilation and ABI/package compatibility test of the integration process. It is not a decision to replace ALARM's installed json-c or ship an older library in the OS. No generated package is installed on the laptop, and no Holo/SteamOS binary repository is added.

## Further imports

For each candidate: identify a concrete missing capability, compare current ALARM packaging and upstream status, preserve license and source attribution, rebuild within the selected package snapshot, run upstream and integration tests, then record why the downstream change is necessary. Track removal when upstream makes it redundant.

Do not merge thousands of historical recipes or mix repository binaries just to increase package count. Decide on a package-by-package basis, with consistent runtime libraries and dependency transitions.
