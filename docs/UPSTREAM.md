# Upstream references

Primary sources checked while preparing the initial plan on 2026-09-23. Upstream documentation may describe capabilities that still need packaging and device testing in MainFrameOS.

| Source | Relevance |
| --- | --- |
| [Arch Linux ARM background](https://archlinuxarm.org/about) | Project identity and ARM ports |
| [Generic AArch64 root filesystem](https://archlinuxarm.org/platforms/armv8/generic) | Starting userspace, not a laptop support guarantee |
| [Qualcomm Snapdragon X2 Linux announcement](https://www.qualcomm.com/news/onq/2026/09/snapdragon-summit-agentic-ai-pcs-linux) | Driver upstreaming and announced distribution milestones; see [tracking policy](QUALCOMM-LINUX.md) |
| [Qualcomm laptop kernel tree](https://github.com/linux-msm/laptops-kernel) | Community hardware work; not assumed to be the exact local kernel source |
| [Mesa platforms](https://docs.mesa3d.org/systems.html) | Driver families |
| [Freedreno / Turnip](https://docs.mesa3d.org/drivers/freedreno.html) | Qualcomm graphics and exact-device support lookup |
| [Waydroid](https://docs.waydro.id/) | Android container architecture |
| [Waydroid image compilation](https://docs.waydro.id/development/compile-waydroid-lineage-os-based-images) | ARM64 image target |
| [Waydroid Google Play certification](https://docs.waydro.id/faq/google-play-certification) | Image/service caveats |
| [FEX](https://fex-emu.com/) | x86 translation on ARM64 and Wine integration |
| [FEX ARM64EC](https://wiki.fex-emu.com/index.php/Development%3AARM64EC) | Windows translation integration details |
| [Flatpak multiarch](https://docs.flatpak.org/en/latest/multiarch.html) | Architecture-dependent runtime considerations |
| [Monado](https://monado.freedesktop.org/) | OpenXR runtime and named hardware support |

Hardware baseline facts also came from a targeted read-only inspection of the reference laptop and prior local audit notes. Only sanitized findings were transcribed; private logs and personal configuration are not repository inputs.
