# Supply-chain residual risk register

This register tracks **open risk conditions and evidence gaps**, not confirmed unobserved vulnerabilities or automatic risk acceptance. The repository maintainer is the accountable owner. Review each entry after relevant CI evidence and before each new release.

| ID | Risk or evidence gap | Impact and treatment | Status |
| --- | --- | --- | --- |
| SC-001 | Release `1.0.0` has no project-published checksum or attested archive | Historical consumers cannot verify project build provenance; preserve limitation and attest future releases | Open, historical |
| SC-002 | PyPI wheel SHA-256 alone does not attest the publisher/build of PyYAML | Capture digest and upstream sources; do not assert unverified build provenance | Open, limited evidence |
| SC-003 | Scanner and advisory-index availability and freshness vary | Audit PRs, pushes, weekly, and on release; fail closed when checks are inconclusive | Open, CI monitoring |
| SC-004 | Pinned GitHub Actions SHAs do not establish publisher trust | Review upstream source and Dependabot proposals before merging | Open, manual review |
| SC-005 | Copilot CLI, Claude Code and live agent behavior remain outside supply-chain checks | Run separate installation and behavioral evaluations and record evidence | Open, compatibility work |
| SC-006 | Release workflow requires OIDC and a release-scoped token with write permission | Review tag/release rulesets; scope permissions to release job; verify the first release run | Open, review new control |

## Decision record

For a change of status, record **risk ID, date UTC, release/revision, evidence URL, likelihood and impact, rationale, owner, treatment, residual exposure, explicit decision and approval, and next review date**. No row above is a recorded risk acceptance.

Related documents: [assessment process](supply-chain-assessment.md), [historical readiness](../releases/v1.0.0-readiness.md), and [publication record](../releases/1.0.0-publication.md).
