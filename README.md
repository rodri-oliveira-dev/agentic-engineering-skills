# Agentic Engineering Skills

[![Validate skills](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml)

Agentic Engineering Skills is a free, open source collection of reusable skills for software-engineering agents. The project is intended to turn recurring engineering practices into reviewable, versioned instructions without tying their core content to one vendor.

The library addresses a common problem: agent workflows are often repeated in prompts, scattered across repositories, or written in platform-specific formats. This repository provides focused skills with explicit scope, inputs, workflows, validation, and failure handling.

## Audience

This project is for software engineers, maintainers, and teams that want to inspect, adapt, and share repeatable agent workflows.

## Planned platforms

Development will prioritize:

1. OpenAI Codex
2. GitHub Copilot
3. Claude Code

The shared contract follows the open [Agent Skills specification](https://agentskills.io/specification). Platform support will be claimed only after it is implemented and tested. The canonical source will live under `.agents/skills/`; platform-specific integration must reuse that source rather than maintain independent copies.

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

Canonical skills live under [`.agents/skills/`](.agents/skills/). Five of the ten planned skills are currently implemented:

- `docs`: create, review, and update technical software documentation.
- `commits`: prepare, organize, review, and create focused Git commits.
- `refactor`: improve maintainability while preserving observable behavior.
- `api-design`: design and evolve API and integration contracts.
- `testing`: plan, implement, run, and assess automated tests.

The remaining skills are tracked in the [roadmap](docs/roadmap.md). The canonical content follows the open Agent Skills contract and prioritizes Codex, but compatibility with GitHub Copilot and Claude Code has not yet been tested or claimed.

## Project status

The foundation and the first five essential skills are implemented. Installers, platform adapters, and automated behavioral evaluation are not available yet.

With Python 3.11 or newer and the dependencies from `requirements.txt` installed, run `python scripts/validate_skills.py --require-skills` to validate the non-empty catalog and `python -m unittest discover -s tests -v` to run the automated validator tests. Structural validation checks format, metadata, catalog integrity, and local references; it does not demonstrate skill triggering or behavioral quality. Representative behavioral scenarios are documented under `tests/fixtures/`, but they are not automated test results.

Development is public, and the project is free software licensed under the [MIT License](LICENSE).
