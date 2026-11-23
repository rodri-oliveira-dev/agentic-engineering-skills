# Installing and updating Agentic Engineering Skills

This guide is for users of the public `rodri-oliveira-dev/agentic-engineering-skills` repository. The ten workflows can be installed either as individual Agent Skills with the cross-agent `skills` CLI or together as the `agentic-engineering` marketplace plugin.

The repository's only editable skill source is `.agents/skills/`. Marketplace packages under `plugins/` are deterministic generated artifacts containing the same files. The plugin install identifier is `agentic-engineering@agentic-engineering-skills` on every supported marketplace.

## Universal Agent Skills installation

The `skills` CLI requires Node.js with `npx`. Its current documentation does not declare a minimum Node.js version, so use a maintained Node.js release and check the installed CLI before relying on optional flags:

```shell
node --version
npx skills --help
```

List this repository's skills without installing anything:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --list
```

On 2026-11-23, the equivalent local-checkout command `npx --yes skills@latest add . --list` ran with Node.js 24.22.3 and npm/npx 11.19.1, found exactly ten skills, and exited `0`. It did not install a skill. The remote `owner/repo` form remains unverified until the marketplace changes are published.

Install one skill and choose its target agents interactively:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --skill code-review
```

Select agents explicitly when you need a reproducible target. Repeat `--agent` for multiple agents:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --skill testing --agent codex --agent claude-code
```

Install all ten skills only after reviewing the source and destinations:

```shell
npx skills add rodri-oliveira-dev/agentic-engineering-skills --all
```

Project scope is the default; `--global` installs for the current user. The CLI may offer symlinks or copies depending on the target. Use `--copy` when the environment cannot create or preserve symlinks.

Check for updates and then update all project skills or one named skill:

```shell
npx skills check
npx skills update --project
npx skills update code-review
```

Remove one installed skill or everything tracked from this source:

```shell
npx skills remove code-review
npx skills remove rodri-oliveira-dev/agentic-engineering-skills
```

The `skills` CLI records installations in `skills-lock.json`; review local modifications before updating or removing tracked content. Private repository sources may require existing Git, GitHub CLI, SSH, `GH_TOKEN`, or `GITHUB_TOKEN` authentication. This public repository does not require repository credentials for ordinary anonymous access.

## Marketplace installation

Marketplace registration writes to the selected agent's user configuration and requires network access to GitHub for the `owner/repo` form. The commands below become remotely usable only after the marketplace files are published on the repository's default branch. This repository has no plugin authentication, MCP server, hook, or executable installation command.

### OpenAI Codex

Check the installed CLI and register the marketplace:

```shell
codex --version
codex plugin marketplace add rodri-oliveira-dev/agentic-engineering-skills
codex plugin marketplace list
codex plugin list --marketplace agentic-engineering-skills --available --json
codex plugin add agentic-engineering@agentic-engineering-skills
```

The current tested CLI is `codex-cli 0.171.0-alpha.13`; the official plugin documentation does not state a minimum Codex CLI version for repository marketplaces. Use `codex plugin --help` to confirm support. Start a new session after installation and enter `/plugins` to inspect the plugin.

Refresh the Git marketplace snapshot:

```shell
codex plugin marketplace upgrade agentic-engineering-skills
```

This tested CLI has no `codex plugin update` subcommand. Use the `/plugins` browser when it offers an update, or explicitly remove and reinstall the plugin after refreshing the marketplace:

```shell
codex plugin remove agentic-engineering@agentic-engineering-skills
codex plugin add agentic-engineering@agentic-engineering-skills
```

Remove the plugin before unregistering its marketplace:

```shell
codex plugin remove agentic-engineering@agentic-engineering-skills
codex plugin marketplace remove agentic-engineering-skills
```

### GitHub Copilot CLI

The current official CLI reference documents `plugin marketplace` and Agent Plugins 1.0 but does not declare a minimum Copilot CLI version for them. Confirm support before registration:

```shell
copilot --version
copilot plugin --help
copilot plugin marketplace add rodri-oliveira-dev/agentic-engineering-skills
copilot plugin marketplace browse agentic-engineering-skills
copilot plugin install agentic-engineering@agentic-engineering-skills
copilot plugin list
```

Refresh the catalog and update the installed plugin:

```shell
copilot plugin marketplace update agentic-engineering-skills
copilot plugin update agentic-engineering@agentic-engineering-skills
```

Remove the plugin before unregistering the marketplace:

```shell
copilot plugin uninstall agentic-engineering@agentic-engineering-skills
copilot plugin marketplace remove agentic-engineering-skills
```

Copilot may retry a failed HTTPS fetch with the authenticated GitHub account. Access to private marketplaces therefore depends on the user's GitHub authentication and organization policy. This marketplace is intended to be public.

### Claude Code

The basic marketplace commands below have no minimum Claude Code version stated in the current command reference. Confirm that the installed release provides them:

```shell
claude --version
claude plugin --help
claude plugin marketplace add rodri-oliveira-dev/agentic-engineering-skills
claude plugin install agentic-engineering@agentic-engineering-skills
claude plugin list
claude plugin details agentic-engineering@agentic-engineering-skills
```

Refresh the marketplace and update the plugin:

```shell
claude plugin marketplace update agentic-engineering-skills
claude plugin update agentic-engineering@agentic-engineering-skills
```

Remove the plugin before unregistering the marketplace:

```shell
claude plugin uninstall agentic-engineering@agentic-engineering-skills
claude plugin marketplace remove agentic-engineering-skills
```

Claude installs at user scope by default. Pass `--scope project` or `--scope local` only after reviewing which settings file will change. Organization policy can restrict marketplace sources, scopes, or plugins.

## Requirements and limitations

| Path | Requirements | Permissions and limitations |
| --- | --- | --- |
| Universal `npx skills` | Maintained Node.js distribution with `npx`; Git/network access for a remote source | Writes skill directories and `skills-lock.json`; global scope needs write access to the user's agent directories; symlink support varies by operating system |
| Codex marketplace | Codex CLI with `plugin marketplace`; Git/network access | Writes below the isolated or user `CODEX_HOME`; remote registration is not verified before publication; IDE extension plugin support is not documented |
| Copilot marketplace | Copilot CLI with `plugin marketplace`; Git/network access | Writes Copilot user configuration/cache; CLI was unavailable in the project validation environment; other Copilot surfaces have different support |
| Claude marketplace | Claude Code with `plugin marketplace`; Git/network access | Writes Claude settings and plugin cache at the selected scope; CLI and native `plugin validate` were unavailable in the project validation environment |
| Package generation | Python 3.11 or newer | Uses only the Python standard library; run from a trusted checkout; edit `.agents/skills/`, never the generated package |

The marketplace plugin always installs all ten skills. Use the universal Agent Skills route for a subset. Structural validation proves the manifests, paths, hashes, and file equality; it does not prove automatic activation or model behavior on any agent.

## Maintainer verification

From a repository checkout:

```shell
python scripts/validate_skills.py --require-skills
python -m unittest discover -s tests -v
python scripts/package_plugins.py check
python scripts/package_plugins.py verify
```

When their CLIs are available, validate marketplaces in isolated configuration directories before publication. Never use a successful offline validator as a substitute for a native CLI result.

## References

- [Vercel `skills` CLI reference](https://github.com/vercel-labs/skills/blob/main/docs/commands.md)
- [OpenAI plugins documentation](https://developers.openai.com/codex/plugins)
- [GitHub Copilot CLI plugin reference](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-plugin-reference)
- [Claude Code marketplace guide](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code plugin commands](https://code.claude.com/docs/en/plugins/cli-reference)
- [Agent Plugins specification](https://agent-plugins.org/specification)
