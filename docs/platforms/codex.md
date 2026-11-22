# OpenAI Codex

Codex is the priority platform for this catalog. The canonical `.agents/skills/` directory is a documented repository discovery location, so no adapter or generated copy is required when Codex works in this repository.

This is structural integration evidence, not a claim that every skill has been behaviorally evaluated. No completed Codex behavioral evaluation record is stored in this repository yet.

## Use in this repository

Clone the repository and start Codex from anywhere inside it. Codex scans `.agents/skills/` from the current working directory toward the repository root. It discovers each skill from its frontmatter and loads the full instructions and linked references only when needed.

Invoke a skill explicitly through the skills menu or by naming it with `$`, for example `$testing`. Codex may also select a skill from the task description. If a newly added skill is not visible, restart Codex after confirming that its `SKILL.md` passes validation.

## Use in another repository

Copy a complete selected directory, including its `references/`, to the target repository:

```text
your-project/
└── .agents/
    └── skills/
        └── testing/
            ├── SKILL.md
            └── references/
```

Alternatively, ask Codex's built-in skill installer to install a skill from this GitHub repository. The exact interaction depends on the installed Codex client; this project does not provide or claim a separate Codex installation CLI.

To update a copied installation, replace the complete selected skill directory from a reviewed repository revision. Review local modifications first: a manual copy has no ownership manifest and this repository's Claude installer does not manage Codex locations.

## Validation boundary

Run the repository's structural checks before using a changed skill. These checks validate metadata, references, catalog integrity, and documented scenarios. They do not prove correct discovery, activation, refusal, or output quality in a live Codex session. Record live runs using the [reproducible manual behavioral evaluation procedure](../validation.md#reproducible-manual-behavioral-evaluation).

## Official reference

- [OpenAI Codex: Agent Skills](https://developers.openai.com/codex/skills)
