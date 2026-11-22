# Roadmap

This roadmap communicates intended work, not delivery commitments. All ten planned skills are implemented; this status records authored and structurally validated content, not completed behavioral or cross-platform evaluation. Platform compatibility will be recorded only after evidence-based testing, and the catalog is not yet a published 1.0 release.

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

### 3. Testing and refinement

- **Current phase:** deterministic structural checks and representative fixtures exist for all ten skills; controlled behavioral execution remains pending.
- Expand static conformance checks and representative scenarios as new skills expose concrete needs.
- Evaluate triggering, non-triggering, normal, edge, and failure scenarios.
- Refine instructions using observed results rather than assumed behavior.
- Keep CI aligned with useful local checks and deterministic structural validation.

### 4. Copilot and Claude compatibility

- Test canonical discovery and behavior across intended Copilot surfaces.
- Implement and test a non-duplicating adapter for Claude Code's discovery location.
- Isolate platform-specific extensions and document any behavioral differences.
- Publish an evidence-based compatibility matrix.

### 5. Version 1.0 publication

- Confirm all planned skills meet the stable authoring contract.
- Complete security, licensing, documentation, and cross-platform reviews.
- Document installation or distribution paths that have been tested.
- Publish release notes and a stable compatibility statement.

Phases may overlap for feedback, but compatibility and completion claims must not precede their validation evidence.
