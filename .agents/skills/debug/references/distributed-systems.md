# Distributed systems debugging

Read this reference when the failing path crosses process, network, service, queue, storage, region, or infrastructure boundaries.

## Reconstruct the operation

Map caller, intermediaries, dependencies, async handoffs, state stores, and response path. Record component versions, configuration, ownership, trust boundaries, timeout budgets, retry policies, identifiers, and expected consistency. Follow a representative failed operation and a comparable successful operation when evidence permits.

At each boundary, verify protocol outcome, request and response timing, serialization, destination, connection or pool state, cancellation, and identifier propagation. Locate the first boundary with evidence of divergence rather than assigning cause to the component that emits the final error.

Account for incomplete traces, clock skew, sampling, independent deployments, and failures reported far from their origin. Separate the initiating fault from propagation, amplification, fallback, and user-visible symptom.

## Timeouts, retries, and transient failures

Determine which layer timed out, the configured budget at each hop, time already consumed before the call, actual latency distribution, queue time, cancellation propagation, and whether downstream work continued after the caller abandoned it. Add queueing, connection acquisition, serialization, network, dependency, and response-processing time to explain accumulated latency. A timeout does not establish unavailability or identify the slow component.

For cascading timeouts, map nested deadlines and work that survives upstream cancellation. Look for budgets that do not decrease downstream, repeated full-length waits, exhausted connection or worker pools, and retries that extend beyond the caller's useful deadline. Do not recommend increasing timeouts until the latency source, capacity effect, and end-to-end objective are known.

For retries, identify triggering errors, maximum attempts, backoff, jitter, deadline, retry layer, and idempotency. Check for multiplicative retries, retry storms, duplicated side effects, increased queueing, and load that outlives the original request. Distinguish a transient classification from evidence that a particular failure was transient.

Confirm a retry storm through attempt rate, original request rate, error classification, retry layers, queue or pool saturation, and feedback between failure and added load. High traffic during errors is not sufficient when the increase may be legitimate demand. Separate the initiating dependency or capacity fault from retry amplification as a contributing factor when evidence supports that relationship.

## Duplicate and eventual processing

Trace message or operation identity, delivery attempts, acknowledgment timing, visibility or lease behavior, deduplication scope, idempotency record lifetime, ordering, and poison handling. At-least-once behavior can produce duplicates; duplicate observation does not by itself identify which boundary retried.

For eventual consistency, define the expected convergence condition and time, authoritative source, replicas or caches, conflict policy, read path, and observation time. Distinguish an expected stale window from failed propagation or a permanently divergent state.

When processing is duplicated, compare logical operation identity with transport delivery and execution attempt identity. Determine whether the duplicate arose from retry, redelivery, lease expiry, concurrent consumers, acknowledgment loss, producer duplication, or reconciliation before assigning cause.

## Concurrency and deadlocks

Identify shared resources, transaction or lock owners, acquisition order, wait graph, timeouts, and cancellation. Confirm a deadlock from a cycle or authoritative detector evidence; long blocking is not automatically deadlock. For races, construct a feasible interleaving that violates an invariant and use controlled coordination rather than timing luck when reproducing it.

## Latency, saturation, and infrastructure

Correlate demand, throughput, concurrency, queue depth, utilization, errors, throttling, and tail latency across components. High utilization may be consequence rather than cause. Look for constrained resources, backpressure failure, uneven load, connection or worker pool exhaustion, noisy neighbors, network loss, name resolution, certificate expiry, capacity changes, and orchestration events only when signals support them.

For an external dependency, compare client-observed outcomes with provider status, contract, quotas, rate limits, DNS, TLS, network path, and a working cohort. Provider status is scoped and may lag; client errors can also originate locally. Preserve uncertainty when neither side has complete evidence.

## Configuration and communication

Compare effective endpoints, credentials metadata without values, permissions, protocol and schema versions, feature flags, timeouts, limits, serialization, region, and service discovery across working and failing cohorts. Check request/response contracts and error mapping at each boundary; do not infer remote behavior solely from a local wrapper error.

After a deployment, compare version and configuration cohorts, rollout timing, artifact identity, schema or dependency changes, traffic, capacity, and concurrent operational events. Chronology selects hypotheses; a causal mechanism and discriminating before/after or cohort evidence are still required.

## Safe experiments

Prefer passive correlation, replay with synthetic or redacted data in an isolated environment, bounded fault simulation, controlled concurrency, or a canary with explicit authorization and rollback. Define predicted signals before the experiment. Do not inject production faults, suppress security controls, purge queues or caches, or restart dependencies merely to see whether the symptom disappears.
