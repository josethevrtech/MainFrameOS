# Repository settings checklist

Repository files configure workflows, code ownership and Dependabot. GitHub server-side settings are separate and must be verified through the repository settings/API before being claimed enabled.

Recommended before outside contributors or supported releases:

- Protect `main`: require pull requests, require `contracts-and-tests`, block force pushes/deletion, and require resolved conversations.
- Require code-owner review when a second active maintainer is available. A single owner cannot independently approve their own work; do not create a nominal rule that is always bypassed.
- Restrict workflow token defaults to read-only and allow only reviewed actions pinned to commits.
- Enable private vulnerability reporting and secret scanning/push protection where available.
- Protect release tags and use a separately approved release environment for signing/publishing.
- Avoid self-hosted runners on public pull requests; use isolated disposable runners.

This checklist is not a claim that those server settings are enabled. The initial implementation report must state which were actually verified. Code owners and green workflows alone are not branch protection.

## Verified settings — 2026-09-23

- Private vulnerability reporting: enabled.
- Dependency graph and Dependabot vulnerability alerts: enabled.
- Dependabot security-update pull requests: enabled; no auto-merge configured.
- Secret Protection and push protection: already enabled, verified in settings.
- Full-length action commit SHA requirement: enabled.
- Workflow token default: read repository contents/packages, verified.
- Workflows creating/approving pull requests: disabled, verified.
- External contributor workflow approval: required for all outside collaborators.

- `main` branch protection: pull request required; `contracts-and-tests` required; branch must be up to date; conversations must be resolved.
- Force pushes and branch deletion: blocked. Administrator bypass: disabled.
- Independent approval count: not required while the project has one maintainer; enable code-owner review when a second active maintainer is available.

Release-tag protection and an approved signing/publishing environment remain pending before release publication.
