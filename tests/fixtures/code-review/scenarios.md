# Code review skill behavioral scenarios

These scenarios support controlled human or agent evaluation of `.agents/skills/code-review/SKILL.md`. They are not executable tests and are not evidence that behavioral evaluation occurred. Evaluate causal reasoning and evidence use rather than exact wording. Record the diff, context inspected, references loaded, checks run, findings, omitted candidates, confidence, and limitations.

## 1. Functional regression

**Input:** Review a diff that changes a discount condition from `total >= threshold` to `total > threshold`. A published rule and an existing boundary test establish that an order exactly at the threshold receives the discount.

**Expected findings:** One correctness defect at the changed condition: the equality case now violates the established contract.

**Prohibited findings:** Pricing redesign, naming or formatting feedback, unrelated legacy pricing concerns, or claims about other thresholds not shown by evidence.

**Minimum evidence:** Changed comparison, authoritative threshold contract, reachable equality input, and observable incorrect result.

**Behavioral criteria:** The review ties condition to impact and recommends the smallest correction or restored invariant.

## 2. Real race condition

**Input:** A diff replaces an atomic per-key insertion with `contains(key)` followed by `insert(key)` on shared mutable state. Two workers can call the method concurrently, no lock or serialized owner surrounds it, and duplicate insertion violates a documented uniqueness invariant.

**Expected findings:** One concurrency defect demonstrating a feasible two-worker interleaving in which both checks pass before either insert completes.

**Prohibited findings:** Deterministic deadlock, generic “collections are unsafe,” or unrelated recommendations to redesign the worker architecture.

**Minimum evidence:** Shared object lifetime, concurrent reachability, unsynchronized compound operation, feasible interleaving, and violated invariant.

**Behavioral criteria:** Confidence and severity follow evidence and impact; the correction restores atomicity without prescribing an unrelated pattern.

## 3. Apparent race protected by synchronization

**Input:** A diff adds a check-then-update sequence on a non-thread-safe map. Surrounding code shows every access occurs inside the same lock, the map never escapes its owner, and tests coordinate concurrent callers through that boundary.

**Expected findings:** No race-condition finding.

**Prohibited findings:** Reporting the map or check-then-update shape as unsafe, demanding a concurrent collection, or lowering severity to preserve a speculative comment.

**Minimum evidence:** Common lock covers all reads and writes, shared object does not escape, and concurrent entry points acquire that lock.

**Behavioral criteria:** The reviewer actively checks protections, records the candidate as disproved or omitted, and does not mistake stylistic discomfort for a defect.

## 4. Idempotency bug after timeout

**Input:** A new payment client retries a timed-out create request with a fresh operation identifier. The provider contract states that a timed-out request may still complete and deduplicates only by stable identifier. The caller can therefore create two charges.

**Expected findings:** One correctness or persistence defect explaining the uncertain first outcome and duplicate effect caused by changing the identifier.

**Prohibited findings:** Claiming every retry is unsafe, demanding distributed transactions, or asserting the provider definitely completed the first request.

**Minimum evidence:** Retry path, identifier generation per attempt, provider deduplication contract, timeout uncertainty, and reachable duplicate side effect.

**Behavioral criteria:** The finding recommends stable logical-operation identity or another contract-compatible correction and separates possibility from certainty of the first completion.

## 5. Unsafe query

**Input:** A diff replaces a parameterized repository query with SQL that interpolates an HTTP parameter. The endpoint is reachable and no query builder or driver binding occurs later.

**Expected findings:** One security defect tracing untrusted input into SQL structure and recommending parameter binding.

**Prohibited findings:** Reproduction with a dangerous payload, disclosure of sensitive values, generic database hardening, or unrelated schema changes.

**Minimum evidence:** Attacker-controlled source, interpolation into query syntax, reachable execution sink, and absence of an effective binding protection.

**Behavioral criteria:** Exploitability, impact, confidence, and severity are distinct and supported.

## 6. Breaking compatibility change

**Input:** A diff renames a required JSON response field. The published schema and a deployed generated client require the old field, and producer and consumer versions will coexist without negotiation or migration.

**Expected findings:** One compatibility defect at the changed serialization contract.

**Prohibited findings:** Treating every rename as breaking without consumer evidence, proposing a broad API redesign, or reviewing unrelated endpoints.

**Minimum evidence:** Before-and-after field contract, affected deployed consumer, overlap condition, and concrete deserialization or behavior failure.

**Behavioral criteria:** The review recommends a compatible transition and locates the finding at the narrowest changed contract.

## 7. Demonstrable performance regression

**Input:** A diff moves one remote lookup per item into a loop over an unbounded result set. Repository telemetry shows the path commonly processes 1,000 items; the prior implementation used one batch request and the dependency quota is documented.

**Expected findings:** One performance defect or conditional risk, according to the evidenced quota and impact, describing the increase from one round trip to approximately one per item.

**Prohibited findings:** Unmeasured allocation micro-optimizations, caching without an invalidation model, or guaranteed latency numbers absent from evidence.

**Minimum evidence:** Changed call placement, input cardinality, prior behavior, remote dependency call, and representative workload or quota context.

**Behavioral criteria:** The finding states the scale condition, material cost, and smallest batching or bounding correction.

## 8. Stylistically poor but correct code

**Input:** An explicit review request covers a diff with long methods, awkward local names, and duplicated-looking branches. The branches intentionally implement distinct documented rules, tests cover both, and behavior and contracts remain correct.

**Expected findings:** No defect. An improvement may be mentioned only if improvement feedback was requested and a concrete material maintenance cost is evidenced.

**Prohibited findings:** Style preferences as LOW defects, mandatory abstraction, SOLID or design-pattern comments, or claims that duplication changes behavior.

**Minimum evidence:** Documented distinct rules, branch behavior, tests or equivalent contract evidence, and absence of a changed failure mode.

**Behavioral criteria:** The response distinguishes correctness from maintainability preference and permits zero findings.

## 9. Incomplete context that invites a false positive

**Input:** A diff adds `store.save(record)` in a new path but omits the store implementation, transaction boundary, caller concurrency, retry configuration, and tests. Lost updates or duplicate writes are conceivable but not established.

**Expected findings:** No defect finding; a focused limitation or verification question may identify the missing evidence.

**Prohibited findings:** Assigning severity to a race, transaction, or idempotency hypothesis; assuming the store is non-atomic; or claiming checks were executed.

**Minimum evidence:** The diff proves only that `save` is called; the artifacts required to establish atomicity, concurrency, and retry behavior are unavailable.

**Behavioral criteria:** Facts and hypotheses are separated, low confidence is not used to disguise speculation, and the requested context is narrowly scoped.

## 10. Correct change with no relevant defects

**Input:** A focused bug fix now matches the published contract, preserves public errors and resource ownership, uses an existing transaction and idempotency mechanism correctly, and includes a regression test. No relevant security, concurrency, performance, dependency, or compatibility signal is introduced.

**Expected findings:** No sufficiently supported findings.

**Prohibited findings:** Praise-only comments, generic resilience recommendations, extra architecture, speculative edge cases, or LOW findings manufactured for output volume.

**Minimum evidence:** Changed path, affected contract, existing protections, regression coverage, and relevant surrounding implementation.

**Behavioral criteria:** The result states reviewed scope, checks actually performed, checks not run, and limitations without claiming the entire system is defect-free.
