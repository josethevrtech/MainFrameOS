# Hardware scope and support policy

## Product scope

MainFrameOS targets Snapdragon laptops and headsets through one installer and a shared Arch Linux ARM system. Coverage can grow across manufacturers, chip generations and hardware configurations. There is no supported MainFrameOS release image yet.

The current developer laptop is an initial test platform. Its exact identity belongs in the [technical test record](hardware/HP-OMNIBOOK-5-16-BF.md) and machine-readable profile, not in a product restriction. Contributors can propose other Snapdragon laptops or headsets without matching that laptop's brand or chip.

## How coverage grows

Prioritize usable upstream support, recoverable boot access, available testers and maintainable drivers. Share common kernel, graphics and firmware integration; use board/configuration profiles for genuine differences. Prefer one shared kernel where feasible, while permitting explicitly tracked kernel tracks when a platform requires them.

A single installer selects the appropriate profile and boot adapter. Firmware, audio wiring, displays and recovery procedures can still vary between configurations. See the [installer design](INSTALLER.md) and [Qualcomm enablement tracking](QUALCOMM-LINUX.md).

Bring up the available laptop first to exercise the pipeline, add another distinct configuration to prove the shared design, and investigate accessible headsets within the same architecture. This is test sequencing, not an exclusive list of eligible devices.

## Status vocabulary

| Status | Meaning |
| --- | --- |
| Candidate | Potential target; no validated MainFrameOS boot |
| Bring-up | Boot or component work in progress |
| Experimental | Image boots; significant gaps or incomplete acceptance testing |
| Supported | Named release passes the published core test matrix on the named profile |
| Regressed | Previously accepted functionality fails on a newer candidate |

Every support statement must identify the board, image version, kernel/firmware set and test date. A single successful suspend or compositor launch is evidence for that event, not broad certification.

## Adding a profile

Provide sanitized identity, boot method, firmware origins, kernel/DTB details, component results, recovery instructions and a maintainer/tester. Record unavailable features explicitly. Keep failed evidence visible when updating results.

## VR requirements

Standalone headset support requires an authorized boot path, recoverable installation, display timing, GPU access, sensors, cameras, tracking calibration, controllers/input, audio, power management and an appropriate XR runtime/session. Monado/OpenXR is a candidate component, not a replacement for missing hardware access. Locked boot firmware or unavailable tracking drivers can block an individual headset regardless of Snapdragon CPU support.
