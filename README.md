# Agentic Engineering Skills

[![Validate skills](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml)

Agentic Engineering Skills is a free, open source collection of reusable skills for software-engineering agents. The project is intended to turn recurring engineering practices into reviewable, versioned instructions without tying their core content to one vendor.

The library addresses a common problem: agent workflows are often repeated in prompts, scattered across repositories, or written in platform-specific formats. This repository provides focused skills with explicit scope, inputs, workflows, validation, and failure handling.

## Audience

This project is for software engineers, maintainers, and teams that want to inspect, adapt, and share repeatable agent workflows.

## Platform support

The shared contract follows the open [Agent Skills specification](https://agentskills.io/specification), and `.agents/skills/` is the only canonical source.

- **OpenAI Codex:** the ten-skill catalog is implemented in Codex's repository discovery location and structurally validated. Representative behavioral scenarios are documented, but no automated cross-model behavioral evaluation has been completed.
- **GitHub Copilot:** compatibility remains pending validation on the intended Copilot surfaces.
- **Claude Code:** compatibility remains pending validation and a non-duplicating adapter for its documented project discovery location.

Platform-specific integration must reuse the canonical source rather than maintain independently editable copies.

## Quality principles

- One well-defined responsibility per skill.
- Concise, action-oriented instructions and progressive disclosure of references.
- Observable validation; never invent test, diagnostic, or verification results.
- Explicit handling of prerequisites, uncertainty, failure, and limitations.
- Confirmation before destructive or irreversible operations.
- Respect for the host environment's permissions and security policies.
- A portable core, isolated from vendor-specific extensions.

## Documentation

- [Architecture](docs/architecture.md)
- [Skill authoring contract](docs/skill-authoring.md)
- [Validation and testing](docs/validation.md)
- [Roadmap](docs/roadmap.md)
- [Contributing](CONTRIBUTING.md)
- [Portuguese (Brazil) README](README.pt-BR.md)

## Skill catalog

Canonical skills live under [`.agents/skills/`](.agents/skills/). The complete planned catalog currently contains ten implemented skills:

- `docs`: create, review, and update technical software documentation.
- `commits`: prepare, organize, review, and create focused Git commits.
- `refactor`: improve maintainability while preserving observable behavior.
- `api-design`: design and evolve API and integration contracts.
- `testing`: plan, implement, run, and assess automated tests.
- `code-review`: review diffs and proposed changes for evidence-backed, actionable defects.
- `sql`: develop and review relational SQL, data integrity, transactions, indexing, and safe schema evolution.
- `debug`: investigate observed failures through evidence, falsifiable hypotheses, and controlled diagnostics.
- `security-review`: perform authorized defensive reviews of code, configuration, dependencies, and architecture.
- `deployment-readiness`: assess technical readiness for controlled deployment without executing it.

Each skill has one canonical `SKILL.md`; specialized guidance is kept in on-demand `references/` files, and representative positive, negative, and insufficient-evidence scenarios live under `tests/fixtures/<skill>/`. See the [roadmap](docs/roadmap.md) for evaluation and platform work. Compatibility with GitHub Copilot and Claude Code has not yet been tested or claimed.

## Project status

The foundation and all ten planned skills are implemented. This is not a published 1.0 release. Installers, Copilot and Claude adapters, and automated behavioral evaluation are not available yet.

With Python 3.11 or newer and the dependencies from `requirements.txt` installed, run `python scripts/validate_skills.py --require-skills` to validate the non-empty catalog and `python -m unittest discover -s tests -v` to run the automated validator tests. Structural validation checks format, metadata, catalog integrity, and local references; it does not demonstrate skill triggering or behavioral quality. Representative behavioral scenarios are documented under `tests/fixtures/`, but they are not automated test results.

Development is public, and the project is free software licensed under the [MIT License](LICENSE).
