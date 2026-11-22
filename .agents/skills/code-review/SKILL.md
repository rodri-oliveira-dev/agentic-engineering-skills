---
name: code-review
description: Review code diffs, proposed changes, and pull requests for actionable correctness, error-handling, security, concurrency, persistence, performance, and compatibility defects. Use when code review is requested; do not use for formatting-only work, isolated documentation edits, or implementation without a review request.
---

# Code review

## Outcome

Produce a diff-first, evidence-based review that identifies defects introduced, exposed, or materially worsened by the change. Prefer a small number of relevant, actionable findings—including none—over stylistic, architectural, or speculative commentary.

## Use and non-use

Use this skill when asked to review a pull request, patch, commit range, diff, or proposed code change. It also applies when the requested outcome is an assessment of merge risk or regression risk in changed code.

Do not activate it for formatting or naming cleanup, an isolated documentation edit with no executable or contractual effect, general explanation of unchanged code, or implementation/debugging without a review request. Do not turn a review into a refactor, security audit, architecture redesign, or implementation task unless the user separately requests that work.

## Required context

Obtain the change's stated objective and the most authoritative available diff. Identify the comparison base, changed files, repository guidance, affected contracts, relevant surrounding code, tests, configuration, generated artifacts, and dependency versions only as needed to understand the changed behavior.

If the diff, base, or intent is unavailable, inspect safe local evidence when possible. Otherwise state the missing input and limit the review; do not reconstruct changes or runtime behavior from guesswork.

## Workflow

1. Identify the objective, expected behavior, scope, and explicit non-goals of the change. Separate stated intent from inferred intent.
2. Inspect the diff before evaluating the wider codebase. Map changed lines to added, removed, or altered behavior; do not treat unchanged legacy code as a finding unless the change exposes, depends on, or materially worsens it.
3. Read the minimum surrounding implementation, tests, schemas, configuration, and call sites needed to understand affected contracts, invariants, data flow, trust boundaries, and lifecycle. Trace the changed execution path across entry point, orchestration, persistence, external calls, callbacks, and cleanup only as far as needed to validate behavior; do not expand into unrelated files.
4. Check functional correctness first: branches, boundary conditions, state transitions, units, ordering, null or empty values, cleanup, and contradictions with the stated objective. Read [correctness](references/correctness.md) when business rules, nontrivial control flow, resource lifetime, or cross-file behavior changes.
5. Evaluate error handling where failure is possible: which layer creates, translates, suppresses, retries, logs, or exposes the failure; whether exception type, status, retryability, cleanup, and partial effects still match caller contracts; and whether catch or fallback paths accidentally report success.
6. Evaluate security and data exposure when the change crosses a trust boundary or handles identity, authorization, untrusted input, secrets, sensitive data, files, network destinations, serialization, or cryptography. Read [security](references/security.md) only for those signals.
7. Analyze concurrency and asynchronous behavior when shared mutable state, parallel work, locks, queues, callbacks, cancellation, background tasks, or reordered events are involved. Read [concurrency](references/concurrency.md) for those signals.
8. Examine persistence and consistency when stored state, queries, transactions, caches, migrations, messages, or external side effects change. Read [persistence](references/persistence.md) for those signals. Read [distributed interactions](references/distributed-interactions.md) when the path adds or changes remote calls, retries, timeouts, idempotency, message delivery, or dependency failure behavior.
9. Consider performance only when the diff plausibly changes work on a relevant path. Read [performance](references/performance.md) for loops over variable input, repeated I/O, query shape, allocations, blocking, algorithms, serialization, or other scale-sensitive changes. Require workload or complexity evidence; avoid micro-optimization.
10. Evaluate compatibility and regressions for public or internal consumers, persisted data, protocols, schemas, configuration, dependencies, platforms, and observable error or timing behavior. Read [compatibility](references/compatibility.md) when a consumed contract or supported environment changes.
11. Validate every candidate using the verification process below. Use tests, static analysis, build output, documentation, or established language/platform behavior when available, but distinguish executed checks from proposed checks.
12. Report only relevant and actionable problems. Consolidate findings with the same root cause. Omit preferences, generic best practices, praise-only comments, and changes whose benefit cannot be tied to a concrete failure mode or material engineering cost.

## Candidate verification

For every suspicious behavior:

1. Identify the changed behavior and the narrowest changed location that could cause the concern.
2. Find evidence in the diff and surrounding implementation; do not infer behavior from a symbol name, API reputation, or isolated hunk.
3. Verify related callers, callees, contracts, configuration, and version-specific guarantees needed to follow the execution or data path. Stop once the claim is resolved; do not review unrelated files.
4. State the concrete input, interleaving, dependency response, deployment overlap, data state, workload, or failure sequence required for the problem to occur.
5. Look for existing protections such as validation, synchronization, uniqueness constraints, transactions, deduplication, cancellation, fallback, retries, ownership, framework guarantees, or upstream enforcement. Confirm their scope instead of assuming they work or do not work.
6. Determine the observable impact and affected consumer, resource, data, or operational path. Separate demonstrated impact from scale- or environment-dependent impact.
7. Classify confidence qualitatively from the evidence and unresolved assumptions; never calculate or require a numeric confidence threshold.
8. Report the candidate only when the change introduces, exposes, or materially worsens it and the causal chain is sufficiently supported for an experienced reviewer to request action now.

Classify the result as one of:

- **Defect:** the changed cause, triggering condition, violated contract or invariant, and failure mode are supported by available evidence.
- **Conditional risk:** the change creates a supported exposure, but occurrence or impact depends on a named workload, runtime, dependency, deployment, or consumer condition that is not yet known. State the condition and the safe verification needed; do not phrase it as a confirmed failure.
- **Improvement:** the code is correct under established contracts, but a concrete maintainability or resilience benefit remains. Keep it separate from defects, do not assign defect severity, and report it only when the user requests improvement feedback or the engineering cost is material and evidenced.
- **Unsupported hypothesis:** evidence cannot establish the path, condition, missing protection, or impact. Do not report it as a finding; record a focused question or limitation only when it materially affects review completeness.

Prefer no finding to a speculative one. Do not lower severity to compensate for weak evidence.

## Severity and confidence

Assign severity from impact and urgency, not certainty:

- **BLOCKER**: merging is unsafe because the change enables catastrophic or immediate impact, such as exploitable critical exposure, irreversible data loss or corruption, deterministic deadlock on a required path, or a breaking change that prevents required consumers from operating.
- **HIGH**: likely production failure or serious impact requiring correction before merge, such as incorrect core behavior, authorization bypass, transaction inconsistency, major resource exhaustion, or a demonstrated large regression.
- **MEDIUM**: concrete, bounded defect or material engineering cost that should be corrected but does not usually make the whole change unsafe, including scale-dependent performance loss or recoverable compatibility failure.
- **LOW**: small but real and actionable impact with clear evidence. Never use it for formatting, personal preference, optional modernization, or speculative abstraction.

Confidence is independent of severity. Use **high** when the changed path, trigger, protection state, and impact are directly supported; **medium** when the causal path is supported but a named environmental or consumer condition remains; and **low** only for a material verification question, not a reported defect. Do not present a low-confidence hypothesis as a defect merely by lowering its severity.

## Output

Order defects and conditional risks by severity, then by the affected execution or consumer path. For each provide:

```markdown
### [SEVERITY] Concise problem title

- **Location:** `path/to/file:line` or the narrowest available hunk/symbol
- **Classification:** defect, conditional risk, or improvement
- **Problem:** what is wrong and the condition that triggers it
- **Evidence:** the diff and contextual facts that support the causal claim
- **Existing protections:** why relevant safeguards do not prevent the issue, or which fact remains conditional
- **Impact:** the probable observable consequence and affected users or systems
- **Recommended fix:** the smallest practical correction or invariant to restore
- **Confidence:** high or medium, with any unresolved assumption
```

Do not quote large code blocks when a location and short explanation suffice. Do not duplicate one root cause across multiple lines or files.

When improvement feedback is in scope, place improvements in a separate section without defect severity and explain the evidenced engineering cost. Never mix them into the blocking findings list.

If there are no sufficiently supported findings, say so explicitly. Then state the reviewed scope, checks actually performed, checks not performed, and limitations that could change the result. Never claim that tests, builds, analyzers, benchmarks, scans, or runtime checks passed unless their execution and result were observed.

## Safety and limits

Review is read-only unless the user separately authorizes changes. Respect repository permissions and instructions, preserve unrelated work, and do not commit, push, post comments, approve, merge, or expose secrets as an implicit part of review. Redact sensitive values from evidence.

Treat generated code, vendored code, lock files, migrations, snapshots, and machine output according to their role; inspect their source or downstream effect when that is where a changed defect originates. Report unavailable tools, inaccessible context, and inconclusive verification honestly. Automated review complements tests, analyzers, security tooling, benchmarks, and human domain knowledge; it does not replace them.
