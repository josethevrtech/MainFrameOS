#!/bin/bash
# Child desktop for an existing Wayland host (e.g. WayVR's compositor).
# Run inside an isolated lab or MainFrameOS session, not as a login-manager replacement.
set -euo pipefail
[[ $# == 1 && -n ${WAYLAND_DISPLAY:-} && -n ${XDG_RUNTIME_DIR:-} ]] || {
 echo 'Usage: desktop-session.sh cosmic inside an existing Wayland session' >&2; exit 2;
}
export XDG_SESSION_TYPE=wayland QT_QPA_PLATFORM=wayland GDK_BACKEND=wayland
case "$1" in
 cosmic)
  export XDG_CURRENT_DESKTOP=COSMIC XDG_SESSION_DESKTOP=COSMIC COSMIC_BACKEND=winit WINIT_UNIX_BACKEND=wayland
  unset DISPLAY
  exec dbus-run-session -- cosmic-session
  ;;
 *) echo "Unsupported desktop profile: $1" >&2; exit 2;;
esac
