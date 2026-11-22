# Architecture

## Purpose and principles

Agentic Engineering Skills provides reusable, inspectable workflows for software-engineering agents. Its architecture favors an open contract, a single canonical source, small cohesive skills, progressive disclosure, explicit validation, and safe operation.

The design follows these principles:

- use the open Agent Skills format as the shared contract;
- keep canonical skill content independent of vendor-only features;
- make platform integrations thin and replaceable;
- avoid dependencies until a concrete capability requires them;
- keep instructions and supporting material easy to review and version;
- report only checks that were actually executed and their observed results.

## Repository organization

The repository organization is:

```text
.
├── .agents/
│   └── skills/          # Canonical skill directories
├── docs/                # Architecture, platform guides, validation, and release readiness
├── scripts/             # Validation, evaluation-record, and distribution tooling
├── tests/
│   └── fixtures/        # Representative behavioral scenarios
├── .github/
│   ├── ISSUE_TEMPLATE/  # Focused issue forms
│   └── workflows/       # Continuous integration
├── CONTRIBUTING.md      # Contribution workflow and acceptance criteria
├── SECURITY.md          # Private reporting and safe-research policy
├── THIRD_PARTY_NOTICES.md
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

The evidence level for each platform is recorded in the [platform compatibility matrix](platforms/compatibility-matrix.md). Official format or discovery support, deterministic structural validation, and controlled runtime behavior are separate claims.

- **Codex:** discovers repository skills under `.agents/skills/`. The ten-skill canonical catalog is implemented and structurally validated there; representative behavioral scenarios are documented but have not been executed as a cross-model evaluation suite.
- **GitHub Copilot:** documents `.agents/skills/` as a supported project location. The canonical catalog has been audited and structurally validated against the shared format, so no adapter or `.github/skills/` copy is needed. Discovery, activation, and workflow behavior across intended Copilot surfaces remain unverified.
- **Claude Code:** follows the Agent Skills standard and documents project discovery under `.claude/skills/`. The standard-library installer copies complete canonical skill directories into that location as a generated distribution, with a hash manifest that supports safe updates and rejects unmanaged conflicts. No Claude-specific frontmatter is added.

Copilot does not require an adapter because it supports the canonical location. Claude Code's generated distribution is created only on demand and is ignored in this repository; `.agents/skills/` remains authoritative. Generated output must not be edited as source. The installer detects local edits through recorded hashes and stops instead of overwriting them.

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

Using `.agents/skills/` aligns directly with Codex and Copilot and prevents content drift. Claude Code receives a generated copy through the installer because its project discovery path differs. The copy is explicitly managed distribution output, not an independently editable source.

### Managed copy instead of symlinks

Claude Code supports symlinked skill directories, but symlink creation and repository behavior vary across operating systems and Windows privilege configurations. The installer therefore uses ordinary files plus SHA-256 inventory metadata. It preflights the complete requested operation, writes changed files atomically, leaves identical files untouched, and refuses to overwrite or remove unmanaged or locally modified content.

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

CI verifies Python tests, scenario coverage, and the structural validator on Ubuntu with Python 3.11 and Windows with Python 3.13. It checks YAML, metadata, catalog structure, duplicate names, local reference safety, documentation links, and generated Claude distribution integrity without executing bundled skill commands. It does not prove behavioral quality, external-link availability, or cross-platform agent behavior. Runtime claims require separate controlled evaluation and are recorded independently from structural compatibility.

## Official references considered

- [Agent Skills specification](https://agentskills.io/specification)
- [OpenAI: Build skills](https://developers.openai.com/codex/skills)
- [GitHub Copilot: Agent skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)
- [GitHub Copilot: Add agent skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- [Claude Code: Extend Claude with skills](https://code.claude.com/docs/en/skills)

These documents describe different discovery locations and vendor extensions. The shared architecture relies only on their common open format; platform behavior remains subject to implementation and verification.
