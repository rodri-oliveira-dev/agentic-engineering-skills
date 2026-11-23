# Agentic Engineering Skills

[English](README.md) | [Português (Brasil)](README.pt-BR.md)

[![Validate skills](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml)

A free, open source library of reusable software-engineering workflows for agents. Each skill has a narrow responsibility, explicit activation boundaries, safe failure behavior, and reviewable instructions. The vendor-neutral source lives only in `.agents/skills/`; OpenAI Codex is the priority platform.

Structural compatibility does not prove behavioral quality. The repository validates files and scenarios offline, while live-agent results are recorded separately and are currently pending.

## Skill catalog

- `api-design`: design or evolve API and integration contracts.
- `code-review`: review changes for evidence-backed, actionable defects.
- `commits`: prepare, organize, review, or create focused Git commits.
- `debug`: investigate observed failures through controlled diagnostics.
- `deployment-readiness`: assess readiness for a controlled deployment without deploying.
- `docs`: create, review, or update technical software documentation.
- `refactor`: improve maintainability while preserving observable behavior.
- `security-review`: perform authorized defensive security reviews.
- `sql`: develop and review relational SQL and safe schema evolution.
- `testing`: plan, implement, run, or assess automated tests.

Each canonical directory contains `SKILL.md` and, where useful, focused `references/` loaded only when needed.

## Quick start

Repository tooling requires Python 3.11 or newer. The validator uses the pinned PyYAML dependency; the installer and remaining tooling use the standard library.

```shell
git clone https://github.com/rodri-oliveira-dev/agentic-engineering-skills.git
cd agentic-engineering-skills
python -m venv .venv
```

Use the virtual environment's interpreter for dependency installation and validation.

Linux and macOS:

```shell
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/validate_skills.py --require-skills
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/evaluate_scenarios.py check
```

Windows PowerShell:

```powershell
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/validate_skills.py --require-skills
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe scripts/evaluate_scenarios.py check
```

Activation commands are platform features, not repository CLI options:

- **Codex:** use the checked-in `.agents/skills/` catalog directly, or copy complete selected skill directories to another repository. See the [Codex guide](docs/platforms/codex.md).
- **GitHub Copilot:** use the same canonical project directory; GitHub CLI also offers a public-preview installation workflow. See the [Copilot guide](docs/platforms/github-copilot.md).
- **Claude Code:** preview and create a managed `.claude/skills/` distribution with the included installer:

  ```shell
  python scripts/install_skills.py --platform claude-code --destination .claude/skills --all --dry-run
  python scripts/install_skills.py --platform claude-code --destination .claude/skills --all
  ```

  See the [Claude Code guide](docs/platforms/claude-code.md) before choosing an explicit project or user destination.

The cross-agent `skills` CLI can also discover all ten canonical skills directly from this repository without using the generated plugin package:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --list
```

Use its `--skill <name>` or `--all` option only after reviewing the listed skills and the destination agents.

For agent selection, individual installation, updates, removal, and the three native marketplaces, follow the [distribution and installation guide](docs/distribution.md). Remote marketplace commands apply after the manifests are published on the repository's default branch.

For marketplace distribution, the repository also provides one generated Agent Plugins 1.0 package containing all ten skills. Regenerate and verify it without a package manager:

```shell
python scripts/package_plugins.py generate
python scripts/package_plugins.py check
python scripts/package_plugins.py verify
```

The generated `plugins/agentic-engineering/skills/` tree is reviewable distribution output; edit only `.agents/skills/`. See [Plugin distribution architecture](docs/distribution-architecture.md) for the marketplace manifests, compatibility decisions, and versioning strategy.

## Updating

Update this checkout with Git only after preserving or committing local work, then rerun validation. Codex and Copilot use this repository immediately when operating here. For a managed Claude Code installation, rerun the same installer command; it updates unchanged managed files and refuses to overwrite unmanaged or locally modified content. Manual copies must be reviewed and replaced manually.

## Validation and compatibility

Automated checks cover the ten-skill structure, metadata, safe local references, catalog integrity, installer updates and removals, overwrite prevention, invalid input, validator regressions, scenario coverage, and documentation links. They require no credentials, paid service, or network access and never execute commands from skills.

Live model discovery, activation, refusal, and output quality are different evidence. See [Validation and testing](docs/validation.md), the [compatibility matrix](docs/platforms/compatibility-matrix.md), and [v1.0.0 readiness](docs/releases/v1.0.0-readiness.md) for the exact boundary.

## Contributing and security

Read [Contributing](CONTRIBUTING.md) and the [skill authoring contract](docs/skill-authoring.md), add focused tests, and report only checks actually run. Report vulnerabilities privately according to the [security policy](SECURITY.md). The project is licensed under the [MIT License](LICENSE); known dependency and attribution information is in [third-party notices](THIRD_PARTY_NOTICES.md).

Additional documentation: [architecture](docs/architecture.md), [roadmap](docs/roadmap.md), and [platform guides](docs/platforms/compatibility-matrix.md).
