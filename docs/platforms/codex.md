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

## Install through the plugin marketplace

The repository marketplace at `.agents/plugins/marketplace.json` exposes one plugin named `agentic-engineering`. Its portable Agent Plugins 1.0 manifest is at `plugins/agentic-engineering/plugin.json`, and the package's fixed `skills/` directory is generated from all ten canonical skills.

After a revision containing these files is published, the intended registration command is:

```shell
codex plugin marketplace add rodri-oliveira-dev/agentic-engineering-skills
```

Then open `/plugins` in Codex CLI and select the `agentic-engineering-skills` marketplace, or inspect it non-interactively:

```shell
codex plugin list --marketplace agentic-engineering-skills --available
```

The plugin identifier is `agentic-engineering@agentic-engineering-skills`. The remote `owner/repo` registration cannot be validated until the revision is published. Do not treat the local validation below as proof that the unpublished remote command already works.

For the complete installation, refresh, removal, requirements, and permissions workflow, see [Installing and updating Agentic Engineering Skills](../distribution.md). In `codex-cli 0.171.0-alpha.13`, refresh a Git marketplace with `codex plugin marketplace upgrade agentic-engineering-skills`; this version has no `codex plugin update` subcommand, so update through `/plugins` when offered or remove and add the plugin again after the refresh.

### Observed local CLI validation

On 2026-11-23, `codex-cli 0.171.0-alpha.13` was tested with `CODEX_HOME` set to a newly created temporary directory. The following commands were executed against this checkout:

```powershell
codex --version
codex plugin marketplace add C:\estudos\agentic-engineering-skills --json
codex plugin marketplace list
codex plugin list --marketplace agentic-engineering-skills --available --json
codex plugin add agentic-engineering@agentic-engineering-skills --json
codex plugin list --marketplace agentic-engineering-skills --json
python scripts/package_plugins.py verify --package <temporary-installed-path>
```

Observed results: the marketplace resolved to this repository root; the plugin appeared as available at `plugins/agentic-engineering`; installation copied it below the temporary `CODEX_HOME`; the installed plugin was enabled; exactly ten skill directories were present; and the installed package passed its SHA-256 inventory verification. A second check copied only `.agents/plugins/marketplace.json` and `plugins/agentic-engineering/` to a different temporary marketplace root, then repeated `marketplace add`, `plugin list`, and `plugin add`; Codex resolved the source below the relocated root and again installed ten skills. The temporary directories were removed after the checks. The interactive `/plugins` browser, the unpublished GitHub source, and behavioral skill activation were not exercised.

## Validation boundary

Run the repository's structural checks before using a changed skill. These checks validate metadata, references, catalog integrity, and documented scenarios. They do not prove correct discovery, activation, refusal, or output quality in a live Codex session. Record live runs using the [reproducible manual behavioral evaluation procedure](../validation.md#reproducible-manual-behavioral-evaluation).

## Official reference

- [OpenAI Codex: Agent Skills](https://developers.openai.com/codex/skills)
- [OpenAI: Plugins in ChatGPT and Codex](https://developers.openai.com/codex/plugins)
- [OpenAI: Package your plugin](https://developers.openai.com/plugins/build/plugins)
