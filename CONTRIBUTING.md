# Contributing

MainFrameOS is at the design and hardware-baseline stage. Useful initial contributions include reproducible hardware reports, kernel/firmware provenance, package definitions and application workflow results.

1. State the exact board, software versions and problem being solved.
2. Reference upstream work before introducing a downstream patch.
3. Keep device-specific changes scoped to their profile.
4. Include meaningful validation and disclose untested hardware.
5. Update documentation when behavior or support status changes.

Hardware reports should use the [test plan](docs/TEST-PLAN.md). Application reports should use the [compatibility record](docs/APPLICATIONS.md). Never infer support from a shared chip name alone.

Remove credentials, serial numbers, network addresses and unrelated personal information from reports. Do not commit firmware or third-party binaries without an established redistribution path. Project licensing is pending; resolve it before soliciting external code contributions or publishing distributable binaries. No additional contributor rights are implied by this document.
