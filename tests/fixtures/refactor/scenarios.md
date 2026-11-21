# Refactor skill behavioral scenarios

These scenarios support controlled human or agent evaluation of `.agents/skills/refactor/SKILL.md`. They specify expected behavior but are not evidence that behavioral tests were executed. Evaluators should use disposable working copies and record changes, commands, and observed results.

## 1. Extract a method

**Input:** A Python request handler contains a long, cohesive block that normalizes an address and is difficult to test independently. Ask to extract it without changing request or response behavior.

**Expected behavior:** The agent traces inputs, outputs, exceptions, and call sites; confirms the block has a coherent purpose; adds or identifies focused coverage; and performs a local extraction with unchanged public behavior. It validates the relevant tests and reports only observed results.

**Failure:** It redesigns the handler architecture, changes validation semantics, creates a generic framework, or claims equivalence because the code imports or compiles.

## 2. Reduce duplication

**Input:** Two TypeScript modules contain similar validation logic with one intentional difference. Ask to reduce duplication.

**Expected behavior:** The agent identifies the shared invariant and the intentional variation, then extracts only the genuinely common logic or explains why duplication is safer. The change remains local and existing consumers retain their behavior.

**Failure:** It forces both modules through one abstraction that erases the variation, broadens the change to unrelated validators, or assumes visually similar code has identical contracts.

## 3. Simplify conditional logic

**Input:** A Java function has nested conditionals governing authorization, with tests for roles, resource ownership, and denial reasons. Ask to make it easier to read without changing decisions.

**Expected behavior:** The agent enumerates decision outcomes and error behavior, uses the tests as a baseline, and applies a small simplification such as guarded exits or named predicates. It checks that decision ordering and denial semantics remain stable.

**Failure:** It changes precedence, exception behavior, or denial details; replaces the logic with an unjustified pattern; or treats formatting alone as the solution.

## 4. Legacy code without tests

**Input:** A legacy Ruby billing routine has no automated tests and several external side effects. Ask for a broad cleanup.

**Expected behavior:** The agent maps callers and side effects, classifies the change as high risk, proposes focused characterization seams or additional inspection, and limits initial edits to behavior that can be observed and validated. It presents alternatives instead of starting a rewrite.

**Failure:** It performs the broad cleanup immediately, assumes current behavior from names alone, mocks away important side effects, or asserts preservation without evidence.

## 5. Public contract break

**Input:** A refactoring proposal renames a JSON response field and changes the default of an exported function used by external consumers.

**Expected behavior:** The agent identifies both changes as public contract changes rather than behavior-preserving refactoring. It preserves the existing contract or separates the proposal into an explicit versioned change with compatibility and migration considerations.

**Failure:** It silently ships the changes, labels them internal cleanup, updates only local tests, or ignores downstream consumers.

## 6. Concurrency-sensitive refactoring

**Input:** A Go worker pool uses shared state and cancellation; ask to extract scheduling logic and simplify locking.

**Expected behavior:** The agent documents atomicity, ordering, cancellation, shutdown, and race-safety invariants; inspects concurrency tests and tooling; proposes small steps; and avoids changing synchronization without appropriate validation. It reports uncertainty where timing behavior cannot be reproduced.

**Failure:** It removes locks because code looks sequential, changes cancellation timing, relies only on ordinary unit tests, or claims a performance benefit without measurement.

## 7. Feature request outside scope

**Input:** Ask to add search filters and pagination to an existing endpoint, describing the work as a refactor.

**Expected behavior:** The refactor skill is not selected as the primary workflow because the request adds observable functionality. Any prerequisite cleanup is separated, justified, and kept smaller than the feature work.

**Failure:** It treats the feature as behavior-preserving, changes the API under the refactoring label, or expands into unrelated architecture work.
