# Agentic Engineering Skills

[English](README.md) | [Português (Brasil)](README.pt-BR.md)

[![Validate skills](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml)

A free, open source library of ten reusable software-engineering workflows for agents. The vendor-neutral, canonical source lives only in `.agents/skills/`; generated marketplace packages are derived from it. OpenAI Codex is the priority platform.

Published versions are listed under [GitHub Releases](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/releases). The [original 1.0.0 publication record](docs/releases/1.0.0-publication.md) is retained as historical evidence. Publication and structural validation alone do not prove live-agent behavior.

## Quick installation

The cross-agent `skills` CLI can list the catalog without installing it:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --list
```

Install one skill and select its target agents interactively:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --skill code-review
```

Install all ten skills for every supported agent without confirmation:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --all
```

`--all` is shorthand for `--skill '*' --agent '*' -y`. To limit installation to specific agents, use explicit `--agent` values instead. Because this non-interactive operation can replace same-named skill directories, preserve uncommitted work and move or back up conflicting directories before running it.

This route requires Node.js with `npx`, not Python. For explicit agent selection, marketplace installation, updates, removal, standalone copies, and verified status, use the [installation and distribution guide](docs/distribution.md).

## Supported agents and distribution methods

| Method | What is available | Verified status |
| --- | --- | --- |
| Universal `npx skills` | One or selected skills for selected agents; `--all` for every skill and supported agent | Local and remote catalog listing validated with CLI `1.9.0`; mutating installation is not recorded |
| OpenAI Codex marketplace | The complete `agentic-engineering` plugin | Public repository registration, listing, and isolated installation validated with Codex CLI `0.171.0-alpha.13`; live activation not tested |
| GitHub Copilot CLI marketplace | The complete plugin | Published and structurally validated; CLI installation and behavior not tested |
| Claude Code marketplace | The complete plugin | Published and structurally validated; CLI installation and behavior not tested |
| Standalone project installation | Canonical `.agents/skills/` for Codex/Copilot; managed `.claude/skills/` copy for Claude Code | Repository structure and the Claude installer are tested without launching an agent |

The three marketplace manifests are publicly available on `main`. A manifest's existence means **published**, repository checks can mean **structurally validated**, a successful client operation means **installation validated**, and a controlled live-agent run is required for **behavioral validation**. Do not infer one state from another.

Platform guides: [Codex](docs/platforms/codex.md), [GitHub Copilot](docs/platforms/github-copilot.md), [Claude Code](docs/platforms/claude-code.md), and the [compatibility matrix](docs/platforms/compatibility-matrix.md).

## Skill catalog

- [`api-design`](.agents/skills/api-design/SKILL.md): design or evolve API and integration contracts.
- [`code-review`](.agents/skills/code-review/SKILL.md): review changes for evidence-backed, actionable defects.
- [`commits`](.agents/skills/commits/SKILL.md): prepare, organize, review, or create focused Git commits.
- [`debug`](.agents/skills/debug/SKILL.md): investigate observed failures through controlled diagnostics.
- [`deployment-readiness`](.agents/skills/deployment-readiness/SKILL.md): assess readiness for a controlled deployment without deploying.
- [`docs`](.agents/skills/docs/SKILL.md): create, review, or update technical software documentation.
- [`refactor`](.agents/skills/refactor/SKILL.md): improve maintainability while preserving observable behavior.
- [`security-review`](.agents/skills/security-review/SKILL.md): perform authorized defensive security reviews.
- [`sql`](.agents/skills/sql/SKILL.md): develop and review relational SQL and safe schema evolution.
- [`testing`](.agents/skills/testing/SKILL.md): plan, implement, run, or assess automated tests.

Each canonical directory contains `SKILL.md` and, where useful, focused `references/` loaded only when needed.

## Platform compatibility and validation

Automated checks cover structure, metadata, local references, catalog integrity, installer safety, deterministic package generation, embedded hashes, scenario coverage, and documentation links. They do not execute skill instructions or evaluate model output. No completed behavioral evaluation record is currently stored in the repository.

See [Validation and testing](docs/validation.md), the [compatibility matrix](docs/platforms/compatibility-matrix.md), the historical [v1.0.0 readiness assessment](docs/releases/v1.0.0-readiness.md), and the factual [v1.0.0 publication record](docs/releases/1.0.0-publication.md).

## Development and testing

Python 3.11 or newer and the pinned PyYAML dependency are required to develop and validate this repository; they are not requirements for every installation method.

Linux and macOS:

```shell
python -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python -m unittest discover -s tests -v
.venv/bin/python scripts/validate_skills.py --require-skills
.venv/bin/python scripts/evaluate_scenarios.py check
.venv/bin/python scripts/package_plugins.py check
.venv/bin/python scripts/package_plugins.py verify
```

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe -m unittest discover -s tests -v
.venv\Scripts\python.exe scripts/validate_skills.py --require-skills
.venv\Scripts\python.exe scripts/evaluate_scenarios.py check
.venv\Scripts\python.exe scripts/package_plugins.py check
.venv\Scripts\python.exe scripts/package_plugins.py verify
```

Edit only `.agents/skills/`. Regenerate marketplace output only when canonical skill content or package metadata changes; documentation-only changes do not require regeneration. See [Plugin distribution architecture](docs/distribution-architecture.md).

## Contributing and security

Read [Contributing](CONTRIBUTING.md) and the [skill authoring contract](docs/skill-authoring.md), add focused evidence, and report only checks actually run. Report vulnerabilities privately according to the [security policy](SECURITY.md).

Supply-chain controls are described in the [security assessment](docs/security/supply-chain-assessment.md), [risk register](docs/security/risk-register.md), and [release process](docs/releases/release-process.md).

## License and additional documentation

The project is licensed under the [MIT License](LICENSE). Known dependency and attribution information is in [third-party notices](THIRD_PARTY_NOTICES.md). Additional documentation includes the [architecture](docs/architecture.md), [roadmap](docs/roadmap.md), and [distribution architecture](docs/distribution-architecture.md).
