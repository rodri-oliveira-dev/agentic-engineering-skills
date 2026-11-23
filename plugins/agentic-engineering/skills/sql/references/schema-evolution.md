# Schema evolution

Read this reference when adding or changing tables, columns, types, constraints, indexes, partitions, views, routines, or persisted data representation.

## Plan compatibility and data state

Inspect existing data, dependencies, consumers, replication or change capture, deployment topology, and versions that may run concurrently. Define the final invariant and the valid intermediate states during rollout. Determine whether the change is metadata-only, rewrites data, scans a large object, validates existing rows, blocks access, or changes serialization and query semantics for the actual DBMS/version.

Compare old application with new schema, new application with old schema, and mixed application versions with every intermediate schema. Removing or renaming an object, tightening nullability or constraints, changing type, collation, default, generated value, key, or enum-like domain can break readers, writers, stored data, indexes, replication, and rollback even when the final schema is internally valid.

Prefer staged expand-and-contract evolution when old and new application versions overlap: add compatible structure, deploy compatible writers/readers, backfill in bounded and restartable batches, validate, enforce the invariant, switch usage, observe, and remove old structure only after consumers are retired. This is a strategy, not a universal sequence; adapt it to engine guarantees and change size.

## Preserve integrity

Use primary keys, unique constraints, foreign keys, checks, nullability, and defaults to encode stable relational invariants when the database should enforce them. Before adding a constraint, identify violating rows and the remediation policy. Do not silently discard or coerce data to make validation pass.

For type, key, or collation changes, verify conversion, range, precision, ordering, comparison, index, foreign-key, and application-binding effects. For backfills, define batching order, restart checkpoints, concurrency with live writes, throttling, and correctness verification.

## Assess operational risk

Identify lock mode and duration, table or index rewrite, log or WAL growth, replication lag, disk headroom, index build behavior, maintenance window, backup or recovery readiness, and abort criteria. Transactional DDL and rollback behavior vary by engine and operation; verify rather than assume.

Separate rollback from forward recovery. A down migration can be destructive or impossible after new data is written, and restoring an old application does not help when it cannot read the new representation. Never execute a migration or schema command without authorization for the exact target and a reviewed recovery approach.

## Validate

Test the migration from a production-like prior schema and representative data, including invalid and boundary rows. Verify application compatibility during mixed-version deployment, constraints after backfill, query plans where indexes change, rerun or resume behavior, duration and locks, observability, and recovery procedure. Report which checks were simulated, executed, or still required.
