# Persistence and consistency review

Read this reference when the change accesses stored state, modifies queries or schemas, changes transactions, introduces caching, publishes messages, or coordinates external side effects.

## Follow state across boundaries

Identify the consistency boundary, authoritative store, transaction ownership, isolation assumptions, expected cardinality, and retry or idempotency model. Trace partial failures between each state change and external effect.

Follow the complete changed unit of work rather than judging one repository method in isolation. Determine where the transaction begins and ends, which operations participate, when irreversible or external effects occur, and what callers observe after commit failure, timeout, cancellation, or uncertain outcome. Do not assume a method annotation, transaction wrapper, or ORM call covers work performed on another connection, worker, service, or message handler.

Check when relevant:

- parameter binding and separation of query structure from untrusted values;
- predicates, joins, ordering, limits, pagination, projections, and null semantics against the intended result set;
- atomicity of related writes and behavior when an intermediate operation fails;
- transaction scope, connection/session ownership, commit, rollback, and nested behavior;
- optimistic or pessimistic concurrency and lost-update handling;
- retry safety, deduplication, idempotency, and uncertain outcomes after timeouts;
- cache keys, freshness, invalidation, tenant boundaries, and source-of-truth behavior;
- schema or migration compatibility with existing data and mixed application versions;
- coordination between database writes and messages or other irreversible side effects.

For an idempotency finding, identify the logical operation identity, deduplication scope and lifetime, atomic relationship between claiming the identity and applying the effect, behavior for the same key with a different payload, concurrent duplicates, and replayed result. A unique constraint can prevent duplicate rows but may not prevent duplicate external effects; conversely, an atomic constraint or conditional write may already protect an apparent check-then-act sequence.

For cross-boundary state changes, verify the actual coordination model. Do not demand distributed transactions, outbox, saga, or another pattern by name; report the concrete lost, duplicated, reordered, or partially committed outcome and recommend the least complex mechanism that enforces the required invariant.

Do not assume a database, driver, ORM, isolation level, or consistency guarantee. Verify it from repository configuration or authoritative platform behavior. When evidence is incomplete, identify the missing fact instead of asserting corruption or inconsistency.
