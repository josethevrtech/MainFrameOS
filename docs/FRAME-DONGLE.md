# Steam-independent Frame USB networking: development evidence

Valve device `28de:2432` enumerated at USB SuperSpeed 5000 Mb/s but had no network
interface. The running `7.1.13-mainframeos-regulator1` configuration disabled RTW89.
Its matching source already supported the exact USB ID, so four additional native
modules were compiled separately and loaded without changing the kernel image,
initramfs, bootloader or existing built-in Wi-Fi driver.

Source: `https://github.com/jglathe/linux_ms_dev_kit`, immutable revision
`8a4f6449525101e3445d33d642d6b1927f2fba3b`, as pinned by the existing kernel source
lock. Driver files came from `drivers/net/wireless/realtek/rtw89`; retain their
GPL-2.0 OR BSD-3-Clause licensing. No driver source modification or USB ID override
was needed. Existing firmware `rtw89/rtw8852c_fw-2.bin` loaded version 0.27.129.4;
no firmware was copied into this repository.

The module build used a private copy of that driver directory and the matching
prepared kernel build tree with its original configuration and Module.symvers:

```sh
make -C /lib/modules/"$(uname -r)"/build M=/absolute/private/rtw89 \
  CONFIG_RTW89_CORE=m CONFIG_RTW89_USB=m \
  CONFIG_RTW89_8852C=m CONFIG_RTW89_8852CU=m -j4 modules
```

Vermagic matched the running kernel. Deployment installed only `rtw89_core.ko`,
`rtw89_usb.ko`, `rtw89_8852c.ko` and `rtw89_8852cu.ko` under
`/lib/modules/7.1.13-mainframeos-regulator1/updates/mainframeos-frame-dongle/`, followed
by `depmod -a` and `modprobe rtw89_8852cu`. As external modules they mark the kernel
out-of-tree-tainted; this is not a signed distribution module package. They apply
only to this kernel ABI and must not be copied to another kernel or distro.

`upstream/vrhotspot/frame-dongle.config` records the desired future kernel options.
It is not silently applied to a release image; merge it in the isolated kernel
build, resolve Kconfig dependencies, and rerun device tests when packaging updates.
Normal module USB aliases provide discovery for the current kernel on replug/boot;
replug, fresh boot and suspend/resume have not yet been qualified.

## Results and actual scope

- Bound driver `rtw89_8852cu`; new USB interface appeared without Steam.
- Owner confirmed US location; live regulatory request changed from unset to US.
  No fixed worldwide region override was installed.
- Native hostapd: 5 GHz channel 36, 80 MHz, Wi-Fi 6 AP startup passed after releasing
  NetworkManager's ownership. An earlier immediate handoff failed and hostapd crashed
  during cleanup. The normal VRhotspot lifecycle then started/stopped successfully.
- VRhotspot inventory recommended the USB adapter; configuration selects it explicitly,
  with owner-selected SSID/password, internet sharing enabled and
  no boot-time hotspot autostart. Original config is backed up root-only at
  `/var/lib/vr-hotspot/config.before-frame-dongle.json`.
- Laptop uplink/default route stayed on the built-in adapter.
- 6 GHz PC AP was not attempted: the driver reports no-IR channels. The observed
  Valve direct-link design instead has the headset host the AP; joining it as a
  client requires a separate pairing/control implementation.

No SteamOS performance parity, improvement, complete Steam-independent headset
runtime, or general distro support is claimed. The owner confirmed client association during the initial offline test. DHCP/internet, latency/throughput,
replug and sleep qualification are separate from successful AP startup. The
VRhotspot diagnostic and portability notes are maintained upstream.

## Rollback

Stop the VRhotspot hotspot first. Restore only the backed-up VRhotspot config if
needed, then unload `rtw89_8852cu`, `rtw89_8852c`, `rtw89_usb`, `rtw89_core` once no
interface uses them. Remove only the added driver modules and the separately added `xt_MASQUERADE.ko` and run `depmod -a`
for the exact kernel. The built-in Wi-Fi and Frame Control service remain separate.
The live country request resets on reboot unless another service reapplies it;
configure the real location through normal distro mechanisms, never by bypassing
regulatory enforcement.

The upstream hostapd version probe was also corrected: missing feature labels are
unknown, not proof of missing HE/SAE. The installed preflight module was updated,
with its prior copy preserved at `/var/lib/vr-hotspot/preflight.before-frame-dongle.py`.
VRhotspot subsequently started the dongle with Wi-Fi 6 enabled at 5 GHz/80 MHz.
Client association was confirmed by the owner; negotiated rates and throughput have not been qualified.

## Internet sharing repair

The initial offline test deliberately omitted routing. Internet sharing was then
requested by the owner. The first routed start failed with iptables reporting
`Extension MASQUERADE revision 0 not supported` and `RULE_INSERT failed`.
The running kernel provided native nftables masquerading but omitted the
`CONFIG_NETFILTER_XT_TARGET_MASQUERADE` compatibility module used by this lnxrouter
installation. This was a host kernel prerequisite, not a wireless width failure,
although the backend's final reported error incorrectly pointed to AP width.

Built the unchanged `net/netfilter/xt_MASQUERADE.c` from the same immutable kernel
source above (GPL), in a private directory with `obj-m += xt_MASQUERADE.o`:

```sh
make -C /lib/modules/"$(uname -r)"/build M=/absolute/private/nat modules
sudo install -m 0644 /absolute/private/nat/xt_MASQUERADE.ko \
  /lib/modules/"$(uname -r)"/updates/mainframeos-frame-dongle/
sudo depmod -a
sudo modprobe xt_MASQUERADE
```

A masquerade rule insertion passed in a disposable network namespace. After
stopping the daemon, reloading `rtw89_8852cu` cleared a queue-flush timeout from the
failed attempts. Restarting the daemon and hotspot succeeded. Verified IPv4
forwarding enabled, subnet-scoped masquerading and forwarding rules, and DHCP/DNS
input allowances. UFW remains active and the laptop's home Wi-Fi remains its
default route. The owner confirmed headset internet and Frame Control both work through the hotspot.

The config persists `enable_internet=true`; hotspot autostart remains disabled.
The compatibility module applies only to the current kernel ABI; a future image
must include the corresponding Kconfig option. To roll back only internet sharing,
set `enable_internet=false` through VRhotspot and restart the hotspot; its managed
NAT rules are removed on stop. Stop the hotspot before removing the added module
and running `depmod -a`. No boot artifacts were replaced.

## Latency qualification and 6 GHz blocker (2026-09-29)

The owner enabled the backed-up and validated `steamos` passwordless sudo rule.
Before changing Wi-Fi power saving, 100 idle ICMP probes on channel 36/80 MHz
averaged 51.353 ms (maximum 323.505 ms, zero loss). After the following narrowly
scoped change, another 100 probes averaged 3.026 ms (maximum 8.355 ms, zero loss):

```sh
sudo nmcli connection modify VR-Hotspot 802-11-wireless.powersave 2
sudo iw dev wlan0 set power_save off
```

The saved connection previously used value 0/default. Rollback is the same nmcli
command with value 0; `sudo iw dev wlan0 set power_save on` restores the observed
previous live state. Other saved Wi-Fi connections are unchanged. Disabling power
saving can increase headset power consumption while this profile is active.

An eight-second single TCP stream using in-memory Python buffers measured
473.02 Mb/s PC-to-Frame and 253.60 Mb/s Frame-to-PC after the change. Concurrent
ICMP averages were 6.915 ms and 10.692 ms respectively, with no packet loss.
These are short sequential diagnostics, not an iperf certification or a controlled
Valve comparison. Channel 149/80 MHz was tested twice earlier and regressed the
PC-to-headset direction (194.66 and 169.73 Mb/s versus 470.68 Mb/s on channel 36),
so channel 36 was restored. Do not prescribe this channel globally.

The headset's dedicated AP was observed using 6 GHz channel 37/160 MHz, WPA3-SAE,
mandatory protected management frames and a hidden SSID. A temporary client-mode
NetworkManager profile failed to associate. A second guarded test temporarily
made the headset AP name visible using hostapd's runtime control socket. Discovery
then succeeded, but wpa_supplicant authentication requests failed and mac80211 logged
`failed to insert STA entry for the AP (error -22)`. The failure needs driver/kernel
diagnosis; it is not evidence that the pairing password was wrong or that regulatory
restrictions should be bypassed. Independent recovery timers were established on
both machines; the headset hidden-SSID setting and PC hotspot were restored and the
temporary pairing profile and credential file removed. No persistent headset AP
configuration or firmware was modified.

The current product remains a 5 GHz PC-hosted hotspot. A complete 6 GHz client/direct
mode still needs validated association, routing, secure pairing, reconnect and
rollback. Valve's [Multi-Link and foveated streaming](https://store.steampowered.com/hardware/steamframe)
are streaming-application features, not generic hotspot toggles. No performance
parity or improvement over Valve's complete implementation is claimed.

## Upstream driver fix and successful direct-link test

The preceding 6 GHz blocker was resolved on this development kernel by upstream
Linux commit `bf4a37f516f0382832c10a9d04414944d0d96591` (Realtek authors): USB devices
must not depend on internal-card ACPI capability checks. In the older driver, US/CA
VLP was denied without ACPI opt-in; the Frame AP advertises VLP. The unmodified
upstream patch applies cleanly to the pinned kernel source. Its exact patch,
attribution and SHA-256 are under `upstream/vrhotspot/patches/0002-rtw89-usb-acpi.*`.
This is not a regulatory-domain override; normal cfg80211 and power constraints
remain. It does not enable a 6 GHz PC AP on no-IR channels.

Built a separate copy of the rtw89 sources with the same four-module command above,
after `patch -p6 < 0002-rtw89-usb-acpi.patch`. Preserved prior modules in root-owned
`/var/lib/vr-hotspot/module-backups/pre-usb-acpi/`. With the hotspot stopped, unloaded
those four modules, installed the patched modules in the existing updates directory,
ran `depmod -a`, and loaded `rtw89_8852cu`. An independent timed module rollback was
armed before replacement. No kernel image, bootloader or firmware was replaced.

Physical result: WPA3-SAE association and DHCP succeeded at 6135 MHz, channel 37,
160 MHz. Reconnection succeeded with the original hidden SSID restored and a hidden
NetworkManager profile. Initial PHY rate was 1921.5 Mb/s. Eight-second TCP samples
measured 1017.81 Mb/s PC-to-Frame and 423.77 Mb/s reverse. Concurrent ICMP averages
were 17.819/19.479 ms, maxima 99.349/99.959 ms, zero loss. Wider channels increased
throughput in these samples but did not improve loaded latency. Do not claim parity
with Valve without a controlled streaming comparison.

The normal 5 GHz hotspot was restored, and the patched modules retained. To undo
the driver update: stop the hotspot, unload `rtw89_8852cu rtw89_8852c rtw89_usb
rtw89_core`, reinstall only the four backed-up modules to the exact kernel's updates
directory, `depmod -a`, reload `rtw89_8852cu`, and restart the hotspot. Kernel updates
need their own compatible build. Shipping desktop pairing, direct-mode lifecycle,
internet relay and Frame Control route selection remains separate integration work;
the current default still uses the validated PC-hosted hotspot.
