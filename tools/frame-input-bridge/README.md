# Laptop keyboard/touchpad to native headset apps

The KDE user service registers an explicit F11 toggle and otherwise stays idle.
On the tested laptop, the owner confirmed **Fn+F11** starts control of native
Frame apps and the same combination returns to the laptop. Fn is handled by
keyboard firmware; the actual shortcut is F11, so Fn Lock can change the physical
combination. F11 is reserved while this shortcut service runs.

The service starts an SDL3 capture worker only on demand. A compact borderless
status strip replaces the earlier large window; it remains a focused capture
surface while active, not a fully windowless input-capture backend. On return,
the strip closes and KDE shows a brief “Laptop control” OSD. Ctrl+Alt+Escape,
focus loss and closing the worker also release capture. The normal window mode
remains available when `MAINFRAMEOS_INPUT_OVERLAY` is unset.

## Components

- `controller.cpp`: Qt6/KDE GlobalAccel user service; D-Bus toggle/status interface,
  one child at a time, activation debounce, connection-result OSD and bounded stop.
- `client.c`: SDL3 input capture; physical keys map to evdev codes; relative motion,
  buttons and horizontal/vertical scroll are sent through existing key-authenticated
  SSH with strict host-key checking. Nonblocking writes stop capture on backpressure.
- `receiver.py`: two ephemeral uinput devices. Releases held input and destroys devices
  on EOF or after three seconds without traffic. No text/pointer history is logged.

The service opens no headset connection while idle and adds no network listener.
It uses the target account's existing uinput permission; do not broaden permissions
globally. No root service or boot change is required. Firmware Fn actions,
multitouch gestures, clipboard sharing and automatic screen-edge switching are
not implemented. Some compositor-reserved shortcuts may remain local; target
keyboard layout controls characters.

## Build and installation

The Arch/ALARM `build.sh NEW_OUTPUT_DIRECTORY` helper uses already installed SDL3
(3.2.12+), Qt6 Widgets/DBus and KF6 GlobalAccel development files. It installs
nothing. The recorded native ARM64 build used these compiler commands with
warnings as errors. A CMake recipe is also supplied but was not run in this
validation environment, where CMake was unavailable.

Install the two binaries under `~/.local/lib/mainframeos-frame-control/`, and the
provided unit under `~/.config/systemd/user/`. Put the target-specific connection
configuration at `~/.config/mainframeos-frame-control/connection.json`:

```json
{
  "identity": "/absolute/path/to/existing/ssh-key",
  "target": "USER@HOST",
  "receiver": "/absolute/remote/path/receiver.py"
}
```

Copy `receiver.py` to that remote path. Verify the target host key first. Use a
remote path without whitespace or shell metacharacters because SSH invokes a
remote shell. These arguments are owner-controlled, not network-provided inputs.

```sh
systemctl --user daemon-reload
systemctl --user enable --now mainframeos-frame-control.service
qdbus6 org.mainframeos.FrameControl /Control org.mainframeos.FrameControl.Toggle
qdbus6 org.mainframeos.FrameControl /Control org.mainframeos.FrameControl.Status
```

The menu launcher should start the service, then call Toggle. The unit is tied
to `graphical-session.target` and runs as the logged-in user. It registers the
shortcut through KDE rather than modifying other applications' shortcuts.

## Validation and rollback

The owner confirmed native Frame pointer/click/type operation and Ctrl+Alt+Escape
on the original client after restoring a missing receiver. SSH delivery of Shift
press/release and relative motion was independently observed through only the
new virtual devices. Receiver timeout cleanup and protocol tests passed.

The new service's automatic activation test reported `controlling-frame`, then
`idle` after release. The owner confirmed both Fn+F11 presses and Frame control
work. Login startup is enabled, but a fresh logout/login remains untested. No
isolated distribution package, OS image, general keyboard/layout compatibility or
long-term reliability is claimed. The receiver is unchanged by this upgrade.

Disable with `systemctl --user disable --now mainframeos-frame-control.service`.
Remove only its user files and unregister `toggle-frame-control` from the
`mainframeos-frame-control` KDE component to uninstall. The device installation
keeps the previous window launcher/binary in a private `legacy/` backup with a
rollback helper. Do not overwrite the entire KDE shortcut configuration.

Code is original MainFrameOS glue under the repository MIT license. SDL, Qt/KDE
and Linux interfaces retain their own licenses. References:
[Linux uinput](https://docs.kernel.org/input/uinput.html),
[SDL relative input](https://wiki.libsdl.org/SDL3/SDL_SetWindowRelativeMouseMode),
[KDE GlobalAccel](https://api.kde.org/kglobalaccel.html).
