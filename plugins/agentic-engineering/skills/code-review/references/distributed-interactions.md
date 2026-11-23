# Distributed interactions review

Read this reference only when the diff adds or changes remote calls, message delivery, retries, timeouts, idempotency, cancellation, fallbacks, or behavior under external dependency failure.

## Follow one logical operation

Trace the changed operation from caller deadline through each remote attempt, state transition, acknowledgment, response, and cleanup. Identify who owns the overall outcome, which effects can occur after the caller stops waiting, and what identity connects retries or duplicate deliveries. Treat the network as capable of delay, loss, duplication, reordering, and an unknown outcome after timeout; do not assume a timeout means the dependency did nothing.

## Validate resilience behavior

Check when relevant:

- timeout budgets across layers, including connection, request, queue, and overall operation deadlines;
- cancellation propagation and whether abandoned downstream work can still commit an effect;
- retry classification, maximum attempts, backoff, jitter, deadline, and the layer responsible for retrying;
- retry multiplication across clients, proxies, services, queues, and jobs;
- idempotency or deduplication scope, atomicity, key lifetime, payload matching, concurrent duplicates, and replayed outcomes;
- message acknowledgment timing, visibility or lease expiry, poison handling, ordering, and redelivery;
- fallback semantics, especially stale, partial, cached, or default data presented as success;
- connection, stream, response-body, subscription, and client lifetime on success, error, timeout, and cancellation;
- dependency contract changes in errors, rate limits, quotas, versions, consistency, and side effects.

## Evidence threshold

Construct a concrete sequence that produces the claimed duplicate effect, lost work, false success, resource leak, or deadline violation. Then inspect existing protections: operation identifiers, conditional writes, constraints, transactional boundaries, bounded retries, circuit or load controls, cancellation, and framework guarantees. A remote call inside a retry loop is not automatically unsafe, and absence of an explicit retry in one method does not prove the system lacks one upstream.

Distinguish a confirmed defect from a conditional risk that depends on deployment topology, retry policy, workload, or provider behavior. If those facts are unavailable, request the narrow configuration or contract evidence needed rather than assuming a specific platform.

Recommend the smallest correction that restores the required end-to-end invariant. Do not prescribe retries, circuit breakers, queues, distributed transactions, sagas, or idempotency keys merely because a network boundary exists.
