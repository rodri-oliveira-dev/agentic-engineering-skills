---
name: docs
description: Create, review, or update technical software documentation, including READMEs, setup guides, API contracts, architecture descriptions, and decision records. Use for explicit documentation work or documentation synchronization after code changes; do not use for commit-only tasks, code-only refactoring, or feature implementation without a documentation deliverable.
---

# Technical documentation

## Outcome

Produce accurate, useful documentation grounded in observable repository evidence. Preserve the project's language, editorial style, terminology, and existing document organization.

## Use and non-use

Use this skill to create, review, or make focused updates to software documentation, especially installation and configuration guides, API or contract references, architecture descriptions, and technical decision records.

Do not activate it for tasks limited to commit messages or Git history, implementation or refactoring with no documentation deliverable, or general code review that does not evaluate documentation. A code change alone does not authorize an unrelated documentation rewrite.

## Required context

Identify the requested deliverable, intended audience, repository scope, and relevant change. Infer these from existing evidence when reliable; ask for information only when its absence prevents an accurate result. Treat repository files as the primary source and distinguish existing behavior from proposed behavior.

## Workflow

1. Define the audience and the question the document must answer. Choose the smallest suitable document type and location instead of adding redundant or decorative content.
2. Inspect relevant code, manifests, configuration, tests, examples, adjacent documentation, and change diffs. Follow project terminology and prefer implementation and executable contracts over assumptions.
3. Establish the documentation scope:
   - For installation and configuration, document observed prerequisites, supported setup paths, configuration keys, defaults, and verification steps.
   - For APIs and contracts, document observed entry points, inputs, outputs, errors, authentication, compatibility, and examples without inventing endpoints or behavior.
   - For architecture, explain component responsibilities, boundaries, dependencies, and important flows at the level the audience needs.
   - For decisions, record context, the chosen option, meaningful alternatives, trade-offs, consequences, and status. Label retrospective inference or proposals explicitly.
4. Compare existing documentation with the evidence and the relevant code changes. Identify stale statements, missing information, contradictions, and claims that cannot be verified.
5. Make focused edits. Preserve useful existing material and structure; do not rewrite an entire document when a local change is sufficient. Do not change production code merely to make it agree with the documentation.
6. Verify local links, file paths, identifiers, configuration names, and command syntax. Run safe, relevant commands or examples when permitted and proportionate. Mark every example not executed as unverified; never imply a check passed without observed evidence.
7. Review the final diff for audience fit, factual support, consistent language and style, unnecessary duplication, and accidental scope expansion. Summarize what changed, the evidence checked, validation actually performed, and remaining uncertainty.

## Uncertainty and limitations

- Never invent functionality, endpoints, dependencies, commands, results, or project intent.
- When evidence is missing or conflicting, state what was inspected, separate facts from hypotheses or proposals, and request only the minimum indispensable information.
- If a command, example, external link, or runtime behavior cannot be checked, report it as not verified and explain the constraint.
- Do not silently choose between conflicting authoritative sources; surface the conflict and its documentation impact.
- Respect host permissions, preserve unrelated user changes, and stop before any destructive or unauthorized action.
