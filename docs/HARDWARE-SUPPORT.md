# Hardware scope and support policy

## Initial scope

The reference target is HP OmniBook 5 16-bf0xxx, board 8E33. Prioritize this physical device and closely related Snapdragon laptops. No additional laptop, desktop or headset is currently certified for MainFrameOS.

“Similar” means a promising port candidate with substantial shared platform support. It does not mean that the same installer, firmware, audio profile or power settings can be used unchanged.

## Expansion order

1. The reference OmniBook board and tested configuration.
2. Other units with that board, checking firmware and component variants.
3. Closely related OmniBook/Snapdragon platforms after reviewing their boot and Linux support.
4. Other Snapdragon computers with available testers and maintainable upstream support.
5. A separately scoped standalone VR headset investigation.

Do not select a second device based only on marketing name or CPU family. Compare device-tree availability, display/GPU support, firmware availability, audio topology, embedded controller, wireless hardware, boot access and recovery options.

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
