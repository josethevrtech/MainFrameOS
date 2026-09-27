# MainFrameOS Frame XR source integration

This is a source recipe, not yet a distributable pacman package. It imports the
six patches used by the physical Frame experiment into the independent ALARM
project. It does not install SteamVR or change the active OpenXR runtime.

Upstream: <https://gitlab.freedesktop.org/monado/monado.git>, commit
`2773473de89567771114d6818f15cfd7c8216822`. The immutable Git tree and each patch
are locked in `upstream/frame-xr.lock.json`. Patches retain upstream BSL-1.0
notices; see `LICENSE.monado` and upstream per-file licensing. The MainFrameOS
generator and build scripts use the project's MIT license.

Patch order: timestamped diagnostic pose transport; measured optics; presentation
diagnostics; optional unscheduled presentation workaround; optional GPU timing;
optional Frame panel rotation.
The transport changes the experimental remote-driver protocol, so an unmodified
upstream remote client is not compatible. It is not a general network XR service.

The measured optical input stays private and must match the recorded hash. It
represents one tested device configuration at a fixed approximately 70 mm IPD,
not general calibration for every headset or wearer. The original working
prototype also needs vendor tracking services and calibration. They are not
included or silently replaced by this recipe.

From the repository root, with a local upstream Git clone containing the pin:

```sh
python3 scripts/frame_xr.py prepare \
  --repository /path/to/monado \
  --optics /path/to/private/optics-129.json \
  --destination build/frame-xr-source
bash scripts/build-frame-xr.sh /path/to/verified-alarm-build-root \
  build/frame-xr-source out/frame-xr
```

Preparation reads the pinned Git objects, ignoring the developer's modified
working tree, verifies recipe hashes, applies every patch and regenerates the
optics header. Existing destinations are refused. The complete prepared source
inventory is checked before and after compilation.

The native ARM64 build uses an existing ALARM build environment with CMake,
Ninja, a compiler and Monado's dependencies installed. It does not install
dependencies on the host. Bubblewrap gives it a read-only root and source,
private namespaces, no network, no display/DRM devices and only the output
directory writable. A transient user service limits it to two CPUs and 3 GiB.
The output includes staged files, builder package inventory and a build report.
The OpenVR frontend, SteamVR plugin and SteamVR lighthouse integration are
disabled; this build targets OpenXR.
Discarding that new output directory rolls back the build; no live setting changes.

This records the existing builder; it does not yet reconstruct a fresh dependency
image from archived packages. Passing this build is not a bootable image test or
a physical validation of the newly compiled binaries. See
[Frame bring-up](../../docs/FRAME-BRINGUP.md).

## Panel orientation experiment

`MAINFRAME_FRAME_PANEL_ROTATION=1`, together with `MAINFRAME_FRAME_OPTICS=1`,
sets each physical panel view to Monado's 180-degree rotation. It changes panel
mapping, not desktop texture orientation or head/eye poses. Both options default
to off. Enable this only for the identified Frame optical prototype, not generic
remote headsets.

The first physical COSMIC test exposed upside-down, misaligned stereo imagery
despite the earlier cube-scene confirmation. A six-second KMS recording reproduced
the issue. With this correction an isolated incremental build produced upright
COSMIC and keyboard images in both recorded eyes. This is capture-based evidence;
wearer comfort, stereo fusion and controller input remain unvalidated. See
`docs/evidence/frame-workspace-tabletop-2026-09-27.json` for build and test scope.
The normal desktop remains the recovery session.
