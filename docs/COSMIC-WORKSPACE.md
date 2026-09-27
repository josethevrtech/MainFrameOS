# COSMIC direction and OpenXR workspace bring-up

The owner selected COSMIC as MainFrameOS's intended desktop on 2026-09-26.
Plasma remains the initial validation and recovery baseline. XR presentation,
tracking and the desktop session must be separate components so changing the
shell does not require replacing headset drivers.

## Validated COSMIC milestone

A separate Arch Linux ARM development root was prepared on the Frame, leaving
the working Plasma root and default session intact. A full signed repository
update resolved `cosmic-comp` and `cosmic-session` to `1:1.9.0-1`.

The first nested session produced a gray window. Switching the nested backend
alone did not resolve it. Adding the system bus and sharing the host PID namespace
made the panel and dock render. The session bus remained private. The owner then
confirmed: **Menu, apps and typing work**. This was COSMIC nested through X11
inside the existing Plasma workspace, not COSMIC presented by OpenXR.

The lab still logs unavailable/incomplete system services and portal integration.
This is a desktop usability milestone, not proof that every COSMIC system feature
works in the isolated session. COSMIC's Wayland/winit path is the candidate for
nesting inside the XR workspace and needs its own validation.

## Workspace integration

[WayVR](https://github.com/wayvr-org/wayvr), formerly WlxOverlay-S, is the candidate
bridge. It includes a Wayland compositor and can launch child applications into
OpenXR surfaces. Its release `v26.8.0` is pinned by immutable revision, source
archive and Cargo lock hashes in `upstream/workspace.lock.json`. The upstream
verified vendor archive allows offline builds without disabling Cargo checksums.

The native ARM64 build and control utility compiled successfully. The build disables default features and enables only
`openxr,wayland,x11`. OpenVR is not enabled. Optional dependency source may still
exist in the upstream lock/vendor bundle; that does not mean it is linked into
the selected build. No upstream project is rebranded or claimed as original code.

The [desktop adapter](../packages/mainframeos-workspace/README.md) launches COSMIC;
the established Plasma recovery session remains separate. `scripts/build-workspace.sh` builds the pinned bridge in a separate
ALARM build root with no network or host device access, two CPUs and 3 GiB. It
never installs into the running OS. The builder needs Rust/Cargo, native graphics,
Wayland/X11, PipeWire, font/audio, clang/shaderc and protobuf development inputs.
A complete dependency image lock and packaged OS integration remain future work.

To recreate the source archive from the exact upstream Git objects:

```sh
git -C /path/to/wayvr archive --format=tar.gz \
  -o /path/to/wayvr-v26.8.0-source.tar.gz \
  cb3aa42bd91aeda0e4d0de91593a6f878350c757
bash scripts/build-workspace.sh /path/to/verified-alarm-root \
  /path/to/wayvr-v26.8.0-source.tar.gz /path/to/vendor.tar.xz out/workspace
```

## Imported-buffer compatibility fix

The simulated OpenXR session reached FOCUSED. COSMIC created a Wayland surface,
then unmodified WayVR crashed in Turnip with both the Frame-specific and ALARM
Mesa drivers. Linear buffers reproduced the same crash. Instrumentation narrowed
it to Vulkano's cubic-filter capability query while creating an imported image
view. The query used DRM-modifier tiling without providing the modifier metadata.

The checked-in patch carries the image's modifier and sharing mode into that
query, satisfying [Vulkan tiling-02249](https://docs.vulkan.org/refpages/latest/refpages/source/VkPhysicalDeviceImageFormatInfo2.html).
The verified vendor archive remains unchanged. Explicit copies of Vulkano and its
macro crate form the patched path dependencies; the derived Cargo lock is hashed,
and compilation still uses `--frozen` with networking disabled. The public
preparation recipe was checked against the native build inputs byte for byte.
The patched build passed separate 30-second simulated runs with both the ALARM
and Frame-specific Vulkan drivers. Each reached FOCUSED, retained a visible
1280×800 COSMIC surface, and exited through the bounded test normally. This does
not verify headset pixels or headset input. The physical view test is pending.

[Recorded build and simulation evidence](evidence/cosmic-workspace-2026-09-27.json).

## Validation gates

1. Compile native ARM64 bridge with recorded provenance.
2. Create the desktop surface using a simulated Monado headset without panel access.
3. Test a bounded physical COSMIC desktop view with automatic return to the working session.
4. Validate keyboard, pointer, application launching and session exit; headset
   controllers remain unvalidated until a real controller input provider is added.
5. Test portals, audio, clipboard, file access and longer operation before
   making COSMIC the default.

A successful cube scene proves neither a spatial desktop nor a usable desktop
input path. Keep those milestones separate in release evidence.
