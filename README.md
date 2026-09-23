# MainFrameOS

**A productivity-first Arch Linux ARM distribution for Snapdragon computers.**

Developed by **josethevrtech**, MainFrameOS is intended to unify computers and XR devices into one ecosystem, starting with a focused laptop foundation.

MainFrameOS aims to combine a polished, integrated desktop with current software, dependable recovery, and native Linux, Android, and selected Windows applications. Large screens, keyboard and mouse workflows, docking, and everyday productivity come first. Gaming is optional.

**Status: design and hardware-baseline stage. No MainFrameOS installer or release image exists yet.** The current reference machine runs a custom experimental ARM SteamOS port. Its successful hardware work informs this project; it is not a MainFrameOS release.

## Initial hardware focus

The first target is the **HP OmniBook 5 Laptop 16-bf0xxx, board 8E33**. The inspected reference system has eight Qualcomm Oryon cores, an Adreno X1-45 GPU recorded by its previous Vulkan check, and device-tree compatibility `qcom,x1p42100`.

Initial expansion is limited to closely related Snapdragon laptops after individual validation. Matching a chip family is insufficient for support: boot firmware, device trees, displays, audio wiring, embedded controllers and power behavior can differ.

Snapdragon PCs and standalone VR headsets remain part of the longer-term vision. They are outside the first release's support commitment.

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
| [Reference laptop](docs/hardware/HP-OMNIBOOK-5-16-BF.md) | Observed hardware, existing fixes and validation gaps |
| [Hardware support policy](docs/HARDWARE-SUPPORT.md) | What similar means and how devices become supported |
| [Applications](docs/APPLICATIONS.md) | Native, Flatpak, Android and Windows strategy |
| [Updates and recovery](docs/UPDATES-AND-RECOVERY.md) | Release channels, complete deployments and rollback |
| [Build and packaging plan](docs/BUILD-AND-PACKAGING.md) | Repeatable builds, proposed packages and source provenance |
| [Roadmap](docs/ROADMAP.md) | Milestones, acceptance criteria and initial work items |
| [Test plan](docs/TEST-PLAN.md) | Hardware and productivity validation |
| [Decisions](docs/DECISIONS.md) | Agreed scope, proposed choices and unresolved decisions |
| [Upstream references](docs/UPSTREAM.md) | Primary technical sources |

## First milestone

Produce a repeatable Arch Linux ARM desktop image for the reference OmniBook that preserves its useful hardware behavior. Then demonstrate representative Flatpak, Android and Windows workflows before broadening device support.

MainFrameOS is an independent project. Arch Linux ARM, Arch Linux, Valve/SteamOS, Qualcomm, HP, KDE and other upstream projects retain their own identities and licenses. The working name does not imply affiliation.

See [CONTRIBUTING.md](CONTRIBUTING.md) for evidence and contribution expectations.
