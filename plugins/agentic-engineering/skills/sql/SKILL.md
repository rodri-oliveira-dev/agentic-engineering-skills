---
name: sql
description: Develop and review relational SQL queries, indexing, data models, transactions, concurrency controls, and safe schema evolution with DBMS-aware correctness, security, and performance analysis. Use for relational database work; do not use for unrelated application code, non-relational stores, or generic data analysis without SQL concerns.
---

# SQL

## Outcome

Produce correct, secure, maintainable SQL and proportionate database recommendations grounded in the known schema, workload, database engine, and evidence. Preserve data integrity and make dialect assumptions, execution effects, validation steps, and unresolved risks explicit.

## Use and non-use

Use this skill to develop or review relational queries, investigate query performance, design indexes and relational constraints, reason about transactions and concurrency, or plan safe schema evolution and migrations.

Do not activate it for unrelated application implementation, general code review without a material SQL concern, non-relational database design, spreadsheet formulas, search query languages, or analytics that do not require relational SQL decisions. Do not translate application logic into database procedures or change a data model unless the request requires it.

## Required context

Identify the DBMS, version, driver or query layer, environment, schema, data sensitivity, expected result, and operational constraints when they affect the answer. Obtain authoritative definitions for relevant tables, columns, types, nullability, keys, foreign keys, checks, defaults, indexes, views, triggers, generated columns, partitioning, row-level policies, and stored routines.

Establish approximate row counts, value distribution, cardinality, growth, request frequency, concurrency, latency target, and write rate only to the depth required by the task. Distinguish observed metadata and measurements from estimates. If critical information is unavailable, ask a focused question or provide a conditional proposal; do not invent schema, workload, plans, or engine behavior.

## Workflow

1. Identify the DBMS and version when syntax, optimizer behavior, isolation, locking, DDL, or operational safety depends on them. Also identify compatibility modes, extensions, proxies, or managed-service restrictions when relevant.
2. Inspect known tables, columns, types, indexes, constraints, relationships, statistics, and representative data shape. Do not infer keys or uniqueness from names alone.
3. Define the query or change objective, required rows and columns, correctness rules, acceptable duplicates and null behavior, ordering, consistency needs, and caller expectations.
4. Estimate relevant cardinalities and volume: base rows, filter selectivity, join multiplicity, groups, result size, skew, growth, frequency, and concurrent executions. Label estimates and identify what measurement would confirm them.
5. Analyze filters, joins, projections, expressions, aggregations, and ordering. Verify join predicates and expected multiplicity; examine sargability only against the actual engine and available access paths; avoid unnecessary columns and work while preserving duplicate, null, grouping, ordering, and error semantics.
6. Inspect the full application-to-database access pattern for N+1 behavior. Count possible round trips and distinguish one set-based query from repeated per-row queries; do not diagnose N+1 from an isolated query alone.
7. Choose pagination according to ordering and consistency requirements. Require deterministic ordering with a stable tie-breaker. Compare offset and keyset approaches using navigation needs, data churn, index support, and result size rather than treating either as universal.
8. Evaluate transaction boundaries, atomicity, isolation, lock duration and order, contention, lost updates, phantom behavior, retry safety, idempotency, deadlocks, timeouts, and concurrent interleavings when multiple statements or sessions can affect the invariant. Read [transactions and concurrency](references/transactions-concurrency.md) for these tasks.
9. Verify integrity at the appropriate boundary using keys, uniqueness, foreign keys, checks, nullability, defaults, and application validation. Read [schema evolution](references/schema-evolution.md) when adding or changing schema, constraints, migrations, partitions, or stored data representation.
10. Inspect available execution plans, actual row counts, estimates, statistics, scans, joins, aggregations, sorts, spills, lookups, parallelism, waits, and duration when performance is in scope. Read [query performance](references/query-performance.md) before interpreting plans or proposing indexes. Never fabricate a plan, confuse estimated cost with elapsed time, or treat plan shape alone as proof.
11. Propose the smallest improvement supported by correctness and workload evidence. Prove result equivalence before treating a rewrite as an optimization. Explain trade-offs, including index storage and write cost, maintenance, lock duration, contention, migration risk, portability, and operational complexity.
12. Define validation before execution: result equivalence or expected rows, boundary and null cases, constraint behavior, concurrency scenarios, parameterized integration tests, plan comparison, representative measurements, rollback or recovery, and production observation as applicable.

## DBMS-specific routing

Keep relational concepts separate from vendor syntax and semantics. Read [DBMS differences](references/dbms-differences.md) when a task depends on PostgreSQL, SQL Server, MySQL, or another engine's pagination, plan commands, locking, isolation, DDL, generated values, upsert, parameter markers, or index capabilities. Verify behavior against authoritative documentation for the actual version; never present a cross-engine approximation as portable SQL.

## Security and execution safety

Prefer bound parameters for data values and preserve the placeholder convention of the actual driver. Never concatenate untrusted input into SQL. Parameters generally do not substitute for identifiers or arbitrary syntax; when dynamic identifiers or clauses are required, choose them from an allowlist and use the DBMS's safe identifier-quoting mechanism.

Request only needed columns and rows, especially for personal, financial, authentication, tenant, or other sensitive data. Do not reveal connection strings, passwords, tokens, query parameters containing secrets, or sensitive result values in commands, logs, plans, examples, or reports. Use least-privilege credentials and a non-production environment when execution is justified.

Classify every proposed command before execution:

- **Analysis only:** reading schema files, reviewing SQL, or generating a statement has no database effect.
- **Database read:** a plain query may still invoke volatile functions, acquire locks, expose sensitive data, consume material resources, or use vendor-specific side effects. Confirm the statement and context before calling it read-only.
- **Diagnostic execution:** `EXPLAIN ANALYZE`, actual execution plans, profiling modes, and equivalents may execute the underlying statement, hold locks, write through functions, or add significant load. Determine behavior for the DBMS, version, and analyzed statement before use; use estimate-only modes when they answer the question safely.
- **Mutation or DDL:** `INSERT`, `UPDATE`, `DELETE`, `MERGE`, `TRUNCATE`, `DROP`, schema changes, migrations, maintenance, and commands that invoke mutating routines require explicit authorization compatible with the exact target, environment, affected data, reversibility, lock and load risk, and recovery plan. A transaction wrapper does not make every operation reversible.

Treat every `UPDATE` or `DELETE` as unsafe until its target set is bounded by predicates, keys, tenant scope, and expected row count appropriate to the request. A `WHERE` clause alone is not proof of adequate restriction. Before authorized execution, validate the target set through the safest equivalent read or estimate, account for triggers and cascades, define an affected-row guard where supported, and preserve a recovery path. Do not convert that preview into a production query or expose sensitive rows without authorization.

Do not execute a destructive, irreversible, or production-affecting command from a general request to analyze, optimize, review, or demonstrate SQL. Prefer offline inspection, synthetic data, isolated environments, and estimate-only diagnostics when they answer the question. Before any authorized production query, consider data sensitivity, workload, plan risk, locks, timeout, replicas, and abort criteria; read-only syntax can still block, saturate resources, or invoke side effects. Before an authorized production change, identify affected objects and rows, dependencies, expected locks and duration, deployment order, backups or recovery mechanism, monitoring, abort criteria, and rollback or forward-recovery path. Stop when the target, authority, or recovery conditions are unclear.

## Performance guidance

Treat performance as measured behavior under a workload. Relate claims to cardinality, selectivity, distribution, concurrency, cache state, plan, elapsed time, CPU, memory, I/O, network round trips, locks, or service objectives. Do not promise improvement from rewritten SQL or a new index without representative evidence.

Consider indexes together with predicate and join support, column order, included or covering data, uniqueness, filtered or partial conditions, expression support, sort order, statistics, and existing overlapping indexes. Account for storage, cache pressure, write amplification, locking, maintenance, rebuild, and deployment cost. Do not recommend an index merely because a filtered or joined column exists.

Treat scans, nested-loop joins, sorts, hash operations, and parallelism as context-dependent choices, not defects by name. Investigate estimate errors, stale or insufficient statistics, skew, parameter sensitivity, spills, implicit conversions, non-sargable predicates, and blocking only when the engine and evidence support the claim.

Classify performance conclusions explicitly:

- **Demonstrated problem:** representative measurements or an attributable actual plan establish material cost against a stated objective.
- **Supported risk:** query shape, cardinality, workload, or locking evidence establishes a plausible material cost, but representative runtime measurement is unavailable. State the condition and validation needed.
- **Hypothesis:** evidence is insufficient to establish materiality or cause. Ask for the minimum plan, statistics, parameters, workload, or timing evidence; do not prescribe an index or rewrite as a finding.

Do not upgrade a hypothesis by relying on a rule of thumb. A table scan, nested-loop join, sort, large estimated cost, or missing-index suggestion can be appropriate; a seek or index-only access can still be expensive.

## Deliverable

Provide, as applicable:

- the DBMS/version and assumptions;
- the query, schema, index, transaction, or migration proposal in the correct dialect;
- an explanation of result semantics and relevant security or concurrency properties;
- evidence and trade-offs for review or performance findings;
- whether each shown command is analysis-only, read, diagnostic execution, or mutation/DDL;
- validation steps and commands, clearly marked as executed or proposed;
- deployment, rollback, and observation guidance for schema or production changes;
- missing evidence and limitations.

For query review, associate each actionable issue with the narrowest available statement, clause, or line and explain the triggering data shape or concurrent condition. If no defect or justified improvement is found, state that explicitly rather than inventing an optimization.

## Failure and uncertainty

Do not claim correctness, safety, portability, plan quality, index usage, absence of deadlocks, or performance gains without evidence. An estimated plan is not runtime proof, a development dataset is not production workload evidence, and one execution is not a stable benchmark.

If database access is unavailable or unnecessary, work from supplied schema, SQL, plans, and measurements and state that no database command was run. If execution fails, preserve the original error context without exposing secrets, avoid repeated risky retries, and explain the next safe diagnostic step. Preserve unrelated files and database objects; do not commit, push, provision infrastructure, or connect to a real database unless the user authorizes that scope.
