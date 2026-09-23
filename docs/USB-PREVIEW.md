# USB development preview

This build targets a personal hardware test on the initial development laptop. The shared installer remains under development. The USB image does not contain an internal disk installer or claim support for other configurations.

## Contents

The image uses the verified Arch Linux ARM bootstrap and ALARM packages. It includes Plasma Wayland, Firefox, Konsole, Dolphin, Kate, Discover, Flatpak, NetworkManager, Bluetooth and PipeWire. Kernel Image, modules and device tree are compiled from the pinned source in `upstream/sources.lock.json`, using ARM64 defconfig and `images/usb/kernel.fragment`. The kernel has its own MainFrameOS version suffix.

The root filesystem comes from ALARM, never from the installed SteamOS system. Only the required, personally provisioned device firmware is taken from the current machine. Firmware hashes are recorded locally. This image must not be redistributed until the relevant redistribution terms are established.

The kernel configuration is a new development configuration, not a recovered copy of the installed kernel config. The candidate device tree differs from the existing boot tree in video decoding and display audio. Those differences and the existing internal audio routing require follow-up testing and integration.

## Build

Use the [foundation build requirements](BUILD-AND-PACKAGING.md), then prepare the verified builder, support package and source with `make bootstrap package-support kernel-dtb`. Existing kernel source extraction directories must be moved aside before rerunning the DTB extraction step.

Run `python3 scripts/build-usb.py --firmware-directory /path/to/personally/provisioned/device/firmware --firmware-provenance /path/to/firmware-inputs.json` on the initial AArch64 test platform. The script creates isolated tool and desktop images, compiles the kernel, stages the firmware and assembles a regular disk image under `out/`. It never writes a physical drive. Kernel compilation uses four CPUs and a 3 GiB memory limit. Move previous USB staging/assembly directories and output images aside before a fresh image build.

The firmware provenance JSON must contain nonempty `origin`, `device_profile`, `revision` and `license_status` strings, `redistribution_allowed: false`, and a `files` object mapping every relative firmware path to its SHA256. The build rejects missing provenance or differing file hashes. Keep this local record with the private image.

The tool and desktop builders record their image IDs, recipe hashes, bootstrap digest and base image identity under `build/usb-tools` and `build/usb-desktop`. Move the respective directory aside to rebuild after a recipe change. Their initial ALARM package resolution uses rolling repositories; retain the resulting images and package inventory for replay.

`python3 scripts/smoke-usb.py` boots the generated image in a network-isolated QEMU ARM machine with temporary disk writes. It first verifies the image checksum and GPT checksums, extracts the kernel and initramfs from the finished image EFI partition, then checks the kernel, initramfs and real root filesystem, then shuts down. It does not emulate the laptop's GPU, firmware, audio, USB controller or EFI implementation.

## Test session

The desktop signs in as `mainframe`. Console credentials are username `mainframe`, password `mainframe`. Local administration uses `sudo`; SSH is disabled. The root account remains locked. This is a local test session with persistent USB storage, not a secured personal installation.

After the image has been verified, confirm the exact USB drive before erasing it. Never select the internal SSD. Use the firmware boot menu to select the USB. On the initial test laptop, the vendor documents Esc followed by F9 for boot options. See [HP's boot instructions](https://www.hp.com/au-en/tech-takes/software/how-to/how-to-boot-from-usb-drive-on-windows-10-pcs.html). Secure Boot was already disabled on the inspected development machine; the preview loader is unsigned and the build does not change firmware settings.

Choose the MainFrameOS USB preview entry. If graphical startup fails, use the troubleshooting console entry. Test display, keyboard, touchpad and networking first, then peripherals and power behavior. Save results with the build ID. Shut down and remove the USB to return to the internal installation.

Android and Windows application integration, internal audio routing, hardware video decoding, an internal disk installer, signed releases and recovery updates remain unfinished. The compiled kernel is staged by the development image builder; production kernel packaging and update integration remain required before a supported release. Do not treat the USB as a daily use installation.

## Recorded build result

The kernel, modules, device tree and 16 GiB disk image were built successfully on 2026-09-23. GRUB configuration, GPT structure, ext4 consistency and required early boot files passed inspection. The isolated ARM virtual machine mounted the actual image root, passed its system check and powered off cleanly. Physical laptop boot remains untested. See the [build record](evidence/2026-09-23/usb-preview.json).
