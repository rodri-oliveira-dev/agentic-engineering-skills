# Compatibility and migrations

Read this reference when the release changes APIs, protocols, messages, schemas, persisted data, configuration contracts, dependencies, runtime targets, or database migrations.

## Model coexistence

Identify producers, consumers, stored data, rollout order, deployment units, and old and new versions that can coexist. Compare fields, types, defaults, nullability, ordering, error behavior, status codes, identifiers, enum values, serialization, timing, and retry or idempotency semantics where consumers rely on them.

Additive changes are not automatically compatible with strict readers, exhaustive enum handling, fixed schemas, resource limits, or older runtimes. Confirm actual compatibility requirements and tests rather than relying on semantic-version labels.

## Evaluate migrations

Determine whether each change is metadata-only, validates or scans existing data, rewrites storage, builds an index, changes keys or types, locks readers or writers, increases logs or replication lag, or requires backfill. Establish data volume, invalid-row handling, expected duration, batching, throttling, resumability, concurrency with live traffic, disk headroom, and observability for the actual engine and version.

When old and new applications overlap, prefer a compatible staged sequence where justified: add or expand, deploy compatible readers and writers, backfill and validate, switch behavior, then contract after old consumers retire. Do not impose this sequence when the platform provides a safer proven mechanism.

For expand-contract, identify the compatibility invariant and exit evidence for every stage. Expansion must remain usable by old and new versions; dual reads or writes need ownership, reconciliation, idempotency, and divergence signals; backfill needs bounds and restart behavior; contraction waits until old binaries, consumers, jobs, cached data, and rollback paths no longer depend on the old representation. A migration named “expand” is not evidence that these properties hold.

## Recovery reality

Separate application rollback from data rollback. Once new-format data is written or destructive transformation occurs, an old binary may no longer be compatible. A down migration can lose data, exceed the recovery window, or be unsupported even if a script exists.

Require evidence for backups, restore procedure, restore duration, point-in-time objectives, forward repair, and reconciliation when relevant. For irreversible changes, define a tested or credible roll-forward recovery and containment strategy before readiness; “restore from backup” without scope and timing is not a plan.

Evaluate recovery against RTO, RPO, outage tolerance, data volume, replication state, and the exact failure point. Application rollback does not reverse writes already accepted under a new contract. State whether recovery restores, repairs, replays, reconciles, or intentionally loses data, and how correctness will be verified afterward.

## Validation

Use production-like prior schemas and representative volumes for authorized rehearsals. Check mixed-version application behavior, invalid and boundary data, lock and resource impact, restart or resume, replication, post-migration constraints, and recovery. Report rehearsals as proposed unless execution records were observed.
