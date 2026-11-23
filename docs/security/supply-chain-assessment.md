# Supply-chain security assessment

This document defines the **post-release supply-chain assessment process** for Agentic Engineering Skills. It does not claim the historical `1.0.0` release met criteria not evidenced at publication. See the [publication record](../releases/1.0.0-publication.md), [historical readiness](../releases/v1.0.0-readiness.md), and [risk register](risk-register.md).

## Automated evidence

The [Supply chain audit workflow](../../.github/workflows/security-audit.yml) runs on pull requests and pushes to `main`, weekly, manually, and when a GitHub Release is published. It uses Python 3.11 and `pip-audit==2.10.1`.

Artifacts from the audit job, retained for 30 days:

| Output | Scope and limitations |
| --- | --- |
| `sca-report.json` | Known Python dependency advisories from PyPI; a clean scan is not proof of absence of vulnerabilities |
| `sbom.cdx.json` | CycloneDX SBOM for resolved Python requirements, not the entire plugin or CI runner |
| `provenance-inventory.json` | Requirements and plugin inventory hashes, pinned Action references, wheel hashes matched against PyPI metadata |
| `auditor-version.txt` | Scanner version used |

The pipeline fails on reported vulnerabilities, dependency resolution errors, missing/inaccessible PyPI metadata, hash mismatches, package drift, and incomplete audit evidence. Available reports are uploaded even when scanner checks fail. Findings are **not automatically ignored or accepted**.

## Provenance and trust boundaries

The workflow downloads pinned Python distributions using `--no-deps --only-binary=:all:` from the official PyPI index. SHA-256 values are compared with the corresponding PyPI JSON metadata. This establishes agreement with the index response, **not independently verified publisher identity or build provenance**. Missing compatible wheels or inaccessible metadata cause an inconclusive, failing check.

Third-party GitHub Actions must use full commit SHA references. SHA pinning prevents drift, not malicious source code. Dependabot update proposals still require maintainer review.

`scripts/package_plugins.py check` and `verify` reconstruct the generated marketplace package from the canonical skill tree and check its embedded hashes. They establish internal integrity, not an independent signature. The audit covers the requirements file, not scanner bootstrap dependencies, the runner image, or live-agent behavior.

Download evidence from the corresponding GitHub Actions run. Do not commit an unrelated workstation audit as if it came from the release pipeline.

## Local commands (PowerShell)

Use the Python version installed locally (3.11 or newer); 3.14 is illustrative:

```powershell
py -3.14 -m venv .venv-audit
.\.venv-audit\Scripts\python.exe -m pip install 'pip-audit==2.10.1' -r requirements.txt
New-Item -ItemType Directory -Force security-evidence
.\.venv-audit\Scripts\python.exe -m pip_audit -r requirements.txt -f json -o security-evidence/sca-report.json
.\.venv-audit\Scripts\python.exe -m pip_audit -r requirements.txt -f cyclonedx-json -o security-evidence/sbom.cdx.json
.\.venv-audit\Scripts\python.exe scripts/package_plugins.py check
.\.venv-audit\Scripts\python.exe scripts/package_plugins.py verify
```

The local audit environment and output directories are ignored by Git.

## Future release provenance

For GitHub Releases published **after this workflow merges**, a read-only build job requires a successful SCA/inventory job, checks out the immutable event commit (`github.sha`), verifies package integrity and version matching, and builds a reproducible ZIP plus SHA-256 checksum. It stages the candidate as an immutable workflow artifact. A separate privileged job downloads that artifact by its ID, rejects artifact digest or checksum mismatches, verifies that the tag still resolves to the triggering commit, and requests an `actions/attest` build-provenance attestation before uploading the ZIP and checksum as Release assets. Only this isolated publishing job receives `contents: write`, `id-token: write` and `attestations: write`; it never checks out or executes repository-controlled Python scripts.

Verify a downloaded archive:

```shell
gh attestation verify agentic-engineering-VERSION.zip --repo rodri-oliveira-dev/agentic-engineering-skills
```

Also compare the archive's hash to the published `.sha256` file. The attestation binds the bytes to a future GitHub Actions run; it does not prove agent behavior. If the repository cannot issue attestations, the release job fails rather than silently publishing an unattested ZIP.

The publishing job relies on GitHub-hosted `gh`, `jq` and `sha256sum` and on the repository's release/tag permissions. The attestation flow has **not been exercised by a real release** yet; the pull-request CI validates only the nonprivileged audit path and structural tests. Version `1.0.0` predates these controls and **has no project-built attested ZIP or project checksum**. The new workflow does not attest the historical release retroactively.

## Repository administration required

At the review date, the repository tag ruleset protects `refs/tags/v*`, whereas the released tag is `1.0.0` without `v`. Extend tag immutability protection to the actual tag naming convention (and future tags) in GitHub Settings before relying on stable tag identity. The branch ruleset currently requires the Linux/Windows validation checks but not the new `SCA, SBOM and provenance inventory` check. After this workflow is merged and a successful run exists on `main`, add that check to required status checks. Repository rulesets are administrative settings and are **not changed by this PR**.

## Manual review and residual risk

Review the [risk register](risk-register.md) after scan failures, dependency changes, advisories, platform tests, and every subsequent release. PyYAML is a development-time validation dependency, not bundled with installed skills; that may constrain its runtime exposure but does not automatically justify accepting a vulnerability.

References: [pip-audit](https://github.com/pypa/pip-audit), [CycloneDX](https://cyclonedx.org/), and [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).
