# Frame: independent productivity system

MainFrameOS uses the project's Arch Linux ARM base, KDE Plasma and a planned
OpenXR productivity session. SteamOS is a hardware reference, not the product
root filesystem or package feed. The existing laptop installer is not safe to
run on the headset; Frame boot/recovery needs its own adapter.

## What has actually worked

On 2026-09-26, the owner confirmed a one-minute physical Monado/OpenXR scene
visible in both eyes, natural head movement and restoration of the normal
desktop afterward. SteamVR was stopped during that scene. Instrumented
presentation returns averaged 89.93 Hz at the panel's 90 Hz setting; this is
not a photon latency measurement. The source pin is
`2773473de89567771114d6818f15cfd7c8216822` plus the five recorded patches.

The working setup uses Linux `6.18.0-g8790bd420211`, Frame-specific Mesa,
vendor XRService/libArcturus tracking and measured optical/calibration data.
It is an independent compositor experiment with remaining vendor dependencies,
not an entirely open hardware stack. Tracking validity was checked, but quality
callbacks do not yet justify setting OpenXR TRACKED flags. Controllers,
passthrough and long-duration reliability remain unvalidated.

Two essential settings were `MAINFRAME_FRAME_UNSCHEDULED_PRESENT=1` and
`U_PACING_COMP_MIN_TIME_MS=7`. Brightness restoration and a fresh fallback VR
session were necessary for reliable return from the test. Earlier attempts
stalled or stayed black. The existing working desktop therefore remains the
default until a complete independent desktop session passes recovery tests.

The measured CPU sensor reached 90.7 degrees C during the minute-long run;
GPU reached 63.2 degrees C. These are not skin temperatures or a thermal
equilibrium assessment. No thermal protections were changed.

## Buildable first step

[Frame XR source recipe](../packages/mainframeos-frame-xr/README.md) reconstructs
and builds the recorded runtime in an isolated ALARM environment. It deliberately
does not import personal logs, optical data, vendor binaries, firmware, private
package URLs, sudo policies or machine account paths into the product.

A clean native ARM64 build completed on 2026-09-26 in a read-only ALARM build
root with network and display access disabled. The staged service and runtime
library are AArch64 ELF files. OpenXR, the service and remote driver are enabled;
OpenVR, the SteamVR plugin and SteamVR lighthouse integration are disabled.
All 32 repository tests passed. See the [artifact hashes](evidence/frame-xr-build-2026-09-26.json)
and [source comparison](evidence/frame-source-rebuild-2026-09-26.json).

The measured source modifications reproduce the working prototype. New build
artifacts require their own physical validation. This work does not claim a
complete bootable MainFrameOS Frame image, custom kernel or finished spatial
KDE desktop.

## Kernel ownership and future Valve updates

MainFrameOS will maintain its own kernel configuration, patch series, version
suffix, build provenance and release testing. Valve's Frame kernel is a hardware
reference whose relevant changes can be reviewed and ported. An update is a
candidate for integration, never an automatic replacement of a working kernel.

The initial known reference and module hashes are in
`kernels/frame/reference.lock.json`; its configuration is `reference.config`.
The package identifies source commit
`8790bd4202113bbce9ee4315d7735ab8b75c8485` in Valve's linux-valve repository.
That source endpoint required sign-in when checked. This prevents an exact
source rebuild of that reference today; it does not prevent independent
userland work or an upstream-based kernel port.

After an observed vendor update, run on the Frame:

```sh
python3 scripts/frame_kernel.py capture /path/to/new-reference
python3 scripts/frame_kernel.py compare /path/to/new-reference/reference.json
```

Capture reads the hardware compatible strings, running configuration, kernel,
DTB and module hashes, and selected package versions. It does not install
updates, read private repository URLs or change a lock. The comparison is an
installed-reference check, not an online watcher or a claim that no newer
upstream release exists. A renamed future kernel package will be reported as
missing and needs explicit review.

For each new source candidate: record its origin/commit/license; review display,
GPU, DSP, tracking, power, storage and boot changes; port the needed changes to
the MainFrameOS kernel branch; compile matching modules/DTBs from source; then
test through a recoverable external boot. Preserve the previous image and
complete matching hardware bundle. Never mix arbitrary stock modules with a
new kernel ABI or silently relabel a stock binary as a custom build.

## Next integration gates

1. Package the rebuilt OpenXR runtime and define a tracking-provider boundary.
   Keep the current vendor-backed bridge explicitly experimental while bringing
   up an open sensor/tracking provider.
2. Build the KDE workspace presentation and input bridge on OpenXR. OpenXR
   provides XR runtime APIs; it does not automatically place a Plasma desktop
   in space. Add the productivity tile launcher, virtual displays and reliable
   keyboard/mouse interaction with app launching.
3. Assemble an independent ALARM userland with those components and a strict
   Frame boot/recovery profile. Keep device calibration private and preserve the
   verified stock recovery copies. No internal repartitioning is part of this work.
4. Build and validate the MainFrameOS kernel from an accessible pinned source
   candidate. Until then the installed stock kernel is the bring-up reference,
   not evidence of an independently compiled MainFrameOS kernel.
5. Test cold boot, tracking loss, brightness, input, suspend, heat, update failure
   and rollback before replacing the default session or advertising support.
