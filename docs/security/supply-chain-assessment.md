# Supply-chain security assessment

This document defines the **post-release supply-chain assessment process** for Agentic Engineering Skills. It does not claim the historical `1.0.0` release met criteria not evidenced at publication. See the [publication record](../releases/1.0.0-publication.md), [historical readiness](../releases/v1.0.0-readiness.md), and [risk register](risk-register.md).

## Automated evidence

The [Supply chain audit workflow](../../.github/workflows/security-audit.yml) runs on pull requests and pushes to `main`, weekly, manually, and when invoked as a reusable workflow by the controlled [Publish release](../../.github/workflows/publish-release.yml) action. It uses Python 3.11 and `pip-audit==2.10.1`.

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

Future releases are prepared in a version-bump PR using [Prepare release](../../.github/workflows/prepare-release.yml), reviewed and merged to main, and only then published manually through [Publish release](../../.github/workflows/publish-release.yml). The full procedure and administrative prerequisites are documented in the [release process](../releases/release-process.md).

The release audit is reused with **read-only** permissions. The read-only builder creates the versioned ZIP and checksum and stages an immutable workflow artifact. The only job with `contents: write`, `id-token: write` and `attestations: write` is the separate publisher, gated by the GitHub Environment named `release`. A GitHub Environment approval is enforced **only after required reviewers have actually been configured in repository Settings**.

The privileged publisher does not check out or execute repository Python code. It downloads the exact staged artifact ID, validates SHA-256, confirms that main is unchanged and the tag does not exist, signs the ZIP with OIDC, and uses `gh attestation verify` to check the exact signer certificate, source ref and SHA. The workflow requires GitHub CLI version 2.102.0 or later. A draft GitHub Release is created with ZIP, checksum and verification JSON; the publisher checks the downloaded assets match the build before making it public.

The GitHub release and asset APIs are not atomic. In the event of a failed draft or upload, a draft release or tag may remain and require manual recovery; the workflow refuses to delete or replace an existing tag/release. User-facing verification commands are in the [release process](../releases/release-process.md).

Version `1.0.0` predates these controls and was not retroactively attested. The first attempt to publish `1.0.1` on 2026-11-23 completed SCA, build, checksum generation and [Sigstore attestation](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/attestations/71200801), then failed during draft asset readback because no Git tag existed yet. The release remained an unpublished Draft. A separate, manually approved recovery workflow verifies the signed original candidate before publishing by Release ID. The end-to-end public release and recovery path remain unverified until a successful recovery run is recorded.

## Manual review and residual risk

Review the [risk register](risk-register.md) after scan failures, dependency changes, advisories, platform tests, and every subsequent release. PyYAML is a development-time validation dependency, not bundled with installed skills; that may constrain its runtime exposure but does not automatically justify accepting a vulnerability.

References: [pip-audit](https://github.com/pypa/pip-audit), [CycloneDX](https://cyclonedx.org/), and [GitHub artifact attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).
