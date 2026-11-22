# Observability and capacity

Read this reference when the release changes behavior, dependencies, latency, throughput, resource demand, background work, scaling, health checks, or failure modes.

## Observe the changed path

Map each material release risk to a signal that can detect it within the available decision window. Use relevant logs, metrics, traces, events, health checks, synthetic journeys, queue or data checks, and business outcomes. Confirm signal source, dimensions, baseline, expected range, delay, sampling, retention, dashboard or query, alert ownership, and access.

Telemetry existence is not sufficient. Verify that failures are distinguishable by release version, environment, region, tenant or cohort where appropriate and that sensitive data is not exposed. Deploy markers and correlation identifiers should connect change timing to observed effects without assuming correlation proves causation.

Use existing SLIs, SLOs, error budgets, and operational objectives when they describe the changed user journey or dependency. Translate them into rollout decisions using a baseline, evaluation window, allowed degradation, burn or consumption threshold, and response owner. Do not invent an SLO, require one for every low-risk release, or treat a fleet-wide average as sufficient when a canary cohort can degrade independently.

Distinguish liveness, readiness, startup, and deep diagnostic signals by their operational purpose. Liveness should support recovery from a stuck process without causing restart loops during dependency failure; readiness should remove a unit that cannot safely accept assigned work; deep diagnostics may be unsuitable for high-frequency traffic gating. Verify the platform's actual semantics before recommending a probe name or behavior.

## Assess capacity and saturation

Compare expected traffic and workload with representative evidence for CPU, memory, storage, I/O, connections, workers, queues, rate limits, third-party quotas, database capacity, and network where relevant. Consider startup and warm-up peaks, cache behavior, migration load, retry amplification, background processing, partial capacity during rollout, and autoscaling delay.

Do not claim capacity from resource limits or averages alone. Tail latency, saturation, skew, burst behavior, and the bottleneck resource may matter. If representative load evidence is absent for a material workload change, classify the gap rather than inventing headroom.

## Define post-deployment verification

Create two layers when relevant:

1. Immediate checks: artifact/version, startup, configuration reference, health, critical smoke path, error rate, latency, saturation, and migration state.
2. Observation-window checks: delayed jobs, retries, queue age, data consistency, resource trend, business outcomes, consumer errors, and low-volume paths.

For external dependencies, include the consumer-observed outcome, timeout and retry amplification, quota or rate-limit headroom, fallback activation, and dependency-specific health only when those signals affect release safety. A provider status page alone does not prove the application's integration is healthy.

For each check, state owner, time, exact signal, baseline, threshold, and response. “Monitor logs” is not actionable. Ensure stop and recovery thresholds can be evaluated before blast radius exceeds the accepted limit.
