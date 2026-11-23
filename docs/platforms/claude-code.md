# Claude Code

The canonical `.agents/skills/` catalog is structurally compatible with Claude Code's Agent Skills format. Claude Code discovers project skills under `.claude/skills/<skill-name>/SKILL.md`, so this repository provides a standard-library Python installer that creates a generated distribution in that location. For marketplace installation, the repository also provides `.claude-plugin/marketplace.json` and a generated plugin with a Claude compatibility manifest. The canonical skills remain unchanged and authoritative.

This support has two verified boundaries: the existing validator accepts all ten canonical skills, and isolated installer tests verify distribution and update behavior. Claude Code itself was not launched, so discovery, automatic activation, direct invocation, and workflow quality remain behaviorally unverified.

## Why the installer copies files

Claude Code supports a skill directory implemented as a symlink. The project does not use that mechanism by default because symlink creation, privileges, checkout behavior, and portability differ across Windows, macOS, and Linux.

The installer instead copies each complete skill directory and writes `.agentic-engineering-skills.json` in the destination. That manifest records SHA-256 hashes for generated files. On later runs, the installer:

- leaves identical files untouched;
- updates only files that still match the previously generated hash;
- removes obsolete generated files only when they remain unchanged;
- rejects unmanaged skill directories and files;
- rejects locally modified generated files;
- validates every planned path before writing;
- writes changed files and the manifest through same-directory temporary files.

Generated copies are distribution artifacts, not a second source. Make changes under `.agents/skills/` and rerun the installer. The root `.claude/skills/` path is ignored in this repository to prevent accidental commits of generated copies.

## Requirements

- Python 3.11 or newer;
- a checkout of this repository containing `.agents/skills/`;
- write access to the explicitly selected destination.

The installer itself uses only the Python standard library. Claude Code does not need to be installed to generate or test the distribution.

## Install through the plugin marketplace

The Claude Code catalog is `.claude-plugin/marketplace.json`. It declares the marketplace `agentic-engineering-skills` and one plugin, `agentic-engineering`, whose source is `./plugins/agentic-engineering` relative to the repository root. The generated package contains the ten skills under Claude's default `skills/` location. Its `.claude-plugin/plugin.json` carries only compatibility metadata; it does not declare hooks, commands, agents, MCP servers, authentication, or alternate skill paths.

After these files are published on the repository's default branch, register the marketplace and install the declared plugin with:

```shell
claude plugin marketplace add rodri-oliveira-dev/agentic-engineering-skills
claude plugin install agentic-engineering@agentic-engineering-skills
claude plugin list
claude plugin details agentic-engineering
```

The install identifier is exactly `agentic-engineering@agentic-engineering-skills`: Claude Code defines it as the marketplace entry name followed by `@` and the marketplace manifest name. The unpublished remote command was not executed. Claude Code was not available in the validation environment, so these commands are documented from the current official contract and the repository paths were verified offline, not claimed as a live install result. When the CLI is available, the corresponding pre-publication checks are `claude plugin validate .` and `claude plugin validate ./plugins/agentic-engineering`.

The documented maintenance commands are `claude plugin marketplace update agentic-engineering-skills`, `claude plugin update agentic-engineering@agentic-engineering-skills`, and `claude plugin uninstall agentic-engineering@agentic-engineering-skills`. They were not executed because Claude Code was unavailable. See [Installing and updating Agentic Engineering Skills](../distribution.md) for the full workflow, including marketplace removal, requirements, scopes, and permissions.

## Project installation

Preview all changes for another project:

```shell
python scripts/install_skills.py --platform claude-code --destination path/to/project/.claude/skills --all --dry-run
```

Install all canonical skills after reviewing the plan:

```shell
python scripts/install_skills.py --platform claude-code --destination path/to/project/.claude/skills --all
```

Install one skill and all of its associated references, scripts, and assets:

```shell
python scripts/install_skills.py --platform claude-code --destination path/to/project/.claude/skills --skill code-review
```

The destination must be the `skills` directory itself. The installer creates missing parent directories but never infers or writes a user configuration location.

## Personal installation

Claude Code documents personal skills under `~/.claude/skills/`. Pass that path explicitly so the same safety checks apply. Shell expansion of `~` is accepted, and the installer also expands it when the shell does not.

```shell
python scripts/install_skills.py --platform claude-code --destination ~/.claude/skills --all --dry-run
python scripts/install_skills.py --platform claude-code --destination ~/.claude/skills --all
```

Personal skills apply to local projects on that machine. Anthropic documents that local personal skills are not automatically available in Cowork or cloud sessions; project skills committed to a repository and skills enabled through a claude.ai account have different availability.

## Activation

Claude Code uses the frontmatter `description` to decide when a skill is relevant and loads the complete Markdown body when invoked. The canonical descriptions already state what each skill does and when to use it. No proprietary invocation fields are required.

After installation, Claude Code is expected to expose a skill by its name, such as `/code-review`. It may also activate a skill automatically from a matching request. Use `/skills` to inspect available skills in a Claude Code session. These runtime steps come from Anthropic's documentation and have not been executed as part of this repository's automated checks.

Claude Code also ships bundled skills named `debug` and `code-review`. Anthropic documents that an enterprise, personal, or project skill with the same name replaces the bundled command at that short name, while bundled aliases can remain available. Installing this catalog therefore intentionally makes `/debug` and `/code-review` resolve to the canonical project workflows at the applicable precedence level.

## Updating

Pull or otherwise update the canonical repository, preview the same command used for installation, and rerun it without `--dry-run`:

```shell
python scripts/install_skills.py --platform claude-code --destination path/to/project/.claude/skills --all --dry-run
python scripts/install_skills.py --platform claude-code --destination path/to/project/.claude/skills --all
```

An immediate repeated run reports `No changes required.` and does not rewrite identical files or the manifest. If a generated file was edited locally, installation stops with a clear error before applying any requested skill changes. Preserve the local work, move the edit back to the canonical source when appropriate, or remove the conflicting distribution only after reviewing it.

The installer does not automatically remove a managed skill that disappeared from the canonical catalog. This avoids silently broadening deletion scope. Uninstall that distribution explicitly.

## Safe uninstallation

Preview removal of one managed skill:

```shell
python scripts/install_skills.py --platform claude-code --destination path/to/project/.claude/skills --skill code-review --uninstall --dry-run
```

Remove it after review:

```shell
python scripts/install_skills.py --platform claude-code --destination path/to/project/.claude/skills --skill code-review --uninstall
```

Use `--all --uninstall` to remove every skill recorded by this installer's manifest. Uninstallation refuses to proceed when a managed file changed or the skill directory contains an unmanaged file, directory, or symlink. It removes the manifest when no managed skills remain and leaves the destination directory itself in place.

## Conflicts and recovery

The installer treats an existing skill directory without a matching manifest record as unmanaged, even if its contents happen to equal the canonical skill. It will not adopt or overwrite that directory automatically. Move or back up the directory, then retry.

Do not edit `.agentic-engineering-skills.json` manually. An invalid, unsupported, or unsafe manifest stops installation. Restore the matching manifest from backup or, after preserving any local content, remove the generated distribution and reinstall it into an empty destination.

Selection values must be direct ASCII kebab-case skill names. Values containing separators or traversal components are rejected. Manifest paths are independently checked to remain below the selected destination.

## Limitations

- Runtime discovery and behavior have not been tested with a Claude Code installation.
- The installer currently supports only the `claude-code` platform selector.
- Generated copies do not update automatically; rerun the installer after canonical changes.
- The installer rejects source symlinks rather than copying or dereferencing them.
- The canonical source catalog itself must be a real directory, not a symlink.
- The selected destination itself must not be a symlink; use the explicit real directory so path checks and ownership remain unambiguous.
- Claude Code reserves the skill directory names `synced` and `anthropic-skills`; the installer rejects those names. The current catalog uses neither.
- Personal local skills do not imply availability in Claude Code cloud or Cowork sessions.
- Claude Code-specific frontmatter, dynamic context injection, and `CLAUDE.md` files are intentionally not added. The marketplace package adds only the minimal `.claude-plugin/plugin.json` compatibility metadata.
- The manifest protects against accidental conflicts and edits; it is not a cryptographic trust or authentication mechanism.
- Do not run concurrent installer processes or use a destination that an untrusted process can mutate during installation; path and hash preflight is not a filesystem transaction or an operating-system security boundary.

## Official reference

- [Claude Code: Extend Claude with skills](https://code.claude.com/docs/en/skills)
- [Claude Code: Create a marketplace](https://code.claude.com/docs/en/plugin-marketplaces)
- [Claude Code: Plugin manifest reference](https://code.claude.com/docs/en/plugins-reference)
