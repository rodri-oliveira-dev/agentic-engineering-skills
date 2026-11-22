# Platform compatibility matrix

This matrix separates vendor support, repository structural evidence, and runtime behavior. A shared file format or documented discovery path does not by itself prove that a skill activates correctly or produces a useful result.

## Status definitions

- **Supported:** current official platform documentation recognizes the format, location, or workflow, and this repository uses it as documented.
- **Structurally validated:** deterministic repository checks verified metadata, layout, references, or generated-file integrity without exercising model behavior.
- **Not tested:** no controlled runtime test of skill activation and instruction-following has been completed on that platform surface.
- **Unsupported:** the platform does not document the named location or workflow as a discovery mechanism; an adapter or another supported path is required.

## Matrix

| Platform | Format recognition | Discovery directory | Installation | Structural validation | Execution tests performed | Known limitations |
| --- | --- | --- | --- | --- | --- | --- |
| OpenAI Codex | **Supported** — Agent Skills with `SKILL.md` frontmatter and Markdown instructions | **Supported** — canonical project catalog at `.agents/skills/` | **Supported** — repository checkout is sufficient; no adapter | **Structurally validated** — all ten canonical skills, metadata, names, references, and catalog integrity pass the repository validator | **Not tested** — Codex CLI 0.171.0-alpha.13 was run read-only and observed the ten directories, but no controlled activation or behavioral scenario was executed | Representative scenarios are documentation fixtures, not automated model evaluations; Codex remains the priority platform |
| GitHub Copilot | **Supported** — GitHub documents Agent Skills | **Supported** — `.agents/skills/` is a documented project location | **Structurally validated** — direct project discovery needs no adapter; `gh skill preview` 2.94.0 found the remote catalog with `--allow-hidden-dirs`; installation was not executed | **Structurally validated** — the canonical catalog passes shared metadata, structure, and reference checks; tests reject an independent `.github/skills/` tree | **Not tested** — Copilot CLI was not available, and no cloud, code-review, app, or IDE activation test was run | Surface and IDE-version support varies; personal local skills do not imply cloud availability; `gh skill` remains preview functionality |
| Claude Code | **Supported** — Anthropic documents the Agent Skills standard and supporting files | **Supported** at `.claude/skills/`; direct discovery from canonical `.agents/skills/` is **Unsupported**, so generated distribution is required | **Structurally validated** — the Python installer copies complete skills, tracks hashes, supports dry run/update/uninstall, and refuses unmanaged conflicts | **Structurally validated** — temporary-directory tests validate the generated catalog, byte equality, references, idempotence, invalid paths, and conflict handling; symlink-specific tests exist but were skipped locally where Windows denied symlink creation | **Not tested** — Claude Code was not installed, so discovery, `/skill-name`, automatic activation, and instruction-following were not run | Generated copies require explicit updates; personal skills differ from cloud/Cowork; canonical `debug` and `code-review` override bundled short names at the applicable precedence |

## Evidence recorded for this change

- `python scripts/validate_skills.py --require-skills` validates the non-empty canonical catalog.
- `python -m unittest discover -s tests -v` validates portable metadata, canonical discovery structure, generated distribution integrity, idempotence, and safety boundaries.
- A read-only `codex exec --ephemeral --sandbox read-only` run enumerated the ten directories under `.agents/skills/`; it did not test activation or workflow behavior.
- GitHub CLI 2.94.0 successfully previewed `code-review` from the remote hidden catalog with `--allow-hidden-dirs`; it did not install or invoke the skill in Copilot.
- Copilot CLI and Claude Code were not present in the validation environment.

## Official references

- [OpenAI: Build skills](https://developers.openai.com/codex/skills)
- [GitHub Copilot: Agent skills](https://docs.github.com/en/copilot/concepts/customizations/agent-skills)
- [GitHub Copilot: Add agent skills](https://docs.github.com/en/copilot/how-tos/copilot-on-github/customize-copilot/customize-cloud-agent/add-skills)
- [Claude Code: Extend Claude with skills](https://code.claude.com/docs/en/skills)
