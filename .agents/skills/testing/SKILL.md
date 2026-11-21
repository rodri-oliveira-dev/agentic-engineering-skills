---
name: testing
description: Plan, implement, run, or review automated tests using behavior and risk to select useful coverage. Use when asked to add tests, choose test levels, investigate test failures, or assess test quality; do not use for production implementation alone, debugging without a testing outcome, or manual QA only.
---

# Automated testing

## Outcome

Create reliable tests that provide useful evidence about observable behavior and meaningful risks at a cost appropriate to the project. Prefer the lowest-cost test level that exercises the relevant contract with sufficient confidence, without treating any fixed test pyramid or coverage percentage as a universal goal.

## Use and non-use

Use this skill to plan, write, run, repair, or assess automated tests; reproduce behavior with a regression test; evaluate coverage gaps; or improve a test suite's reliability.

Do not activate it for feature implementation with no testing deliverable, root-cause debugging that does not require test work, manual exploratory QA alone, or performance and security assessment that requires a specialized workflow. Do not change production behavior merely to satisfy an artificial test.

## Required context

Identify the behavior or contract to verify, affected code, change intent, failure history, consumers, existing test conventions, supported environments, and available commands. Inspect the repository before choosing frameworks or patterns. Separate confirmed behavior from assumptions and preserve unrelated work.

## Workflow

1. State the behavior, invariant, regression, or risk the test must provide evidence about. Define what failure should mean to a maintainer.
2. Inspect the implementation, public contracts, call sites, existing tests, fixtures, test configuration, and recent changes. Reuse project conventions and helpers when they remain clear and trustworthy.
3. Assess risk using impact, likelihood, change reach, statefulness, concurrency, external integration, compatibility, and prior defects. Let risk determine depth rather than maximizing test count.
4. Derive representative scenarios: normal paths, boundaries, invalid input, exceptions, state transitions, retries, and regressions. Use parameterization when cases share behavior and remain readable.
5. Select test levels by the contract under test, feedback speed, reliability, diagnostic value, and maintenance cost. Combine levels only when each catches a distinct material risk; do not impose a universal pyramid.
6. Identify external dependencies such as databases, filesystems, clocks, randomness, networks, processes, queues, and third-party services. Decide deliberately whether to use a real dependency, controlled substitute, fake, stub, or mock at a stable boundary.
7. Prepare minimal, explicit data and fixtures. Control time, random seeds, identifiers, locale, environment, and cleanup where relevant. Avoid shared mutable state and order dependence.
8. Implement tests around observable outcomes: returned values, state changes, emitted events, persisted data, external calls at owned boundaries, or documented errors. Use meaningful assertions and keep setup readable.
9. Run the narrowest relevant tests, then broader checks warranted by risk. Record the exact commands and observed results. Distinguish assertion failures from setup, environment, timeout, infrastructure, and flaky failures before changing code.
10. Compare results with the intended contract. Identify real defects, incorrect expectations, unstable tests, and remaining coverage gaps. Report what was and was not exercised; never infer total quality from compilation, one passing test, or coverage percentage alone.

## Test strategy guidance

- **Unit tests:** Exercise cohesive logic quickly with controlled collaborators when isolation improves diagnosis without replacing meaningful behavior with mock choreography.
- **Integration tests:** Verify real boundaries such as persistence, serialization, framework configuration, or component collaboration where substitutes would hide material risk.
- **Contract tests:** Check provider and consumer expectations, schemas, compatibility, and failure semantics at integration boundaries.
- **End-to-end tests:** Reserve for critical cross-system journeys that need deployed wiring; keep the set focused because setup and diagnosis are costly.
- **Regression tests:** Reproduce an observed defect before or alongside the fix and fail for the correct reason on the faulty behavior.
- **Parameterized tests:** Cover meaningful input classes compactly; keep case names and expected outcomes understandable.
- **Edge and exception tests:** Exercise limits, empty or malformed input, overflow, partial state, error mapping, cleanup, and recovery according to risk.
- **Concurrency tests:** Check atomicity, ordering, cancellation, races, deadlocks, and shared-state invariants with appropriate tooling and repeatable coordination rather than timing luck.
- **Asynchronous tests:** Await observable completion, control schedulers or clocks when practical, bound eventual assertions, and propagate task failures.
- **Characterization tests:** Capture important current legacy behavior before risky change while avoiding accidental internals that need not become permanent contracts.

## Quality safeguards

- Assert behavior precisely enough that an incorrect implementation fails. Avoid trivial existence checks and tests that only verify mocks were called without a relevant outcome.
- Keep tests deterministic, isolated at the appropriate boundary, reproducible, legible, and resistant to legitimate internal refactoring.
- Prefer controlled signals, fake clocks, latches, events, or bounded polling over real-time dependence and indiscriminate sleeps.
- Make fixtures local or safely scoped, use realistic minimal data, and clean up resources even when the test fails.
- Do not depend on execution order, live mutable services, undeclared machine state, or network availability unless the test is explicitly an integration check with managed prerequisites.
- Do not weaken assertions, delete tests, ignore failures, or modify production code solely to make a misleading test pass.
- Treat line or branch coverage as navigation evidence, not a standalone quality score. Examine which behaviors and risks remain untested.

## Failure handling and limits

- Reproduce a failing test before classifying it. If it exposes a production defect, preserve the evidence and report the defect rather than rewriting the expectation to match faulty behavior.
- For a flaky test, identify the uncontrolled input or race and verify the stabilization through repeated or targeted execution; do not hide it with retries or longer sleeps by default.
- If required services, data, permissions, tooling, or environments are unavailable, report the blocked checks and use the closest valid lower-level evidence without claiming equivalence.
- When legacy behavior is unknown, add narrow characterization coverage or inspect further before asserting the intended result.
- Report exact commands, pass/fail/skip counts, relevant failure context, and checks not run. Never claim tests passed without execution evidence.
- Do not commit or push automatically.
