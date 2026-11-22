# Query performance

Read this reference when investigating a slow query, interpreting a plan, evaluating N+1 behavior, choosing pagination, or proposing an index.

## Establish evidence

Capture the exact SQL shape and parameter values or representative classes, DBMS/version, relevant schema and indexes, table and result cardinalities, distribution or skew, statistics definition and freshness, execution frequency, concurrency, and performance objective. Prefer representative, repeatable measurements. Separate compilation or planning time, execution time, lock wait, client fetch time, and network round trips when the distinction matters.

Use the safest plan facility that answers the question. Estimate-only plans avoid executing the statement but cannot provide actual rows or runtime effects. Actual-plan, profiling, and `EXPLAIN ANALYZE`-style facilities may execute the statement and add overhead; apply the execution classification and authorization rules from `SKILL.md`.

## Read plans comparatively

Compare estimated and actual cardinalities at each important step and at the final result. Large estimate errors can change join order, join algorithm, memory allocation, access path, and parallelism; investigate their source rather than treating the chosen operator as the cause. Follow data flow from access methods through joins, filters, aggregates, sorts, and result production. Investigate, when evidenced:

- full or range scans relative to table size, selectivity, and required output;
- join algorithm choice, input size, repetition, and predicate correctness;
- sorts, hashes, temporary structures, memory grants, and spills;
- repeated lookups, correlated subqueries, or application round trips;
- partition pruning, predicate pushdown, and implicit type conversions;
- blocking, lock waits, I/O, CPU, parallel workers, and plan instability;
- estimate errors caused by stale statistics, skew, correlation, or parameter sensitivity.
- long duration caused by lock waits, resource queues, client consumption, network transfer, or repeated execution rather than CPU or I/O inside one plan.

A scan can be optimal, an unused index can be redundant, and a nested-loop join can be correct for a small outer input. Treat operator names as clues, not findings.

Statistics being old is not automatically a defect, and updating them is not a universal fix. Verify whether sampled or full statistics represent relevant values, multiple columns are correlated, parameters produce different selectivity classes, and the engine has the statistics feature needed. Account for plan cache and reoptimization behavior only when evidenced for the actual DBMS/version.

## Preserve semantics while reshaping work

For joins, verify keys, multiplicity, null extension, filter placement, and duplicate behavior before changing join type or order. For aggregation, verify grouping keys, distinctness, null handling, numeric precision, overflow, filter timing, and whether pre-aggregation changes multiplicity. For pagination, require deterministic ordering and compare offset and keyset behavior under concurrent inserts, updates, and deletes against navigation requirements.

Assess sargability as an access-path question, not a syntax score. Functions or casts on indexed columns, implicit conversions, collation changes, arithmetic, leading-wildcard searches, and mismatched types can inhibit an index on some engines, but expression indexes, computed columns, optimizer transformations, or a scan may make the original form appropriate. Never rewrite a predicate until its null, time-zone, collation, precision, and boundary semantics are proven equivalent.

## Evaluate indexes

Start from demonstrated access patterns. Determine whether an existing index can support equality, range, join, ordering, grouping, or uniqueness needs and whether the proposed column order matches those operations. For a composite index, reason about leading keys, equality and range predicates, sort direction, grouping, selectivity and skew, skip or loose scan capabilities, and reuse across important queries. Do not apply “most selective column first” as a universal rule.

Consider included or covering columns and filtered, partial, expression, clustered, or other engine-specific indexes only if the engine/version supports their needed semantics. Coverage can reduce lookups while increasing index width, cache use, update cost, and build time. Prefer consolidating overlapping indexes only after confirming their distinct read, uniqueness, ordering, and operational roles.

Estimate read benefit against storage, cache use, insert/update/delete amplification, page or structure splits, maintenance, statistics, build time, replication or log volume, locks, and overlap with existing indexes. Include write frequency and latency objectives, not only read speed. Validate with comparable plans and measurements after representative data and statistics are prepared. Do not promise a particular index or join choice; optimizers retain plan choice.

## Locks, contention, and long queries

Determine whether a slow execution is working, waiting, blocked, or blocked by the client. Identify lock owner, waiter, mode, resource, acquisition order, transaction age, rows touched, and isolation semantics before recommending an index or isolation change. An index can shorten lock duration or can add write contention; either claim needs evidence.

For long-running queries, examine workload purpose, progress, cancellation safety, temporary or memory use, spill, result transfer, transaction scope, replication effects, and competition with critical work. Do not terminate, reconfigure, or move production work as part of analysis without authorization.

## Validate changes

Verify result equivalence—including row multiplicity, nulls, values, ordering promises, errors, and side effects—before comparing performance. Warm and cold cache behavior, parameter classes, data skew, concurrent load, write cost, and plan reuse may require separate trials. Report measured values, setup, variance, and limitations; do not extrapolate a single local run into a production guarantee.
