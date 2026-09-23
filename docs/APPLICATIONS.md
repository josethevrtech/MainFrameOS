# Application strategy

## Four execution paths

| Application type | Proposed path | Key limit |
| --- | --- | --- |
| Native Linux ARM64 | Arch Linux ARM / MainFrameOS packages | Package availability and compatible dependencies |
| Flatpak | ARM64 application and matching runtime | An x86-only app does not become ARM-native through packaging |
| Android | Waydroid with ARM64 Android image | App services, graphics, ABI, input and device integrations |
| Windows x86/x64 | Wine plus FEX translation | Per-app API, CPU, graphics, installer and service compatibility |

FEX's Wine integration supports a route through ARM64 Wine with WoW64/ARM64EC components. Validate available versions and build/package requirements on Arch Linux ARM before choosing a shipping configuration. Do not assume ordinary ARM64 Wine automatically translates arbitrary x86 executables. Sources: [FEX](https://fex-emu.com/) and [ARM64EC integration](https://wiki.fex-emu.com/index.php/Development%3AARM64EC).

## Native and Flatpak first

Use native ARM64 software for the browser, desktop services and normal productivity where practical. Flatpaks provide a useful application delivery path, but their runtimes and GPU integration still require testing. Verify current availability for each proposed default application.

Initial candidate workflows: browser documents and calls, office documents/PDFs, text/code editing, image editing, media playback and screen recording. Baseline installation/startup evidence exists for some applications; it does not certify the future image.

## Android integration

Waydroid runs Android in a container on Linux and publishes an ARM64 image build target. Host kernel support, graphics access and the Android image must align. Sources: [overview](https://docs.waydro.id/) and [image builds](https://docs.waydro.id/development/compile-waydroid-lineage-os-based-images).

Prototype startup/shutdown, windowed app launch, resizing, keyboard shortcuts, mouse/touch input, clipboard, audio, notifications and file exchange. Test suspend and battery cost with Android idle as well as active. Keep the Android environment optional when unused.

Choose Android image provenance and update policy explicitly. Google services, device integrity checks and protected media may impose application-specific requirements; do not promise universal compatibility. Default image choice remains open.

## Windows integration

Begin with a small reproducible `.exe` workflow and then the owner's essential applications. Store a separate prefix per app or compatible app group. Pin tested Wine/FEX versions and relevant libraries in each profile; record graphics translation requirements where applicable.

Test installation, launch, document open/save, dialogs, clipboard, fonts, networking, printing if required, clean shutdown and repeated launch. A splash screen is not acceptance. Kernel drivers, proprietary services and unsupported APIs may prevent operation.

Expose useful failure reports and compatibility status. Do not silently download unreviewed installers or automatically execute a downloaded `.exe`.

## Compatibility record template

| Field | Required content |
| --- | --- |
| Application | Exact name, version and architecture |
| Source | Vendor/distribution source and checksum when applicable |
| Environment | Image, device profile, runtime versions |
| Workflow | Actual task performed and expected output |
| Result | Pass, limited, fail or untested |
| Evidence | Sanitized log or reproduction notes |
| Limitations | Missing features and practical impact |
| Regression check | Date and previous known-good combination |

No Android/Windows application is certified by this initial documentation. The essential-app shortlist remains to be established; native office, browser and media workflows can proceed independently.
