# Roadmap

This roadmap communicates intended work, not delivery commitments. All ten planned skills are implemented and version `1.0.0` is published. Those facts do not imply completed behavioral, security, dependency, or cross-platform evaluation; compatibility is recorded only at the level supported by evidence.

## Planned skills

| Skill | Intended responsibility | Status |
| --- | --- | --- |
| `code-review` | Review changes for correctness, maintainability, risk, and actionable findings | Implemented |
| `refactor` | Improve internal code structure while preserving observable behavior | Implemented |
| `api-design` | Design and evaluate clear, evolvable API contracts | Implemented |
| `docs` | Create and maintain accurate software documentation | Implemented |
| `sql` | Develop and review safe, correct, and maintainable SQL | Implemented |
| `debug` | Investigate failures systematically and identify evidence-backed causes | Implemented |
| `testing` | Plan, write, and assess useful automated tests | Implemented |
| `security-review` | Identify and communicate security risks within an explicit scope | Implemented |
| `commits` | Prepare coherent changes and accurate commit messages | Implemented |
| `deployment-readiness` | Assess whether a change is ready for a controlled deployment | Implemented |

The responsibility statements are initial boundaries and will be refined during authoring without merging distinct skills into a generic workflow.

## Phases

### 1. Foundation

- Establish the canonical layout and shared architecture.
- Define the authoring, portability, validation, and safety contracts.
- Establish reusable structural validation and isolated CLI tests.
- Automate foundation checks and establish lightweight contribution governance.
- Document the planned skills and platform strategy.

### 2. Skill implementation for Codex

- Ten skills are authored under `.agents/skills/` and reviewed against the authoring contract.
- Supporting references remain scoped and dependency-free.
- Codex discovery uses the canonical repository location; behavioral evaluation remains part of the next phase.

### 3. Testing and refinement — ongoing

- **Current phase:** deterministic structural checks and representative fixtures exist for all ten skills; controlled behavioral execution remains pending.
- Expand static conformance checks and representative scenarios as new skills expose concrete needs.
- Evaluate triggering, non-triggering, normal, edge, and failure scenarios.
- Refine instructions using observed results rather than assumed behavior.
- Keep CI aligned with useful local checks and deterministic structural validation.

### 4. Copilot and Claude compatibility — structurally complete, runtime work ongoing

- **Copilot structural compatibility complete:** the canonical directory is officially supported, the catalog has been audited against the shared structure, and regression tests prevent a duplicated `.github/skills/` tree.
- Test canonical discovery, activation, and behavior across intended Copilot surfaces.
- **Claude structural distribution complete:** a tested Python installer generates `.claude/skills/` from the canonical catalog, preserves supporting files, and protects unmanaged or modified content.
- Test discovery, activation, and behavior across intended Claude Code surfaces.
- Isolate platform-specific extensions and document any behavioral differences.
- **Compatibility matrix published:** record official support, structural evidence, runtime checks, and limitations separately; update it as controlled platform testing becomes available.

### 5. Version 1.0 publication — published with outstanding readiness criteria

- **Completed implementation:** all planned skills and marketplace manifests were included in tag `1.0.0`; the GitHub Release and generated source archives were published on 2026-11-23.
- **Completed deterministic evidence:** exact-commit CI passed the repository's unit, structural, scenario-consistency, and package-integrity checks.
- **Partially complete installation evidence:** public Codex marketplace registration and isolated installation were validated after publication; Copilot CLI, Claude Code, and mutating universal-CLI installation remain unverified.
- **Outstanding quality work:** live-agent behavioral evaluation, complete dependency vulnerability/provenance assessment, remaining client workflows, and any release approval record remain unresolved.

The prerelease decision and its original evidence remain in [Version 1.0.0 readiness](releases/v1.0.0-readiness.md). The factual release state and unresolved criteria are recorded separately in the [Version 1.0.0 publication record](releases/1.0.0-publication.md). Publication does not retroactively prove compliance with the original criteria.

Phases may overlap for feedback, but compatibility and completion claims must not precede their validation evidence.
