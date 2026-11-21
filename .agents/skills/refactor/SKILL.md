---
name: refactor
description: Restructure existing code to improve maintainability while preserving observable behavior and compatibility. Use for behavior-preserving cleanup of design, duplication, coupling, or complexity; do not use primarily to fix defects, add features, or claim performance optimization.
---

# Refactoring

## Outcome

Improve a demonstrated maintenance problem through small, reversible changes while preserving observable behavior, public contracts, and compatibility with existing consumers. Prefer the simplest design improvement supported by repository evidence.

## Use and non-use

Use this skill when the requested outcome is clearer structure, lower unnecessary coupling, higher cohesion, reduced duplication or complexity, or improved testability without intentionally changing behavior.

Do not activate it when the primary outcome is a bug fix, new functionality, dependency upgrade, style-only rewrite, or performance optimization. Separate those concerns when they coexist, and do not disguise behavior changes as refactoring.

## Required evidence

Identify the maintenance problem, requested scope, affected code, current tests, known consumers, and repository conventions. Treat a design principle or personal preference as a possible lens, not evidence of a defect. If existing behavior or compatibility obligations cannot be characterized well enough for the risk, inspect further or add focused characterization tests before changing the code.

## Workflow

1. State the concrete maintenance problem and why it matters. Distinguish excessive responsibility, coupling, duplication, low cohesion, complex flow, poor naming, or hard-to-test boundaries from harmless stylistic differences.
2. Inspect the current implementation, call sites, tests, documentation, configuration, data formats, and relevant change history. Record the baseline repository state and preserve unrelated work.
3. Map contracts and dependencies across the proposed boundary, including public and internal consumers, external services, generated code, plugins, and versioned interfaces.
4. Define observable invariants before editing: accepted inputs, outputs, ordering, errors, state transitions, side effects, compatibility, and resource or concurrency semantics relevant to the change.
5. Assess risk and validation strength. Consider reach, contract visibility, legacy behavior, test coverage, stateful data, concurrency, rollback difficulty, and the cost of failure. Do not treat successful compilation as behavioral equivalence.
6. Select a proportional strategy. Prefer a local rename, extraction, movement, simplification, or deduplication when it solves the demonstrated problem. Use responsibility separation, new abstractions, or architectural boundaries only when evidence justifies their additional complexity.
7. Establish a safety net with existing tests or focused characterization and regression tests. Characterization tests should capture important current behavior without declaring every accidental implementation detail permanent.
8. Apply one coherent, reversible change at a time. Keep diffs narrow, preserve interfaces where possible, and re-check affected call sites after each meaningful step. Avoid opportunistic cleanup outside the requested scope.
9. Run the most relevant available checks, progressing from focused tests to broader suites, build, static analysis, integration checks, or compatibility tests as risk warrants. Add specialized validation for persistence, serialization, or concurrency when those contracts are touched.
10. Compare the final behavior, contracts, tests, and diff with the baseline. Report what changed structurally, what remained invariant, checks actually executed and their observed results, unresolved risks, and any follow-up that should remain separate.

## Behavior and compatibility safeguards

- **Public APIs:** Preserve names, signatures, defaults, return semantics, ordering, and documented behavior. Treat a required API change as a separate, explicit compatibility decision with migration planning.
- **Serialization:** Preserve field names, types, nullability, defaults, encodings, and format/version expectations used by readers and writers.
- **Persistence:** Preserve schemas, keys, constraints, transaction behavior, stored representations, and migration compatibility. Do not rewrite persistent data implicitly.
- **Exceptions:** Preserve externally observed error categories, timing, propagation, and relied-upon details. Do not broaden catches or suppress failures merely to simplify control flow.
- **Concurrency:** Preserve atomicity, ordering, synchronization, cancellation, reentrancy, and thread or task safety. Treat changes to shared mutable state or timing as high risk.
- **Side effects:** Preserve which external actions occur, their order, frequency, idempotency, and failure behavior.
- **Versions and consumers:** Check supported runtimes, protocols, extensions, and downstream callers; avoid silently requiring a newer dependency or platform.
- **Regression evidence:** Retain existing tests and add focused coverage for exposed risks. Never delete or weaken a test merely to make validation pass.

## Engineering criteria

Favor cohesion, legibility, simplicity, testability, incremental evolution, and reduced unnecessary coupling. Apply single responsibility only when distinct reasons to change or mixed concerns are observable. Do not impose SOLID, Clean Architecture, DDD, patterns, layers, or generic abstractions without showing the concrete problem they solve. Avoid premature abstraction and avoid reporting subjective style preferences as architectural defects.

## Limits and uncertainty

- Respect the requested scope; do not expand a local improvement into a broad rewrite without evidence and authorization.
- Preserve unrelated changes and do not update dependencies unless the refactoring demonstrably requires it and the scope permits it.
- Do not alter public contracts silently, remove tests, or accept failing checks as proof of preservation.
- Do not claim performance improvement without representative measurement, or behavioral equivalence from compilation alone.
- For high-risk or weakly characterized code, present safer alternatives, narrow the change to what can be validated, or stop before editing.
- Report checks not run and why. Never fabricate results, and do not commit or push automatically.
