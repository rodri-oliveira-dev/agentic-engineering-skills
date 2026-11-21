# Agentic Engineering Skills

[![Validate skills](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml/badge.svg)](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/actions/workflows/validate-skills.yml)

Agentic Engineering Skills is a free, open source collection of reusable skills for software-engineering agents. The project is intended to turn recurring engineering practices into reviewable, versioned instructions without tying their core content to one vendor.

The library addresses a common problem: agent workflows are often repeated in prompts, scattered across repositories, or written in platform-specific formats. This repository will provide focused skills with explicit scope, inputs, workflows, validation, and failure handling.

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

## Project status

The project is in its foundation phase. The architecture, authoring contract, structural validation tooling, CI workflow, and contribution guidelines are established; none of the ten planned skills has been implemented. Installers, platform adapters, and behavioral evaluation are not available yet.

With Python 3.11 or newer and the dependencies from `requirements.txt` installed, run `python scripts/validate_skills.py` to validate the catalog and `python -m unittest discover -s tests -v` to run the test suite. An empty catalog is allowed during foundation work and is reported as zero validated skills.

Development is public, and the project is free software licensed under the [MIT License](LICENSE).
