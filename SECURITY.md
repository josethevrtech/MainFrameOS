# Security and vulnerability handling

No supported OS release exists yet. Current artifacts are development-only.

For a suspected vulnerability, use [GitHub private vulnerability reporting](https://github.com/josethevrtech/MainFrameOS/security/advisories/new), now enabled for this repository. Do not include exploit details or credentials in a public issue. Response staffing must be established before a supported release; no response-time guarantee is made at this stage.

The maintainer should acknowledge, reproduce and assess impact, identify affected builds and upstream ownership, prepare a tested fix, publish remediation and credit, and document any unsupported/EOL versions. Track boot, updater, package trust and runtime isolation issues as release blockers when they affect required security properties.

Signing keys, registry credentials and release tokens must remain outside the source tree. CI checks use read-only repository permissions; they do not publish releases or sign artifacts. Manual package workflows upload unsigned development artifacts only. Do not run untrusted pull-request code on the reference laptop or a privileged self-hosted runner.

Original project code uses MIT; third-party code retains its upstream license. Package integrity and licensing are separate checks.
