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
  with SSID `MainFrameOS-VR`, a generated private password, no internet sharing and
  no boot-time hotspot autostart. Original config is backed up root-only at
  `/var/lib/vr-hotspot/config.before-frame-dongle.json`.
- Laptop uplink/default route stayed on the built-in adapter.
- 6 GHz PC AP was not attempted: the driver reports no-IR channels. The observed
  Valve direct-link design instead has the headset host the AP; joining it as a
  client requires a separate pairing/control implementation.

No SteamOS performance parity, improvement, complete Steam-independent headset
runtime, or general distro support is claimed. Association/DHCP, latency/throughput,
replug and sleep qualification are separate from successful AP startup. The
VRhotspot diagnostic and portability notes are maintained upstream.

## Rollback

Stop the VRhotspot hotspot first. Restore only the backed-up VRhotspot config if
needed, then unload `rtw89_8852cu`, `rtw89_8852c`, `rtw89_usb`, `rtw89_core` once no
interface uses them. Remove only the four added modules/directory and run `depmod -a`
for the exact kernel. The built-in Wi-Fi and Frame Control service remain separate.
The live country request resets on reboot unless another service reapplies it;
configure the real location through normal distro mechanisms, never by bypassing
regulatory enforcement.
