# Contributing

Thank you for helping build Agentic Engineering Skills. The project develops small, inspectable, reusable workflows for software-engineering agents. Contributions should favor an open, portable core, explicit validation, safe behavior, and evidence over platform-specific convenience or unverified claims.

All contributions must follow the open [Agent Skills specification](https://agentskills.io/specification) and this repository's [skill authoring contract](docs/skill-authoring.md).

## Prepare the environment

Requirements:

- Git;
- Python 3.11 or newer;
- a virtual environment is recommended.

From the repository root, create the environment and use its interpreter explicitly. Activation is optional.

Linux and macOS:

```shell
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
```

The project intentionally keeps its dependency set small and pinned. Python is required for repository development and validation, not for every end-user installation route.

## Create a skill

Before authoring, read [Architecture](docs/architecture.md), [Skill authoring](docs/skill-authoring.md), and [Validation and testing](docs/validation.md).

1. Create `.agents/skills/<skill-name>/SKILL.md`.
2. Use an English ASCII kebab-case directory name, such as `code-review`.
3. Make the frontmatter `name` exactly match the directory.
4. Write a precise `description` that states what the skill does and when it should be used.
5. Define one responsibility, use and non-use boundaries, prerequisites, an ordered workflow, validation, and failure handling.
6. Add focused `references/`, `scripts/`, or `assets/` only when they are necessary.
7. Keep the shared skill independent of proprietary platform fields.

The minimum specification-compatible file begins with:

```yaml
---
name: example-skill
description: Perform a specific outcome. Use when the task has these explicit signals.
---
```

The complete project contract is normative; this example is not a substitute for it. Never include credentials, claim checks that were not executed, or direct an agent to perform destructive operations without confirmation.

## Run validation

With the virtual environment activated, run the same commands used by continuous integration. If it is not activated, replace `python` with `.venv/bin/python` on Linux/macOS or `.venv\Scripts\python.exe` on Windows PowerShell:

```shell
python -m unittest discover -s tests -v
python scripts/validate_skills.py --require-skills
python scripts/evaluate_scenarios.py check
python scripts/package_plugins.py check
python scripts/package_plugins.py verify
```

The validator checks structure, frontmatter, names, duplicates, and local reference safety without executing skill scripts. Errors fail validation; project-convention warnings do not. The scenario checker verifies fixture coverage and any supplied evaluation-record schema; it does not run an agent or turn fixtures into behavioral results. Structural success does not prove behavioral quality.

`.agents/skills/` is the only canonical source for skill content. `plugins/agentic-engineering/` and the three marketplace manifests are generated distribution artifacts. When canonical skills or package metadata change, run `python scripts/package_plugins.py generate`, review the generated diff, and then run both package checks above. Documentation-only changes that do not affect package content do not require regeneration. Do not commit generated `.claude/skills/` output or create an independently editable `.github/skills/` tree.

Changes to platform distribution must update the [compatibility matrix](docs/platforms/compatibility-matrix.md), preserve deterministic generation and safety boundaries, and include evidence at the level claimed. Documentation must distinguish structural checks, client installation, and live behavioral execution.

## Write tests

Use Python's `unittest` framework. Add focused scenarios to `tests/`, create skill catalogs under `tempfile.TemporaryDirectory`, and keep tests deterministic, independent of the network, and portable across Linux, macOS, and Windows.

Cover the smallest behavior changed. Assert actionable diagnostics and exit codes when relevant. Do not put deliberately invalid fixtures in the canonical `.agents/skills/` catalog, weaken tests to hide failures, or execute bundled skill scripts.

## Report bugs

Use the bug report issue form. Include reproducible steps, observed and expected behavior, platform and Python information, and relevant logs with secrets removed. Search existing issues first when practical.

Security-sensitive reports must follow the [security policy](SECURITY.md) and avoid publishing exploit details or credentials in a public issue.

## Propose improvements

Use the feature request form to explain the problem before the proposed solution, alternatives considered, expected impact, and any compatibility implications. Open an issue before a large or breaking change so the scope can be aligned without imposing a heavy process on small improvements.

## Open a pull request

- Create a focused branch; do not mix unrelated changes.
- Update documentation when behavior or contracts change.
- Add or adjust tests for verifiable behavior.
- Run all validation commands locally and report their observed results, including skips.
- Complete the pull request checklist and describe known limitations.
- Do not claim compatibility that has not been tested.
- Identify public-contract, compatibility, dependency, packaging, or canonical-layout effects. Apply Semantic Versioning implications according to [Architecture](docs/architecture.md#versioning); documentation-only corrections normally do not change the package version.
- Expect review of scope, canonical-source ownership, generated artifacts, test evidence, documentation accuracy, security boundaries, compatibility claims, and versioning impact.

A contribution is ready for acceptance when its scope is clear, required checks pass, Agent Skills conformance and project conventions are preserved, safety implications are addressed, documentation matches behavior, and review comments are resolved. Changes to the shared contract or compatibility promises require the additional review described in [Technical governance](docs/architecture.md#technical-governance).
