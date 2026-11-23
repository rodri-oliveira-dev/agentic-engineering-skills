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

GitHub draft releases do **not** necessarily create a Git tag until publication. The workflow identifies a draft by its numeric release ID and reads its assets through the GitHub Releases API; the tag-to-commit check runs **after** publication. This matters because by-tag release lookup and Git ref lookup can return 404 on a valid draft. Release creation and asset upload are not atomic.

### Recover a signed draft without deleting it

If the publishing job fails after a draft and an attestation have been created, do **not** rerun Publish release or manually publish/delete the draft. Confirm that the original run signed the intended archive, then use [Recover verified release draft](../../.github/workflows/recover-release-draft.yml) manually from main.

Enter the existing stable version and the **numeric Release ID** from the Releases API. The recovery job requires the protected release Environment and repeats the current SCA audit. Before publishing, it confirms the draft identity and intended source SHA, ensures that commit is an ancestor of current main, verifies the original archive/checksum and GitHub-stored asset digests, checks the original Sigstore attestation's signer workflow, source ref and commit, and requires that the Git tag does not already exist. It then publishes **the existing Draft by ID**, confirms creation of the tag, and checks that the new tag points to the original attested commit.

Recovery is a separate, explicit approval step. It does not regenerate or silently replace assets, change the approved source commit, delete tags, or publish on its own. If verification fails, the Draft remains unpublished for manual investigation.

For the 2026-11-23 partial publication of version 1.0.1, the recorded Draft ID is **455709541**, the original source commit is `8f6cd2ff748cca8af81dc54a06a426e4d2b0f1d5`, and the original attestation is [71200801](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/attestations/71200801). These values identify the existing **unpublished** candidate; they are not evidence that recovery has succeeded. See [1.0.1 draft incident](1.0.1-draft-recovery.md).

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
