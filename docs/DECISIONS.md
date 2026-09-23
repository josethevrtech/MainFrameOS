# Decision register

Updated 2026-09-23.

| Decision | State | Reason / next action |
| --- | --- | --- |
| Name: MainFrameOS | Owner-selected working name | Use consistently; no affiliation claim |
| Arch-based ARM system | Owner requirement | Confirmed implementation base is Arch Linux ARM AArch64; SteamOS is excluded as a build input |
| Snapdragon laptops and headsets | Owner requirement | Shared distribution across manufacturers and configurations; unrelated CPU platforms and a separate desktop-PC edition are outside current scope |
| Productivity and large-screen focus | Owner requirement | Desktop, applications and docking take priority |
| Native Linux, Android, `.exe`, Flatpak goals | Owner requirement | Validate each execution path and actual app workloads |
| One installer with hardware detection | Owner requirement | Shared installation flow and system, with platform profiles and boot adapters |
| Current laptop as first test machine | Owner clarification | A starting point for validation, not a product boundary or brand restriction |
| Full detail maintained on GitHub | Owner requirement | Keep design, roadmap and evidence in repository |
| KDE Plasma on Wayland | Proposed | Reuse familiar desktop; confirm during prototype |
| Waydroid ARM64 | Proposed | Existing Android-on-Linux route; prove prerequisites and workflows |
| Wine with FEX | Proposed | Existing Windows API/CPU translation route; prove packaging and apps |
| Developer image before managed base | Proposed | Ease hardware bring-up while designing production recovery |
| Image-based stable updates | Proposed | Backend and boot fallback mechanism remain unselected |
| Headset support within shared architecture | Owner requirement | Laptop testing starts first; headset boot/recovery and tracking need their own validation |

## Open engineering decisions

- Exact kernel source and patch maintenance plan.
- Precise marketed reference-chip SKU, beyond the observed DT compatible string.
- Firmware inventory and distributable/provisioned boundary.
- Repository snapshot/mirroring, signing and build infrastructure.
- Bootloader and deployment backend, with secure-boot compatibility investigated for the chosen installation path.
- Android image source and optional services policy.
- Essential Windows/Android application shortlist.
- Second device profile and available tester.
- Complete component-level license/firmware inventory before binary distribution. Original project code uses MIT; imported recipes retain their licenses.

Choose these using evidence from the reference prototype. Do not turn untested proposals into release promises.

## Engineering implementation decision

Collabora Holo Core is a source-level integration reference, not a base repository. A json-c recipe is pinned and rebuilt on ALARM as a compatibility test. Rootless isolated builds and read-only board identification are implemented; managed OS deployment and full kernel equivalence remain pending. See [Collabora integration](COLLABORA-INTEGRATION.md).
