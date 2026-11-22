# Skill authoring contract

This contract governs every skill that will be added to this repository. It deliberately separates requirements of the open Agent Skills specification from stricter project conventions.

The contract applies to all ten implemented skills and to proposed changes. Adding another skill requires an explicit project-scope decision; this document does not itself expand the catalog.

## Normative language

**MUST**, **MUST NOT**, **SHOULD**, and **MAY** express requirement levels in this document. A rule labeled **Specification** comes from the Agent Skills format. A rule labeled **Project** is an internal convention that improves consistency, safety, or portability but is not necessarily required by the open format.

## Requirements from the Agent Skills specification

Each skill:

- **MUST** be a directory containing a `SKILL.md` file.
- **MUST** begin `SKILL.md` with valid YAML frontmatter followed by Markdown content.
- **MUST** define `name` and `description` in the frontmatter.
- **MUST** use a `name` from 1 to 64 characters containing only lowercase Unicode alphanumeric characters and hyphens; it must not start or end with a hyphen or contain consecutive hyphens.
- **MUST** make `name` match the parent directory name.
- **MUST** use a non-empty `description` of at most 1,024 characters that explains what the skill does and when to use it.
- **MAY** use specification-defined optional fields such as `license`, `compatibility`, and `metadata` when justified and valid.
- **MAY** contain supporting directories such as `scripts/`, `references/`, and `assets/`.

The specification currently marks `allowed-tools` as experimental with potentially varying client support. Shared skills **MUST NOT** depend on it for safety or correctness. If a future adapter uses it, the core workflow must still state its real prerequisites and safety constraints.

The Markdown body has no mandatory section schema in the open specification. The structure below is therefore a project convention.

## Project conventions

### Location and naming

- A skill **MUST** live at `.agents/skills/<skill-name>/` as its canonical source.
- Names **MUST** be English ASCII kebab-case and describe the capability, not a platform or team. This is stricter than the specification's Unicode allowance.
- A skill **MUST** have one clearly bounded responsibility.
- Independently editable copies under platform-specific directories **MUST NOT** be maintained.

### Frontmatter

Start with the smallest portable frontmatter:

```yaml
---
name: example-skill
description: Perform a specific outcome. Use when the task has these explicit signals; do not use for this neighboring task.
---
```

The description **MUST** front-load concrete trigger terms, state the primary outcome, and distinguish close non-use cases when ambiguity is likely. This supports discovery from the metadata alone.

Optional standard fields **SHOULD** be omitted unless they convey useful information. Vendor-specific fields **MUST NOT** appear in the canonical shared file; place them in a future adapter or overlay. Metadata **MUST NOT** be used to hide behavioral requirements that belong in readable instructions.

### Instruction content

Each `SKILL.md` **MUST** state, using headings appropriate to the skill:

1. its responsibility and desired outcome;
2. when to use it and when not to use it;
3. prerequisites and required information;
4. an objective, ordered workflow;
5. how to validate the result;
6. how to handle failures, uncertainty, missing information, and known limitations.

Positive and negative examples **SHOULD** be included when they materially clarify triggering or expected behavior. Additional references **SHOULD** be included only when they improve execution.

Instructions **MUST** be concise, imperative, and observable. Avoid persona text, broad background material, repeated policy, and claims that cannot be checked.

### Progressive disclosure and reuse

Agents initially discover a skill from its name and description and load the full `SKILL.md` after selection. Authors therefore **MUST** keep discovery information in frontmatter and the essential workflow in `SKILL.md`.

Lengthy technical detail, domain tables, and uncommon branches **SHOULD** move to focused files under `references/`. `SKILL.md` **MUST** link directly to each reference and say when to read it. References **MUST NOT** be nested behind chains of unrelated documents.

Shared knowledge **MUST** have one authoritative home. Link to repository-wide guidance or an authoritative external source instead of copying it into several skills. A reference that serves only one skill belongs with that skill; repository-wide policy belongs in `docs/`.

### Guidance, verification, and command execution

Keep three concerns explicit:

- **Guidance** defines how to reason, choose an approach, and produce the deliverable.
- **Verification** defines evidence and acceptance checks without assuming they pass.
- **Execution** identifies commands or scripts, prerequisites, side effects, and expected outputs.

A workflow **MUST NOT** present a recommended check as if it were executed. It **MUST NOT** invent test results, diagnostic output, scan findings, file contents, or any other verification. When execution is unavailable, report the check as not run and explain why.

Commands **SHOULD** be optional when equivalent safe inspection is possible. Platform-specific shell syntax belongs in a targeted reference or adapter when it would reduce portability.

### Safety and failure behavior

Every skill **MUST** respect the host's permissions, sandbox, approval process, and security policies. A skill cannot grant authority or bypass an environment restriction.

The instructions **MUST**:

- prefer reversible and least-privilege actions;
- request explicit user confirmation before destructive or irreversible operations;
- identify material side effects before execution;
- stop safely when required authority, inputs, or capabilities are missing;
- distinguish observed facts from hypotheses and recommendations;
- preserve user work and avoid overwriting unrelated changes;
- avoid exposing secrets or sensitive environment data.

Failures **MUST** produce actionable context without fabricating success. Uncertainty **MUST** be stated, and validation depth **SHOULD** be proportional to the risk of the change.

### Supporting content

Add optional content only when it is used:

- `references/` for focused, on-demand documentation;
- `scripts/` for deterministic helpers that are safer or more reliable than re-generating commands;
- `assets/` for templates or files used in outputs.

Scripts **MUST** document dependencies and side effects, validate inputs, return meaningful failures, and avoid embedding credentials. They **MUST NOT** substitute for clear workflow instructions or rely on undeclared packages. Generated files **MUST** be identifiable and reproducible.

## Author checklist

Before proposing a skill, verify that:

- its directory and `name` match and meet the specification constraints;
- its YAML parses and contains a precise `description`;
- use and non-use boundaries are unambiguous;
- prerequisites, workflow, validation, failures, and limitations are covered;
- optional references and scripts are necessary, linked, and focused;
- no core behavior depends on proprietary fields or tools;
- commands disclose prerequisites and side effects;
- destructive actions require confirmation;
- every reported verification is based on observed execution;
- the skill does not duplicate another authoritative document.

Run the structural validator and test suite as described in [Validation and testing](validation.md). A clean structural result does not replace review of the workflow or behavioral evaluation with an agent.

## References

- [Agent Skills specification](https://agentskills.io/specification)
- [OpenAI: Build skills](https://developers.openai.com/codex/skills)
- [GitHub Copilot: Agent skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)
- [GitHub Copilot: Add agent skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- [Claude Code: Extend Claude with skills](https://code.claude.com/docs/en/skills)
