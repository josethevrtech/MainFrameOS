# VRhotspot in MainFrameOS

VRhotspot is the local networking and headset-control component for MainFrameOS.
The development laptop now has a native ARM64 backend, a GTK4/WebKit desktop
companion, and the optional Frame Control tray integration. It appears as **VR
Hotspot** in the application menu. This is a local development installation;
future MainFrameOS images still need an isolated ALARM package and image inclusion.

## Source and architecture

`upstream/vrhotspot.lock.json` pins the source archive, immutable upstream commit,
archive hash, and Frame Control patch hash. The ARM build uses the upstream
`tools/arm64/build.py` recipe. Its source hashes, hostapd configuration, output hashes
and linkage receipt are retained with the local artifact. No prebuilt binaries,
credentials or personal state are imported here. VRhotspot project code is MIT;
hostapd, dnsmasq, linux-router and dependencies retain their own license obligations.

- Root system service: hotspot network operations and loopback management API.
- User desktop process: paired through the Secret Service wallet, without root.
- Separate user Frame Control service: F11 toggle, SSH and ephemeral uinput devices.
  The root networking daemon does not acquire SSH keys or capture input.

## Installed development layout

| Path | Purpose |
| --- | --- |
| `/var/lib/vr-hotspot/app` | Pinned application source plus Frame Control patch |
| `/var/lib/vr-hotspot/venv` | Private backend Python environment |
| `/opt/mainframeos/vrhotspot-arm64` | Root-owned native network binaries and receipt |
| `/etc/vr-hotspot/env` | Root-only token, loopback bind and native bundle selection |
| `/etc/systemd/system/vr-hotspotd.service` | Enabled backend service |
| `/usr/local/bin/vrhotspot` | Native user desktop launcher |
| `/usr/local/share/applications/io.github.josethevrtech.VRhotspot.desktop` | Menu entry |

Runtime dependency `webkitgtk-6.0` was installed from Arch Linux ARM using the
existing package database; no development packages, OS upgrade or boot changes were
needed. GTK4, PyGObject, libsecret, network tools and native build libraries were
already present. The backend installer builds a private Python environment; it does
not replace system Python packages.

The service is enabled, but hotspot autostart is disabled. The API listens only on
127.0.0.1 and has a random token stored root-only; the desktop's copy is held in the
user wallet. Desktop launch is through the menu rather than an automatic popup at
login. Radio activation remains an explicit action in VRhotspot.

## Evidence and remaining work

Native binaries passed architecture, version and linkage checks, a loopback DNS
query succeeded, and backend health plus secure desktop pairing passed. The GTK
process and sandboxed WebKit renderer started successfully. The combined upstream
changes are separately covered by PRs 153 and 154; upstream CI passed before this
installation. The home Wi-Fi connection stayed active. The owner confirmed that both the main interface and system tray appear.

Live AP start/stop, headset DHCP association, offline Fn+F11 operation and regulatory
band/channel qualification remain untested. Managed Android Platform-Tools are
still x86-only. Do not present this component as a certified hotspot or a completed
MainFrameOS image package. Before release, build the networking and app packages
in the pinned ALARM builder, retain source/license artifacts, and add them to the
shared installer/image profile. Do not copy this developer OS as the image input.

## Rollback

Quit the desktop companion. Disable and stop `vr-hotspotd.service` and
`vr-hotspot-autostart.service`. Remove only the documented VRhotspot launcher,
menu/icons, service units and native bundle when no process uses them. Preserve
`/etc/vr-hotspot` and `/var/lib/vr-hotspot` as a private backup if settings are wanted;
they contain credentials. Reload systemd afterward. Clear only VRhotspot's wallet
credential through the companion before uninstalling if desired. Keep Frame Control
and other applications untouched. The WebKit runtime can remain for other apps.

## Frame USB adapter

[Frame dongle bring-up](FRAME-DONGLE.md) records the separate driver deployment,
5 GHz AP/start-stop evidence, rollback and pending direct-link/performance work.
