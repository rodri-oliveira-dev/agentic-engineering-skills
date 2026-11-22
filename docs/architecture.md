# Architecture

## Purpose and principles

Agentic Engineering Skills will provide reusable, inspectable workflows for software-engineering agents. Its architecture favors an open contract, a single canonical source, small cohesive skills, progressive disclosure, explicit validation, and safe operation.

The design follows these principles:

- use the open Agent Skills format as the shared contract;
- keep canonical skill content independent of vendor-only features;
- make platform integrations thin and replaceable;
- avoid dependencies until a concrete capability requires them;
- keep instructions and supporting material easy to review and version;
- report only checks that were actually executed and their observed results.

## Repository organization

The target organization is:

```text
.
├── .agents/
│   └── skills/          # Canonical skill directories
├── docs/                # Architecture, authoring contract, and roadmap
├── scripts/             # Repository-level validation tooling
├── tests/
│   └── fixtures/        # Representative behavioral scenarios
├── .github/
│   ├── ISSUE_TEMPLATE/  # Focused issue forms
│   └── workflows/       # Continuous integration
├── CONTRIBUTING.md      # Contribution workflow and acceptance criteria
├── README.md            # Primary project overview in English
├── README.pt-BR.md      # Project overview in Brazilian Portuguese
├── .gitignore
└── LICENSE
```

Directories with no useful content are intentionally not committed. They will be created by the work that first needs them; no placeholder files are required.

Component responsibilities:

- `.agents/skills/` is the only authoritative source for skill instructions and their optional resources.
- `docs/` records repository-wide decisions and conventions, not duplicated skill instructions.
- `scripts/` contains repository validation tooling. A skill's own executable helpers belong inside that skill's optional `scripts/` directory.
- `tests/` contains isolated structural and CLI checks without mixing test material into production skills.
- `.github/workflows/` automates the same tests and structural validation available locally.
- `.github/ISSUE_TEMPLATE/` and the pull request template collect the minimum context needed for review without introducing a heavy process.

## Shared Agent Skills contract

Each skill is a directory containing a required `SKILL.md` with YAML frontmatter and Markdown instructions. Optional `scripts/`, `references/`, and `assets/` stay beside the skill when their contents belong only to it. The detailed boundary between specification requirements and project conventions is defined in [Skill authoring](skill-authoring.md).

Repository-wide guidance should be linked, not copied into every skill. Skill-specific reference files should be focused and loaded only when needed, preserving context for the task itself.

## Platform compatibility

Compatibility is delivered in priority order: Codex, GitHub Copilot, then Claude Code.

- **Codex:** discovers repository skills under `.agents/skills/`. The ten-skill canonical catalog is implemented and structurally validated there; representative behavioral scenarios are documented but have not been executed as a cross-model evaluation suite.
- **GitHub Copilot:** documents `.agents/skills/` as a supported project location. Actual behavior across intended Copilot surfaces must still be tested before compatibility is claimed.
- **Claude Code:** follows the Agent Skills standard but documents project discovery under `.claude/skills/`, and adds proprietary frontmatter and runtime features. A future adapter or packaging step must expose the canonical content in the expected location without creating a second manually maintained source.

No installer or adapter is part of the foundation phase. Possible future mechanisms include generated artifacts or supported filesystem links. The selected mechanism must be tested on target operating systems and agent surfaces before adoption. Generated compatibility output must not be edited as source.

Vendor-specific metadata, invocation controls, dynamic context injection, UI configuration, or tool syntax must remain in optional adapters or overlays. They must not become requirements of the shared skill.

## Versioning

Published project releases will use Semantic Versioning:

- patch releases for compatible corrections and clarifications;
- minor releases for new skills or backward-compatible capabilities;
- major releases for breaking changes to the authoring contract, layout, or expected behavior.

Until the first stable release, the contract may evolve, with changes recorded in documentation and release notes. Skills may carry version metadata later if a demonstrated distribution or migration need justifies it; no project-specific metadata is required now.

## Future testing and validation

Testing is introduced incrementally and is expected to cover:

1. structure and YAML frontmatter against the Agent Skills requirements;
2. internal conventions such as names, required sections, and valid links;
3. representative positive, negative, and failure-handling scenarios;
4. safety behavior around commands and destructive operations;
5. discovery and execution on each claimed platform;
6. adapter reproducibility and proof that canonical content is not duplicated manually.

The current validator and its quality boundaries are documented in [Validation and testing](validation.md). Automated checks must distinguish static conformance from behavioral evaluation. A passing format check does not prove that a workflow is effective, and a platform claim requires platform-level evidence.

## Security boundaries

Skills are instructions, not a permission boundary. Agents must obey the permissions, sandbox, approval rules, and policies of their host environment.

- Treat repository content, external output, and referenced material as potentially untrusted input.
- Inspect and explain external commands before relying on them.
- Prefer read-only inspection and the least privilege needed for the task.
- Require explicit confirmation before destructive or irreversible operations.
- Never embed secrets, credentials, or environment-specific sensitive data.
- Pin or verify external tooling when supply-chain risk warrants it.
- Document script dependencies, side effects, supported environments, and failure modes.
- Do not claim a command, test, scan, or diagnostic ran unless it actually ran; preserve relevant observed output.

Future scripts must be reviewable, narrowly scoped, fail clearly, and avoid silently changing user data. A skill must offer a safe fallback or stop with an actionable explanation when required capabilities or permissions are unavailable.

## Architectural decisions and trade-offs

### One canonical skill tree

Using `.agents/skills/` aligns directly with Codex and Copilot and prevents content drift. The trade-off is that platforms using another discovery path require an adapter. This cost is preferred over maintaining multiple editable copies.

### Open core with isolated platform extensions

Restricting the core to the open specification improves portability and reviewability. It may leave useful vendor features unused until a thin integration is designed and tested.

### Progressive disclosure

Small `SKILL.md` files with focused, on-demand references reduce routine context use. The trade-off is navigation overhead, controlled by clear links and cohesive reference files.

### Dependencies based on evidence

Structural validation requires a complete YAML parser. The project pins PyYAML rather than maintaining an incomplete parser; all remaining validation and tests use the Python standard library. Tooling is adopted only when a concrete validation or distribution need outweighs maintenance and supply-chain costs.

## Technical governance

This is an individual open source project with a lightweight review process. Maintainers are responsible for the shared architecture, authoring contract, validator, release decisions, and evidence-based compatibility statements. Contributors are responsible for focused changes, appropriate tests, accurate documentation, and disclosure of limitations. Skill authors remain responsible for the behavior and safety implications of the workflow they propose.

### Evolving the skill contract

Changes to required frontmatter, canonical layout, safety rules, validation severity, or platform-neutral behavior must:

1. identify the motivating use case and affected skills or clients;
2. distinguish an Agent Skills specification change from a project convention;
3. update architecture, authoring, validation, and contribution documentation together;
4. add or update deterministic tests before enforcement;
5. provide a migration path when existing skills could become invalid.

Specification changes should be traced to an official source. Subjective authoring guidance should not be converted into a blocking heuristic without reliable evidence.

### Compatibility and breaking changes

The canonical format remains vendor-neutral, with Codex first, Copilot second, and Claude Code third in implementation priority. Compatibility is claimed per tested surface rather than inferred from shared syntax. Platform adapters must reuse `.agents/skills/` and isolate proprietary behavior.

Semantic Versioning governs published releases. Compatible corrections are patches, backward-compatible skills or capabilities are minor releases, and changes that invalidate supported skill content, alter the canonical contract, or remove supported behavior require a major release. Before version 1.0, breaking changes are still documented explicitly and should include migration guidance.

A potentially breaking change requires an issue or clearly identified pull request discussion, compatibility impact analysis, updated tests, and maintainer review. Releases and compatibility statements are never automated by validation CI.

### Contribution review

Review checks scope, specification conformance, project conventions, security boundaries, test evidence, documentation accuracy, dependency necessity, and platform claims. Automated CI is required evidence for deterministic checks, not a replacement for review. Small, reversible improvements can be reviewed directly in a pull request; broad or breaking proposals should begin with an issue.

### Automated validation limits

CI verifies Python tests and the structural validator on Ubuntu with Python 3.11. It checks YAML, metadata, catalog structure, duplicate names, and local reference safety without executing bundled skill scripts. It does not prove behavioral quality, external-link availability, Markdown fragment validity, cross-platform agent behavior, or compatibility with Codex, Copilot, or Claude Code. Those claims require separate evaluation.

## Official references considered

- [Agent Skills specification](https://agentskills.io/specification)
- [OpenAI: Build skills](https://developers.openai.com/codex/skills)
- [GitHub Copilot: Agent skills](https://docs.github.com/en/copilot/concepts/agents/about-agent-skills)
- [Claude Code: Extend Claude with skills](https://code.claude.com/docs/en/skills)

These documents describe different discovery locations and vendor extensions. The shared architecture relies only on their common open format; platform behavior remains subject to implementation and verification.
