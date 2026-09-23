# Qualcomm Linux enablement tracking

Checked 2026-09-23. Snapdragon laptops and headsets are the MainFrameOS product scope across manufacturers and configurations. Upstream readiness determines implementation order, rather than similarity to the developer's laptop.

## Snapdragon X2 announcement

Qualcomm's [September 23, 2026 announcement](https://www.qualcomm.com/news/onq/2026/09/snapdragon-summit-agentic-ai-pcs-linux) describes upstreaming Snapdragon X2 core drivers, including Adreno GPU and Hexagon NPU support. It targets Debian availability by the end of 2026 and Ubuntu certification in the first half of 2027. These are Qualcomm's announced milestones, not MainFrameOS release commitments.

This creates a useful upstream path for MainFrameOS to evaluate. It does not establish a currently complete driver stack for every laptop configuration, nor headset boot, tracking or firmware support. Distribution certification is also distinct from kernel/Mesa support that other distributions may integrate.

## Integration policy

- Track public kernel changes, graphics drivers, firmware and platform descriptions by exact revision and license.
- Distinguish announced, posted for review, merged, packaged, boot-tested and release-validated states.
- Evaluate applicable work for current and newer Snapdragon generations; do not require a brand relationship to the first test machine.
- Package necessary changes for Arch Linux ARM with regression coverage and a plan to remove downstream patches when upstream is sufficient.
- Extend the shared installer's profile catalog and boot adapters as configurations become testable.
- Record GPU, NPU, audio, suspend, displays and other subsystem results separately. One functioning driver does not certify a whole device.

MainFrameOS remains based on Arch Linux ARM. Reusing upstream Qualcomm work does not require changing the userspace base to Debian or Ubuntu. Full system support still depends on matching firmware, boot configuration and physical testing.
