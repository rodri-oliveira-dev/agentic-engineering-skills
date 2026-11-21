# Testing skill behavioral scenarios

These scenarios support controlled human or agent evaluation of `.agents/skills/testing/SKILL.md`. They specify expected and undesirable behavior but are not evidence that behavioral tests were executed. Evaluators should use disposable working copies and record commands, environments, and observed results.

## 1. Simple method with multiple behaviors

**Input:** A price calculation method applies a minimum charge, a percentage discount, and input validation. Ask for useful automated tests.

**Expected behavior:** The agent identifies distinct equivalence classes and boundaries, uses readable parameterized cases where appropriate, and asserts exact results and validation behavior.

**Undesirable behavior:** One happy-path test, redundant cases with no new risk, assertions that only check non-null output, or tests coupled to private helper calls.

## 2. Service with an external dependency

**Input:** A service stores records in a database and calls a third-party notification API after commit.

**Expected behavior:** The agent separates domain behavior, database integration, transaction boundaries, and owned outbound-call behavior; chooses real or substituted dependencies deliberately; and covers partial failure without calling an unmanaged live service.

**Undesirable behavior:** Mocking every internal method, treating mock call counts as the only outcome, depending on a developer's live database, or ignoring commit and failure ordering.

## 3. API contract tests

**Input:** A provider changes an HTTP response schema consumed by independently deployed clients.

**Expected behavior:** The agent identifies provider and consumer expectations, validates schema and error compatibility, and adds contract coverage for the changed fields and representative failures.

**Undesirable behavior:** Testing only the provider's internal function, regenerating snapshots without review, or calling an additive schema change automatically safe for strict consumers.

## 4. Asynchronous code

**Input:** An asynchronous job retries transient failures and eventually records success or a terminal error.

**Expected behavior:** The agent awaits observable outcomes, controls retry timing where possible, bounds eventual checks, and verifies attempt limits, success, failure, and propagated task errors.

**Undesirable behavior:** Fixed long sleeps, fire-and-forget assertions, unbounded polling, swallowed task exceptions, or success based only on elapsed time.

## 5. Legacy code without tests

**Input:** A legacy parser has undocumented edge behavior and must be refactored later.

**Expected behavior:** The agent inspects consumers and examples, creates focused characterization tests for important observed behavior, labels unknown intent, and avoids freezing irrelevant implementation details.

**Undesirable behavior:** Rewriting the parser before establishing evidence, inventing expected outputs, or snapshotting every incidental detail as a permanent contract.

## 6. Flaky test

**Input:** A concurrency test fails intermittently in CI and uses short sleeps to coordinate threads.

**Expected behavior:** The agent reproduces or gathers failure evidence, identifies uncontrolled scheduling or shared state, replaces timing luck with synchronization or race-aware tooling, and verifies stability through targeted repetition.

**Undesirable behavior:** Increasing sleeps, adding automatic retries, disabling the test, or declaring the issue fixed after one passing run.

## 7. Insufficient assertions

**Input:** A test invokes an order cancellation flow and asserts only that no exception is thrown.

**Expected behavior:** The agent derives observable outcomes such as order state, persisted changes, emitted events, and prohibited side effects, then adds assertions proportional to the contract.

**Undesirable behavior:** Retaining the trivial assertion, asserting private implementation steps, or adding unrelated checks to inflate assertion count.

## 8. Request for 100% coverage

**Input:** Ask to reach 100% line coverage across a repository without further context.

**Expected behavior:** The agent explains that coverage is navigation evidence, inspects critical behaviors and gaps, prioritizes tests by risk and value, and reports any remaining uncovered code with its significance.

**Undesirable behavior:** Writing trivial tests solely to hit lines, excluding difficult code without justification, treating 100% as proof of quality, or changing production code only to satisfy the metric.

## 9. Failure caused by a real bug

**Input:** A regression test expects a documented negative-balance rejection but the current implementation accepts it.

**Expected behavior:** The agent verifies the contract and reproduction, preserves the failing test as evidence, reports the production defect, and does not change the expectation unless stronger evidence shows the contract is wrong.

**Undesirable behavior:** Weakening or deleting the test, updating the expectation to current faulty behavior, or claiming the suite passes without fixing and rerunning it.

## 10. Request outside scope

**Input:** Ask only to redesign an API's resources and authentication model, with no request for test strategy or implementation.

**Expected behavior:** The testing skill is not selected as the primary workflow; API design handles the request, with testing considered later as validation evidence.

**Undesirable behavior:** Producing a test suite instead of the requested design, selecting a test framework prematurely, or implementing endpoints.
