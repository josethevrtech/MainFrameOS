# Decision register

Updated 2026-09-23.

| Decision | State | Reason / next action |
| --- | --- | --- |
| Name: MainFrameOS | Owner-selected working name | Use consistently; no affiliation claim |
| Arch-based ARM system | Owner requirement | Proposed implementation base is Arch Linux ARM AArch64 |
| Snapdragon-only hardware scope | Owner requirement | Do not expand to unrelated CPU platforms |
| Productivity and large-screen focus | Owner requirement | Desktop, applications and docking take priority |
| Native Linux, Android, `.exe`, Flatpak goals | Owner requirement | Validate each execution path and actual app workloads |
| Current laptop and similar first | Owner-confirmed scope | OmniBook 5 16-bf0xxx / 8E33 is the reference |
| Full detail maintained on GitHub | Owner requirement | Keep design, roadmap and evidence in repository |
| KDE Plasma on Wayland | Proposed | Reuse familiar desktop; confirm during prototype |
| Waydroid ARM64 | Proposed | Existing Android-on-Linux route; prove prerequisites and workflows |
| Wine with FEX | Proposed | Existing Windows API/CPU translation route; prove packaging and apps |
| Developer image before managed base | Proposed | Ease hardware bring-up while designing production recovery |
| Image-based stable updates | Proposed | Backend and boot fallback mechanism remain unselected |
| Headsets after laptop foundation | Recommended sequencing | Hardware access and tracking require independent feasibility |

## Open engineering decisions

- Exact kernel source and patch maintenance plan.
- Precise marketed reference-chip SKU, beyond the observed DT compatible string.
- Firmware inventory and distributable/provisioned boundary.
- Repository snapshot/mirroring, signing and build infrastructure.
- Bootloader and deployment backend, with secure-boot compatibility investigated for the chosen installation path.
- Android image source and optional services policy.
- Essential Windows/Android application shortlist.
- Second device profile and available tester.
- Project licensing before external contribution or binary distribution.

Choose these using evidence from the reference prototype. Do not turn untested proposals into release promises.
