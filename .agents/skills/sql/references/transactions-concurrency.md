# Transactions and concurrency

Read this reference when multiple statements or sessions can violate an invariant, when isolation or locking is under review, or when retry and deadlock behavior matters.

## Define the invariant and boundary

Identify the business invariant, transaction owner, statements and external effects inside the boundary, expected concurrency, and behavior after timeout, cancellation, disconnect, or partial failure. Verify that all required database operations use the same actual transactional context; annotations or nested APIs do not prove this. Keep transactions no longer than required, but do not split an atomic invariant merely to reduce lock duration.

For a long transaction, identify time spent working versus waiting, application think time, remote calls, result streaming, rows and indexes touched, lock retention, version or undo growth, log pressure, replication impact, and cleanup after cancellation. Shortening it is beneficial only if the invariant and failure semantics remain correct.

## Analyze interleavings

Construct concrete concurrent schedules for relevant risks:

- lost updates from read-modify-write sequences;
- dirty, non-repeatable, or phantom observations when those phenomena violate the requirement;
- write skew across multiple rows or predicates;
- duplicate creation from check-then-insert logic;
- inconsistent reads across related statements;
- deadlock cycles caused by conflicting lock acquisition order;
- uncertain commit outcomes and unsafe automatic retries.

Confirm how the actual DBMS/version implements the named isolation level; identical labels do not guarantee identical locking, MVCC, predicate protection, or conflict behavior. Distinguish blocking, deadlock, serialization failure, and application timeout.

For a lost update, show two transactions reading or deriving from overlapping state and one write overwriting the other's accepted change without detection. Check for atomic updates, version predicates, locks, serialization, or conflict detection before reporting. For phantom behavior, identify the predicate-based invariant, a concurrent insert/delete that changes its result set, and why the configured isolation does not protect that predicate in the actual engine.

For a deadlock, establish a feasible or observed wait cycle: each transaction holds a resource needed by the other. Long blocking, timeouts, and serialization failures are not deadlocks without the cycle or authoritative detector evidence. Examine consistent access order and transaction scope before suggesting broader locking or weaker isolation.

## Choose a control

Use the least costly mechanism that enforces the invariant: a declarative constraint, atomic statement, conditional update, version column, explicit lock, consistent access order, or stronger isolation. Constraints should be the final guard for stable data invariants when supported; pre-checks alone remain racy under concurrency.

Define retry eligibility from the actual error category and transaction outcome. Retry the complete transaction from a clean context, not an arbitrary suffix, and require every repeated database and external effect to be idempotent or safely deduplicated. Bound attempts, respect an overall deadline, use backoff where it prevents contention or synchronized retry storms, and preserve the final diagnostic context.

Do not retry persistent validation, constraint, authentication, syntax, or deterministic business failures merely because they surfaced through a database API. A specific constraint conflict may be retryable only when engine and application evidence establishes a transient concurrency cause—for example, a PostgreSQL unique violation from concurrent key selection—and a complete retry can safely choose new state without duplicating effects. Distinguish that case from a value that will violate the same constraint on every attempt.

For idempotency, identify the logical operation key, scope, lifetime, payload matching, atomic relationship between recording the key and applying effects, concurrent duplicates, and replayed outcome. A unique constraint can protect one row while leaving external or multi-row side effects duplicated.

Database transactions do not automatically make external messages, files, or service calls atomic. When those effects matter, describe the coordination and recovery model rather than implying universal distributed atomicity.

## Validate

Test a controlled concurrent schedule that can reproduce the risk and assert the invariant, not merely successful statement completion. Coordinate sessions with deterministic barriers or locks rather than timing luck where possible. Observe lock waits, wait graph or detector output, serialization diagnostics, transaction duration, affected rows, and retry outcomes with non-sensitive data in an isolated environment. Do not claim that a concurrency test proves absence of all races.
