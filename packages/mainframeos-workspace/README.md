# Replaceable desktop session for the OpenXR workspace

COSMIC is the owner's intended MainFrameOS desktop. Plasma is the initial XR
integration and recovery baseline. Neither compositor owns the headset directly
in this design: Monado owns XR presentation/tracking, a workspace bridge presents
Wayland surfaces, and the selected desktop runs as a nested Wayland client.

`desktop-session.sh cosmic` is the child entry point for a Wayland host.
It uses a separate session bus and does not install a login-manager session or
change a default runtime. Launch it from the workspace bridge inside an isolated
lab, with the parent's `WAYLAND_DISPLAY` and a private `XDG_RUNTIME_DIR`.

The COSMIC child uses the winit backend and cosmic-session. The existing Plasma
recovery session remains separate; the unsuccessful experimental KWin child is
not included as a supported launcher. The session must have its expected graphics services;
the Frame lab required the system bus and host PID namespace for working graphics.
Its user/session bus stays separate from the host desktop. System integration,
portals and app launch behavior still require independent testing.

Candidate bridge: [WayVR](https://github.com/wayvr-org/wayvr), pinned in
`upstream/workspace.lock.json`. Build features are `openxr,wayland,x11` with default
features disabled. The project and dependencies retain their upstream licenses.
The upstream source/vendor trees are not copied into this repository.

Nested desktop validation is not an OpenXR workspace validation. Headset tracking
currently uses the separately documented experimental vendor-backed provider.
Controller support must not be inferred from a working mouse inside a nested window.
