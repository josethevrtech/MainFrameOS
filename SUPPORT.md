# Support policy

**Current support level: development / bring-up. There is no supported MainFrameOS OS image yet.**

The product scope is Snapdragon laptops and headsets across manufacturers and configurations, through one shared installer. The available developer laptop is the first test machine. Each configuration remains a candidate until it passes its own published tests. Android and Windows application compatibility is version/workflow specific.

Use repository bug or device templates for reproducible issues. Include build ID, board, relevant runtime versions, reproduction and redacted evidence. The `mainframeos-support` utility reports only a small allowlist of model identifiers; it does not collect serial numbers, network configuration or personal logs.

Initial maintainer: `@josethevrtech`. A backup maintainer/tester remains to be recruited. Development reports are handled as capacity permits; there is no paid support or response SLA.

Before a stable release, publish supported versions, release dates, support windows, critical-fix process, migration policy and recovery instructions. Unsupported configurations must remain clearly labeled. See [Engineering contract](docs/ENGINEERING.md) and [Test plan](docs/TEST-PLAN.md).
