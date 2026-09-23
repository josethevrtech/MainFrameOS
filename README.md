# MainFrameOS

**Arch Linux ARM for productivity on Snapdragon laptops and headsets.**

MainFrameOS is being developed by **josethevrtech** for Snapdragon laptops and headsets, with one installer that configures the system for supported hardware.

The goal is a desktop for everyday work, with current software, reliable recovery and support for native Linux, Android and selected Windows applications. The focus is large screens, keyboard and mouse use, docking and productivity. Gaming is optional.

**Status: early development. A personal USB desktop preview has been built and passed an ARM virtual boot test. Physical hardware validation is pending. A general installer and public release are not yet available.** Initial development uses an existing Snapdragon laptop as a test machine; that machine does not define the product scope.

## One installer for Snapdragon laptops and headsets

The goal is a shared ARM64 installer that detects supported hardware and selects the appropriate kernel, firmware, boot setup and configuration. New devices should join the same distribution through maintained hardware profiles, without requiring a separate MainFrameOS edition for each laptop.

Snapdragon generations and manufacturers are candidates according to upstream Linux support, boot access and available testing. The developer's current laptop is the first test platform, not an exclusive target or a requirement for contributors.

Headsets share the same product and installation framework, with boot and recovery adapters for each platform and an XR session where needed. A common installer does not imply that every headset can boot a USB image or use a laptop's partition layout. No device has certified support in a MainFrameOS release yet.

See the [unified installer design](docs/INSTALLER.md), [hardware support policy](docs/HARDWARE-SUPPORT.md) and [Qualcomm Linux enablement tracking](docs/QUALCOMM-LINUX.md).

See [USB preview instructions and limitations](docs/USB-PREVIEW.md) for the current test build.

## Build and maintenance

The product base is **Arch Linux ARM**, independent of SteamOS. Collabora's preview is integrated selectively as pinned source recipes rebuilt in the ALARM toolchain.

```sh
make check             # Offline contract and unit checks
make bootstrap         # Native ARM64; verified ALARM bootstrap + rootless Podman builder
make package-support   # Build MainFrameOS hardware identification package
make package-canary    # Compile/test the imported Collabora json-c recipe
make kernel-dtb        # Compile the initial test-platform device tree; does not install it
```

See [Build instructions](docs/BUILD-AND-PACKAGING.md), [Engineering contract](docs/ENGINEERING.md), [Collabora integration](docs/COLLABORA-INTEGRATION.md), [Build evidence](docs/BUILD-EVIDENCE.md), [Support](SUPPORT.md), and [Security](SECURITY.md). Builds are isolated from the running OS. Generated packages are unsigned development artifacts.

## Proposed experience

- KDE Plasma on Wayland, opening directly into a productive desktop.
- ARM64 native packages and Flatpaks for the primary application experience.
- Android applications through an integrated Waydroid environment.
- Selected Windows `.exe` applications through Wine and FEX CPU translation.
- Frequent, tested updates, with a previous system deployment available for recovery.
- Device-specific settings and fixes packaged reproducibly rather than applied by hand.
- A clear compatibility record for each device and application version.

Android and Windows compatibility are development targets, not universal compatibility promises. Flatpak applications also need an appropriate architecture build.

## Documentation

| Document | Contents |
| --- | --- |
| [Vision and scope](docs/VISION.md) | Product direction, priorities and first-release boundaries |
| [Architecture](docs/ARCHITECTURE.md) | Base system, desktop, hardware profiles and application layers |
| [Hardware support](docs/HARDWARE-SUPPORT.md) | Platform coverage, configuration profiles and test evidence |
| [Hardware support policy](docs/HARDWARE-SUPPORT.md) | What similar means and how devices become supported |
| [Applications](docs/APPLICATIONS.md) | Native, Flatpak, Android and Windows strategy |
| [Updates and recovery](docs/UPDATES-AND-RECOVERY.md) | Release channels, complete deployments and rollback |
| [Build and packaging plan](docs/BUILD-AND-PACKAGING.md) | Repeatable builds, proposed packages and source provenance |
| [Roadmap](docs/ROADMAP.md) | Milestones, acceptance criteria and initial work items |
| [Test plan](docs/TEST-PLAN.md) | Hardware and productivity validation |
| [Decisions](docs/DECISIONS.md) | Agreed scope, proposed choices and unresolved decisions |
| [Upstream references](docs/UPSTREAM.md) | Primary technical sources |

## First milestone

Build the shared installer and Arch Linux ARM desktop, using the available laptop for the first end-to-end test. Add supported Snapdragon configurations through the same profile system. Demonstrate representative Flatpak, Android and Windows workflows, then validate headset installation and XR workflows as hardware access permits.

MainFrameOS is an independent project. Arch Linux ARM, Arch Linux, Valve/SteamOS, Qualcomm, device manufacturers, KDE and other upstream projects retain their own identities and licenses. The working name does not imply affiliation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for evidence and contribution expectations.
