# Evidence sources

Read only the sections matching evidence that is available and relevant. Record provenance, time range, environment, filters, sampling, retention, and known gaps before drawing conclusions.

## Logs and stack traces

Use structured fields, severity, timestamps, correlation identifiers, component/version, and surrounding events to reconstruct a path. Preserve the complete exception chain and relevant stack frames; the top message may be a wrapper or downstream symptom. Check sampling, truncation, buffering, asynchronous delivery, clock skew, and log-level changes before interpreting absence.

Verify where trace IDs, span IDs, correlation IDs, request IDs, message IDs, operation IDs, and idempotency keys are created, transformed, reused, or dropped. An identifier should connect records from one logical operation under its documented scope; a shared batch, retry, or tenant identifier may correlate unrelated work, while a new identifier per retry may hide one operation's attempts.

Redact credentials, tokens, personal data, request bodies, connection strings, and tenant-specific values. Avoid broad production log queries or increased verbosity without considering access, cost, volume, privacy, and performance.

## Metrics and traces

Correlate rate, errors, duration, and saturation with baselines and affected cohorts. Inspect distribution and percentiles rather than averages alone when tail behavior matters. Confirm label meaning, aggregation, scrape interval, missing series, resets, sampling, and dashboard transformations.

Use distributed traces to follow causal and temporal relationships across spans, while accounting for missing sampling, broken propagation, asynchronous boundaries, retries, and clock differences. A slow child span may represent waiting, throttling, or downstream work; trace shape alone does not establish root cause.

Correlate signals only after aligning scope and semantics. A service-level metric may aggregate versions, regions, tenants, or success and failure cohorts that a trace isolates. Contradictory signals can both be correct at different aggregation levels or time windows; inspect raw definitions and cohorts before choosing one as authoritative.

## Events and dumps

Use platform, runtime, audit, deployment, orchestration, and infrastructure events to build a timeline and identify state transitions. Verify source clocks, deduplication, retention, and whether an event reports intent, acceptance, or completion.

Dumps, heap snapshots, profiles, packet captures, and thread snapshots can expose secrets and impose pause, CPU, memory, disk, or network costs. Capture them only with appropriate authorization, scope, storage, retention, and transfer controls. Interpret them with symbols and versions matching the observed process when required.

## Tests and reproduction

A failing test or minimal reproduction is strong evidence only when it exercises the same contract and relevant environment conditions. Record exact inputs, seed, clock, locale, dependency versions, concurrency, and setup. A passing run does not disprove an intermittent defect; repeated runs without controlled scheduling may add little evidence.

## Configuration and changes

Compare effective runtime configuration, not only source files or declared defaults. Account for environment overlays, flags, secrets, permissions, service discovery, certificates, quotas, compatibility modes, and rollout state without exposing values.

Review code, dependency, schema, configuration, infrastructure, traffic, and data changes in the relevant window. Use before/after cohorts, rollback or replay in a safe environment, or a mechanism-specific experiment to test causality. “Started after deployment” establishes chronology, not causation.

## External dependencies

Inspect client-side timing, status or error categories, provider health, quotas, throttling, DNS and certificate behavior, protocol negotiation, and contract/version changes where available. Provider dashboards and status pages are evidence with scope and latency limits, not definitive explanations for every request.
