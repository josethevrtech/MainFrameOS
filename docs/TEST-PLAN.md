# Acceptance test plan

Record board, firmware version, image/build ID, kernel, DTB hash, graphics/runtime versions, date, result and evidence. Use pass, limited, fail or untested. Repeat tests when relevant components change; do not run destructive failure tests on the only working installation.

## Core device checks

| Area | Procedure | Passing evidence |
| --- | --- | --- |
| Cold boot | Boot repeatedly with and without the dock | Reach usable desktop, no recovery intervention |
| Graphics | Verify hardware renderer and exercise desktop plus app workloads | Hardware acceleration, correct output, no reproducible hangs |
| Input | Keyboard, touchpad, gestures and connected peripherals | Consistent input before/after suspend |
| Storage | Read/write workload, normal shutdown and reboot | Data retained and filesystems clean |
| Displays | Internal-only, docked, unplug/replug, scaling, refresh and lid scenarios | Usable picture and correct layout after transitions |
| Audio | Speakers, DP/HDMI, microphone, idle/resume and headphone switching | Physical playback/capture, no unintended route loss |
| Network | Wi-Fi/Bluetooth reconnect after sleep and ordinary workloads | Reliable connectivity without manual recovery |
| Webcam | Browser call and capture application | Actual frames and usable microphone routing |
| Suspend | At least ten initial cycles plus an overnight test | Reliable resume; measured drain and reported anomalies |
| Power | Compare idle and fixed workload in each supported profile | Recorded performance/energy/thermal behavior |
| Battery | Telemetry and charge-limit persistence | Consistent readings and verified limit behavior |
| Printing | Print/scan with the selected peripheral when in scope | Physical output/capture |

Ten cycles is an initial project test target, not proof of long-term reliability. Document the adapter, monitor and peripherals used, without publishing unique serials.

## Productivity workflows

1. Open, edit, save and reopen an office document; export a PDF.
2. Browser video call with camera, microphone and screen sharing.
3. Record desktop and audio, then play the recording.
4. Edit a file/project, use the terminal and complete a development task.
5. Use multiple windows and an external monitor through dock/suspend transitions.
6. Run representative ARM64 Flatpak, Android and Windows workflows using the [compatibility record](APPLICATIONS.md).

## Recovery checks

On disposable storage or a designated test installation: reject invalid signatures/corrupt artifacts, handle insufficient space, interrupt an update, simulate unsuccessful trial boot, boot the prior deployment and verify user files persist. Check that configuration migrations do not make the previous deployment unusable.

## Reporting regressions

Record the last known-good build, first failing build if known, shortest reproduction, expected/actual behavior and whether the issue also occurs upstream. Publish focused, redacted excerpts; do not upload entire personal system logs by default.

Baseline success from the custom SteamOS port must remain labeled as baseline evidence until the same check passes on MainFrameOS.
