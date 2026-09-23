# Vision and scope

## Purpose

Make supported Snapdragon laptops and headsets useful as modern Linux workstations: office work, browsers, coding, communications, media, creative applications and large-screen multitasking. Give applications a consistent place in the desktop regardless of their runtime, while making compatibility limitations visible.

The SteamOS inspiration is its integrated system experience and recoverability. MainFrameOS should use an independent Arch Linux ARM foundation and a desktop-first session. A gaming launcher is not the primary interface.

## Priorities, in order

1. Build one installation framework with reliable boot, graphics, input, networking and recovery across supported Snapdragon configurations.
2. Make audio, docking, screen sharing, suspend and battery behavior suitable for daily productivity.
3. Deliver a current, internally consistent desktop and application environment.
4. Integrate Android and selected Windows workflows without hiding compatibility failures.
5. Make builds, device configuration and update behavior repeatable.
6. Expand only when additional physical devices can be tested.

## MainFrameOS 0.1

Deliver a shared installer prototype, first exercised on the available test laptop, with a Plasma Wayland desktop, working ARM64 Flatpaks, an Android proof of concept, and a small Windows application compatibility record. Device profiles are implementation details within one distribution; the product is not restricted to the first machine. Publish an image manifest, documented installation/recovery approach and an honest list of remaining limitations.

An Android or Windows blocker discovered during prototyping must be documented and explicitly reflected in release scope. Do not silently remove either long-term application goal or advertise it as complete.

## Deferred scope

A release-ready standalone VR experience, universal `.exe` compatibility, a custom desktop compositor, a custom app store backend, mandatory gaming components, and NPU-dependent core functionality are not first-release requirements.

Snapdragon laptops and headsets are the product scope; different Snapdragon generations are evaluated on upstream readiness and test access. For VR, the productivity goal includes large virtual displays and spatial workspaces. First prove boot access, graphics and tracking on a named headset; then select an XR session. A laptop-to-headset streaming workflow is a different deliverable from replacing a headset's operating system.

## Success measures

- Document time from upstream fixes to tested MainFrameOS updates.
- Measure idle drain, fixed-workload battery use, resume behavior and application responsiveness on the same machine.
- Count completed user workflows rather than installed packages.
- Record recovery results after intentionally interrupted or failed updates.
- Track the number and maintenance cost of downstream patches.

“More up to date than SteamOS” is a product objective. The existing local port uses its own package snapshot and custom kernel; it cannot establish a blanket comparison with all SteamOS releases.
