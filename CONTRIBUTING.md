# Contributing

MainFrameOS is at the engineering-bootstrap stage. Useful initial contributions include reproducible hardware reports, kernel/firmware provenance, package definitions and application workflow results.

1. State the exact board, software versions and problem being solved.
2. Reference upstream work before introducing a downstream patch.
3. Keep device-specific changes scoped to their profile.
4. Include meaningful validation and disclose untested hardware.
5. Update documentation when behavior or support status changes.

Hardware reports should use the [test plan](docs/TEST-PLAN.md). Application reports should use the [compatibility record](docs/APPLICATIONS.md). Never infer support from a shared chip name alone.

Remove credentials, serial numbers, network addresses and unrelated personal information from reports. Do not commit firmware or third-party binaries without an established redistribution path. Original project code and documentation use MIT. Imported code retains its upstream license and attribution. Submit original contributions under the project license and explicitly identify any third-party material.

Run `make check` before submitting changes. Build affected packages in the isolated ALARM builder and include the build manifest. Do not run package recipes directly on the development host.
