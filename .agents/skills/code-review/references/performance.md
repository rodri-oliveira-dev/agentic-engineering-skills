# Performance review

Read this reference only when the change plausibly affects a hot path, variable-size input, algorithmic complexity, repeated I/O, query count, allocation volume, blocking, serialization, startup, or another stated performance objective.

## Require an impact model

Relate the changed work to input size, frequency, concurrency, latency, memory, I/O round trips, or an established service objective. Prefer benchmark, profile, query plan, telemetry, or complexity evidence. If workload context is missing, qualify a material risk or omit the finding.

Check when relevant:

- increased asymptotic complexity or repeated scans over growing inputs;
- I/O or database operations moved inside a loop or duplicated across a request;
- unbounded reads, buffering, queues, caches, retries, or fan-out;
- blocking introduced on a latency- or worker-sensitive path;
- query shapes that retrieve substantially more rows or columns, or perform one query per item;
- large or repeated allocations and copies on a demonstrated frequent path;
- contention or serialized work that reduces throughput under expected concurrency;
- expensive work performed eagerly when most paths do not need it.

Do not recommend caching without a valid freshness and invalidation model. Do not demand low-level allocation tricks, loop rewrites, or newer APIs without evidence that the path matters. State the scale condition and expected cost rather than using vague terms such as "slow."
