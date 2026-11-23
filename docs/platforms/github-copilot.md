# GitHub Copilot

The canonical `.agents/skills/` catalog is structurally compatible with GitHub Copilot and remains optimized first for OpenAI Codex. GitHub documents `.agents/skills/` as a supported project location, so this repository does not duplicate skills under `.github/skills/` and does not need a Copilot-specific adapter.

This compatibility statement is intentionally narrow. The repository validator and automated tests check the shared file structure, YAML frontmatter, names, descriptions, catalog integrity, and relative references. They do not prove that every Copilot surface discovers, activates, or executes every workflow correctly. No controlled behavioral run of this catalog on Copilot has been recorded yet.

## Supported catalog

The repository currently contains these ten skills:

- `api-design`
- `code-review`
- `commits`
- `debug`
- `deployment-readiness`
- `docs`
- `refactor`
- `security-review`
- `sql`
- `testing`

Each directory contains one canonical `SKILL.md`. Some skills also contain relative `references/`; keep the complete skill directory together so those links continue to resolve.

## Install through the plugin marketplace

The Copilot CLI catalog is `.github/plugin/marketplace.json`. It declares the marketplace `agentic-engineering-skills` and one plugin, `agentic-engineering`, whose source is `./plugins/agentic-engineering` relative to the repository root. The package uses the Agent Plugins 1.0 root `plugin.json`; Copilot gives that portable manifest precedence over legacy manifests and discovers all ten generated skills in its fixed `skills/` directory. No Copilot-specific manifest or `copilot-instructions.md` is needed.

After these files are published on the repository's default branch, register the marketplace and install the declared plugin with:

```shell
copilot plugin marketplace add rodri-oliveira-dev/agentic-engineering-skills
copilot plugin marketplace browse agentic-engineering-skills
copilot plugin install agentic-engineering@agentic-engineering-skills
copilot plugin list
```

The install identifier is exactly `agentic-engineering@agentic-engineering-skills`: the portion before `@` is the plugin entry name and the portion after it is the marketplace manifest name. The unpublished remote command was not executed. Copilot CLI was not available in the validation environment, so these commands are documented from the current official CLI contract and the repository paths were verified offline, not claimed as a live install result.

The documented maintenance commands are `copilot plugin marketplace update agentic-engineering-skills`, `copilot plugin update agentic-engineering@agentic-engineering-skills`, and `copilot plugin uninstall agentic-engineering@agentic-engineering-skills`. They were not executed because Copilot CLI was unavailable. See [Installing and updating Agentic Engineering Skills](../distribution.md) for the full workflow, including marketplace removal, requirements, and permissions.

## Project installation

When using this repository itself, no installation step is required: Copilot can discover the checked-in `.agents/skills/` directory.

To use one or more skills in another repository, copy each selected skill directory, including all of its contents, into that repository's `.agents/skills/` directory:

```text
your-project/
└── .agents/
    └── skills/
        ├── code-review/
        │   ├── SKILL.md
        │   └── references/
        └── testing/
            └── SKILL.md
```

Do not create a second copy under `.github/skills/`. GitHub supports `.agents/skills/` directly, and one location avoids ambiguous discovery and content drift.

GitHub CLI 2.90.0 or newer also provides the public-preview `gh skill` workflow. Inspect a skill before installation, then install it at project scope:

```shell
gh skill preview rodri-oliveira-dev/agentic-engineering-skills code-review --allow-hidden-dirs
gh skill install rodri-oliveira-dev/agentic-engineering-skills code-review --allow-hidden-dirs
```

GitHub documents Copilot project scope as the default. The `--allow-hidden-dirs` option is required because the canonical catalog is below the hidden `.agents/` directory. Remote preview has been verified with GitHub CLI 2.94.0; installation was not executed because it would modify the checkout. The manual directory layout above is the format covered by local tests.

For a skill installed by this preview workflow, GitHub CLI documents `gh skill update` as the update command. Preview the source again and review local work before updating; this repository has not executed or verified the mutating install/update path.

## User installation

For local personal skills shared across projects, GitHub documents `~/.copilot/skills/` and `~/.agents/skills/`. Copy complete skill directories into one of those locations, or use the public-preview GitHub CLI installer with user scope:

```shell
gh skill preview rodri-oliveira-dev/agentic-engineering-skills testing --allow-hidden-dirs
gh skill install rodri-oliveira-dev/agentic-engineering-skills testing --scope user --allow-hidden-dirs
```

Personal skill availability varies by Copilot surface. In particular, a skill installed in a local home directory must not be assumed to exist in a cloud sandbox. Follow the setup guidance for the surface you use; GitHub documents a separate dotfiles mechanism for making personal skills available to supported cloud sandbox sessions.

## Activation and verification

Copilot selects skills from the task and the frontmatter `description`. Make the request explicit enough to match the intended skill. In Copilot CLI, a skill can also be named with a slash, for example:

```text
Use the /code-review skill to review the current diff for actionable defects.
```

Within an interactive Copilot CLI session:

- `/skills list` lists available skills;
- `/skills info code-review` shows the selected skill and its location;
- `/skills reload` reloads skills added during the current session;
- `/skills` enables or disables an available skill.

The equivalent terminal commands include `copilot skill list`, `copilot skill enable SKILL-NAME`, and `copilot skill disable SKILL-NAME`.

For a project checkout, verify structural compatibility independently of Copilot with:

```shell
python scripts/validate_skills.py --require-skills
python -m unittest discover -s tests -v
```

A successful result verifies repository structure only. To verify execution on a specific Copilot surface, confirm discovery there, invoke a representative task, record whether the intended skill was loaded, and compare the observed output with the relevant scenario under `tests/fixtures/`.

## Limitations and security

- Copilot support and management controls vary across the app, CLI, cloud agent, code review, and IDE agent modes; IDE support also depends on version.
- Personal local skills are not automatically available to every cloud-hosted session.
- Copilot decides automatic activation from the prompt and `description`; structural validity does not guarantee activation quality.
- The catalog has no executable skill scripts and does not use `allowed-tools`. If either is added later, host permissions and confirmation behavior must be reviewed separately.
- Skills are instructions, not a permission boundary. Review third-party skill contents before installation and retain the host's approval and security controls.
- OpenAI Codex remains the priority platform. Copilot-specific behavior must not weaken the portable core or introduce an independently maintained copy.

## Official references

- [GitHub Copilot: Agent skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)
- [GitHub Copilot: Adding agent skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- [GitHub Copilot CLI: Adding agent skills](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/add-skills)
- [GitHub Copilot CLI: Plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)
