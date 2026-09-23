# Reference device: HP OmniBook 5 16-bf family

Recorded: 2026-09-23. This is a sanitized development baseline, not a MainFrameOS certification.

## Directly observed identity

| Field | Observation |
| --- | --- |
| DMI manufacturer | HP |
| DMI product | HP OmniBook 5 Laptop 16-bf0xxx |
| DMI board | 8E33 |
| Device-tree model | HP OmniBook 5 |
| Device-tree compatible entries | `hp,omnibook-5`, `lenovo,thinkpad-t14s`, `qcom,x1p42100` |
| CPU | Eight Qualcomm Oryon cores; AArch64 |
| GPU | Adreno X1-45 in the 2026-09-22 Vulkan audit |
| Running kernel | `7.1.13-jg-0-qcom-x1e` |
| Current OS identity | SteamOS 0.1, custom-20260922, experimental hardware port |
| Installed Plasma / KWin | 6.6.2 |
| Installed Mesa / vulkan-freedreno | 1:26.0.1-1 |
| Installed PipeWire / WirePlumber | 1:1.6.0-1 / 0.5.13-1 |
| Installed Flatpak | 1:1.16.3-1 |

The `qcom,x1p42100` value is an observed software compatibility identifier. Confirm the precise marketed chip SKU from authoritative hardware identification before assigning one in release metadata. The inherited ThinkPad compatibility entry does not make this a ThinkPad or demonstrate ThinkPad support.

No serial numbers, network addresses, disk identifiers, credentials or raw personal logs are included.

## Evidence and limitations

The owner reports satisfaction with current SteamOS performance. Previous local audit notes contain successful checks as well as later regressions. They inform the starting point; all release acceptance checks must run against the eventual MainFrameOS image.

| Function | Existing evidence | MainFrameOS follow-up |
| --- | --- | --- |
| Boot/storage | Prior audit verified standalone NVMe root boot | Reconstruct and test a clean install and recovery boot |
| GPU | Prior hardware Vulkan rendering test passed | Verify OpenGL/Vulkan, compositing and sustained workloads |
| Internal/external display | Prior owner confirmation at 2560×1440, 120/144 Hz | Repeat cold boot, hotplug, scaling and docking checks |
| Audio | Custom UCM and audio policies restored; playback/capture checks recorded | Re-test internal/DP outputs, microphone and headphone switching |
| Display audio regression | Later audit recorded missing sink, route fallback and start delay; workarounds applied | Confirm physical audio, idle wake, hotplug and suspend after final changes |
| Brightness | Internal backlight readback tested | Re-test with packaged permissions |
| External brightness | DDC polling disabled as a link-failure mitigation | Investigate separately; avoid inheriting workaround globally |
| Wi-Fi/Bluetooth | Prior connectivity and post-suspend reconnection evidence | Repeat with current drivers and normal peripherals |
| Suspend | One documented cycle passed before later changes | Test repeated cycles and overnight drain |
| Webcam | Frame streaming passed before/after suspend | Test browser calls and recording |
| Power profiles | Custom profile changes verified through D-Bus | Measure thermals, performance and energy use |
| Battery/charge limit | Telemetry and 80% limit previously verified | Recheck persistence and provide a user setting |
| Printing | Software setup verified; physical print deferred | Test an actual printer before claiming support |
| NPU | Unconfigured/unverified in baseline | Experimental follow-up, not a core dependency |
| Sensors | Earlier discovery failures | Do not claim auto-brightness/rotation support |

## Changes worth extracting

1. Model-specific ALSA UCM profile and required PipeWire/WirePlumber configuration.
2. Audio sleep/wake handling and external-output recovery policy, reviewed for necessity and race conditions.
3. Qualcomm service dependencies such as QRTR/PD support, with exact package ownership established.
4. Power-profile configuration, charge-limit behavior, brightness access and zram defaults.
5. Kernel/device-tree/firmware sources and the working boot sequence.

Do not copy per-user paths, account configuration, paired-device databases, network credentials or temporary repair scripts into a distributable image. Convert useful policy into maintainable system packages with explicit user overrides.

## Boot-specific finding

The previous migration audit reports a repaired ARM64 EFI loader with an embedded legacy configuration path. That path is an implementation dependency of the existing bootloader, not proof that the former Arch installation still exists. A clean MainFrameOS boot design must replace this dependency deliberately and preserve a usable recovery route.

## Baseline tasks

- Establish exact kernel source commit, configuration, patches and build toolchain.
- Identify the active DTB and explain the inherited compatibility strings.
- Inventory required firmware with file hashes, provenance and redistribution status.
- Convert custom audio/power configuration into packages.
- Run the full test plan after the final baseline changes.
- Produce a model profile without claiming other OmniBook variants are interchangeable.
