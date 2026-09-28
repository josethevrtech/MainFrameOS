# Laptop keyboard/touchpad to native headset apps

An opt-in development utility forwards input from a focused SDL3 laptop window
to two ephemeral Linux uinput devices on the Frame over authenticated SSH. It
controls apps running on the Frame, not a remotely streamed laptop desktop.
No Bluetooth pairing, screen capture, root daemon or listening network socket
is added. Input content is not logged. Code is original MainFrameOS glue under
the repository MIT license; SDL and Linux interfaces retain their own licenses.

## Build and launch

Use a development environment with a C compiler, SDL3 headers/library (3.2.12 or
newer) and pkg-config. The receiver needs Python 3, Linux uinput and an existing
account permitted to open `/dev/uinput`. Do not broaden permissions globally.

```sh
cc -Wall -Wextra -Werror -O2 client.c -o frame-input-client $(pkg-config --cflags --libs sdl3)
# Copy receiver.py to a user-owned directory on the target, then:
./frame-input-client /path/to/ssh-key USER@HOST /absolute/remote/path/receiver.py
```

Verify the target's SSH identity beforehand; the client requires a known host key
and an existing key-based login. Use a remote script path without whitespace or
shell metacharacters (SSH passes the remote command through its shell). Arguments
are supplied by the local owner, not accepted from a network endpoint.

The window starts with capture **off**. Once Ready, click or press Space to start.
**Ctrl+Alt+Escape**, window focus loss or closing releases local capture and sends
release-all to the target. The client checks receiver acknowledgements; the
receiver destroys both devices on EOF or after three seconds without traffic.
Nonblocking writes stop capture when the SSH pipe cannot accept more input.

Physical key positions are mapped to Linux evdev codes; the target's keyboard
layout controls characters. Relative pointer motion, left/right/middle/side
buttons and horizontal/vertical scroll are supported. Multitouch gestures and
firmware-handled Fn actions are not transported. Compositor-reserved shortcuts
may remain local. This is not a clipboard-sharing service or seamless edge-switch
KVM. Only explicit capture in the control window sends input.

## Observed validation and remaining gate

On the development laptop, compiled against existing SDL 3.4.16 with warnings
as errors. No development packages were installed. The Frame stock account
already had uinput access. Its kernel and udev recognized separate keyboard and
mouse devices. SSH startup, heartbeat and automatic device removal after traffic
stopped passed. Protocol tests cover routing, rejection, release and duplicate
key-down handling. The GUI is running without capturing until the owner starts it.

Native Frame app clicking/typing and emergency-return usability still require
owner confirmation. Device enumeration is not proof of headset usability. This
is a standalone developer utility, not an isolated distribution package build,
a new OS image or a certified feature. The stock partition and XR session are
unchanged. No auto-start entry is installed.

For the recorded local setup, source and executable are in the task's private
`outputs/frame-input-bridge` directory, with a laptop application-menu entry named
**Control Steam Frame**. The receiver is in the shared home development directory.
Closing the app removes its virtual devices; remove those user-owned files and
the application-menu entry to uninstall. No system configuration rollback needed.

References: [Linux uinput](https://docs.kernel.org/input/uinput.html),
[SDL relative input](https://wiki.libsdl.org/SDL3/SDL_SetWindowRelativeMouseMode),
[SDL keyboard grab](https://wiki.libsdl.org/SDL3/SDL_SetWindowKeyboardGrab).
