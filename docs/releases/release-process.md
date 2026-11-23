# Release process: prepare, approve, attest, publish

This process automates a stable SemVer release without automatically merging source changes. It does not modify the historical 1.0.0 Git tag or publication record.

## One-time GitHub administration

Before the first use, configure the repository:

1. **Settings → Actions → General:** enable **Allow GitHub Actions to create and approve pull requests**, otherwise the preparation workflow cannot create a PR using GITHUB_TOKEN.
2. **Settings → Environments:** create an environment called **release**, require a reviewer, and restrict it to deployments from **main**. If "Prevent self-review" is enabled, another maintainer must approve the job. Merely referencing an environment in YAML does **not** provide protection: GitHub can automatically create an unprotected environment.
3. **Settings → Rulesets:** require the Linux/Windows validation and SCA, SBOM and provenance inventory checks for main. Keep the unprefixed SemVer tag convention protected against deletion or modification.
4. Verify repository Actions policy permits job-scoped token permissions and GitHub artifact attestations.

Repository administration cannot be completed merely by merging these workflow files. Without configured reviewers the publication job is manual to trigger, but **does not** have an independent approval gate.

## 1. Prepare a version PR

Go to [Prepare release](../../.github/workflows/prepare-release.yml) in GitHub Actions and select **Run workflow** from main. Enter the new stable version (such as 1.0.1, without a v prefix) and factual release notes.

The workflow rejects invalid/non-increasing versions and existing tags, updates the canonical PLUGIN_VERSION in scripts/package_plugins.py, regenerates all plugin and marketplace files, and creates docs/releases/<version>-notes.md. It runs unit, packaging, skill and fixture tests before opening a **draft PR**; it never merges or publishes a tag.

Because GITHUB_TOKEN-authored PRs may not automatically run ordinary PR workflows, the action explicitly dispatches both validate-skills.yml and security-audit.yml on the candidate branch. Inspect the required checks on the correct head SHA and review the actual release notes before marking the PR ready and merging it.

## 2. Publish the approved version

Once the version PR is merged and all main checks pass, open [Publish release](../../.github/workflows/publish-release.yml) in Actions. Select main, provide the exact merged version and start it manually.

The workflow has six stages:

1. Check the main event SHA, manifest versions, generated package integrity, proposed release notes and absence of the tag/release.
2. Run the existing vulnerability audit, CycloneDX SBOM and provenance inventory through a read-only reusable workflow.
3. Build a deterministic ZIP and SHA-256 checksum and stage them as an immutable Actions artifact, using only read permissions.
4. Pause for approval by the protected **release** Environment reviewer. Only this final job has contents: write, id-token: write and attestations: write.
5. Download the exact artifact by ID and verify the digest, checksum and unchanged main commit. Attest the ZIP using GitHub OIDC; independently validate the attestation against the **exact signer certificate identity**, source branch and source SHA, using a patched GitHub CLI (>= 2.102.0).
6. Create a draft GitHub Release with the ZIP, checksum and verification evidence. Download the draft assets, verify their SHA-256 and compare the bytes to the original. Only then publish the release.

The release notes include the workflow run URL and commit SHA. The preparation PR does **not** claim its version is published. Only the completed publication run establishes that fact.

If the workflow fails after creating the draft release or tag, inspect the draft and recover manually. Publishing with assets is not atomic; the automation does not delete protected tags or overwrite an existing release.

## 3. Verify the release independently

After a successful publication of 1.0.1, on a machine with a current GitHub CLI:

~~~powershell
gh release download 1.0.1 --repo rodri-oliveira-dev/agentic-engineering-skills --pattern "agentic-engineering-1.0.1.zip*" --dir .\release-verify
Get-FileHash .\release-verify\agentic-engineering-1.0.1.zip -Algorithm SHA256
gh attestation verify .\release-verify\agentic-engineering-1.0.1.zip --repo rodri-oliveira-dev/agentic-engineering-skills --cert-identity "https://github.com/rodri-oliveira-dev/agentic-engineering-skills/.github/workflows/publish-release.yml@refs/heads/main" --source-ref refs/heads/main
~~~

Compare the hash to the downloaded checksum file. Preserve the published attestation-verification.json asset and GitHub Actions run as the evidence record.

This proves the artifact's cryptographic provenance and integrity to the verified source workflow; it does not prove behavioral quality in Codex, Copilot or Claude. The original [1.0.0 publication](1.0.0-publication.md) predates this procedure and is **not** retroactively attested.

See [security assessment](../security/supply-chain-assessment.md) and [residual risk register](../security/risk-register.md).

Official documentation: [GITHUB_TOKEN triggering behavior](https://docs.github.com/en/actions/concepts/security/github_token), [protected environments](https://docs.github.com/en/actions/how-tos/deploy/configure-and-manage-deployments/manage-environments), [GitHub attestations](https://docs.github.com/en/actions/how-tos/secure-your-work/use-artifact-attestations/use-artifact-attestations).
