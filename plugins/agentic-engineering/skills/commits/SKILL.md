---
name: commits
description: Prepare, organize, review, or create Git commits by inspecting working-tree and staged changes, separating unrelated work, and proposing project-compatible messages. Use when asked to plan, stage, review, or make local commits; do not use for remote publication alone or general implementation without commit work.
---

# Git commits

## Outcome

Produce focused, reviewable local commits that preserve existing work, exclude sensitive or unrelated files, and follow the repository's message conventions. Treat inspection, staging, commit creation, history rewriting, and remote publication as distinct operations with distinct authorization.

## Use and non-use

Use this skill to inspect commit readiness, organize changes, suggest messages, prepare staging, review staged content, or create a requested local commit.

Do not activate it for implementation with no commit-related request, documentation work alone, or remote publication that does not involve commit preparation. Skill activation itself authorizes only read-only inspection.

## Authorization boundaries

- **Message suggestion:** Inspect relevant context and return candidate text; do not stage, commit, or push.
- **Preparation:** Propose groups and exact files or hunks. Stage or unstage only when the user's request authorizes that working-tree index change.
- **Commit creation:** Run `git commit` only when the user explicitly requests or authorizes creating the local commit. Authorization to commit does not authorize amend, rebase, reset, push, or force push.
- **Remote publication:** Push only under a separate explicit request. Never infer push authorization from a request for a local commit.

Before any write, confirm that the requested operation, repository, and intended change group are clear. Explain material side effects and stop when authority is missing.

## Workflow

1. Inspect the branch and repository state, including tracked, untracked, modified, and staged files. Compare both unstaged and staged diffs; do not assume the index matches the working tree.
2. Establish the requested change's purpose from the user's task, diffs, tests, and nearby project context. Inspect recent commit history and contribution guidance for repository-specific message conventions.
3. Classify each changed path or hunk as part of the requested change, a necessary companion such as a lockfile, unrelated existing work, generated output, or uncertain. Preserve unrelated work and ask only when uncertainty prevents safe grouping.
4. Screen filenames and diffs for credentials, tokens, private keys, local environment files, personal data, machine-specific configuration, caches, logs, and unexpected binaries or generated artifacts. Do not expose secret values while reporting a concern. Exclude suspicious content and stop for user review.
5. Propose the smallest coherent groups that can be understood, tested, and reverted independently. Keep tests and documentation with the behavior they directly verify or explain unless the repository convention calls for separate commits.
6. Review the exact staged diff before commit creation. Never use `git add .` indiscriminately; prefer explicit paths or deliberate interactive hunk selection. Do not discard working-tree changes to simplify staging.
7. Propose a concise message that describes the observed intent. Follow repository conventions first; when none are evident, suggest Conventional Commits using the guidance below.
8. If local commit creation is authorized, run only the staging and commit operations covered by that authorization. Report hooks or failures truthfully; never bypass checks or claim tests ran without observed evidence.
9. Verify the resulting commit and final Git state: inspect the committed paths and summary, confirm unrelated changes remain preserved, and report remaining staged, unstaged, and untracked files. Do not push unless separately authorized.

## Conventional Commits guidance

Use `type(scope)!: summary` when compatible with the project. Keep the scope optional and use it only for a stable component or area that improves clarity. Use `!` only for a real compatibility break and add a `BREAKING CHANGE:` footer describing the impact and required migration.

- `feat`: add user-visible capability.
- `fix`: correct faulty behavior.
- `docs`: change documentation only.
- `refactor`: restructure code without changing intended behavior.
- `test`: add or correct tests without changing production behavior.
- `build`: change build systems, packaging, or dependencies.
- `ci`: change continuous-integration configuration or automation.
- `chore`: perform maintenance not better represented by another type.
- `perf`: improve performance without changing intended behavior.
- `revert`: reverse an earlier commit and identify it in the body when useful.

Do not label a change as breaking merely because it is large. Inspect public APIs, persisted data, configuration, supported workflows, and compatibility contracts. Use a body or standard footers when rationale, migration, issue references, or breaking impact cannot fit clearly in the subject; do not invent a proprietary message format.

## Safety and failure handling

- Never include secrets, credentials, or sensitive local files. If such content is staged, warn without reproducing it and do not commit until it is safely excluded under appropriate authorization.
- Never discard existing changes. Do not run `git reset --hard`, `git clean -fd`, history rewrites, amend, rebase, or force push without specific explicit authorization for that operation and understood consequences.
- Do not broaden a path-based staging request, silently combine independent changes, or overwrite another contributor's work.
- If there are no changes, report the clean state and do not create an empty commit unless the user explicitly requests one and understands the purpose.
- If project conventions, change intent, or breaking impact cannot be established, present the evidence and uncertainty instead of guessing.
- Report only tests, hooks, commits, and pushes actually observed. A successful commit does not prove tests passed.
