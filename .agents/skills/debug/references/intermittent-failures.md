# Intermittent failures

Read this reference when a failure depends on timing, concurrency, load, resource availability, environment, test order, or a dependency that is not consistently available.

## Make occurrence measurable

Define the failure signature, denominator, time window, affected cohort, environment, workload, and observation reliability. Preserve seeds, inputs, identifiers, versions, machine or container characteristics, clock, locale, test order, concurrency, and resource state when available. “Sometimes” and a retry success are symptoms, not mechanisms.

Compare failing and successful executions across one variable at a time. Repetition can estimate occurrence only when trials are independent and representative; repeated runs without controlling timing or state may hide the causal variable. Do not report a failure percentage unless the run count, setup, and observed outcomes are recorded.

## Investigate common mechanisms

- For a race, identify shared state, concurrent access, missing or insufficient ordering, and a feasible interleaving that violates an invariant. Use barriers, latches, controlled schedulers, or instrumentation instead of timing luck.
- For time-dependent behavior, control clocks, deadlines, expiry, time zones, leap or daylight transitions, scheduling, and eventual assertions where practical.
- For resource starvation, correlate queue depth, workers or threads, connections, file descriptors, memory, CPU, storage, quotas, and wait time with the failing operation. Saturation can be cause, amplifier, or consequence.
- For load-dependent failure, identify the threshold, bottleneck, queueing, backpressure, retry amplification, and recovery behavior using bounded synthetic load in an authorized environment.
- For flaky tests, distinguish product defect, test race, shared state, order dependence, clock/randomness, environment, and external dependency. Do not hide the signal with retries or quarantine without an owned investigation.
- For dependencies, distinguish unavailable, slow, throttled, inconsistent, misconfigured, or unreachable behavior using client and provider evidence when available.
- For local-versus-production differences, compare effective configuration, versions, data shape, scale, topology, permissions, network, time, resource limits, optimization, and instrumentation rather than assuming “environment issue.”

## Reproduce and correct safely

Prefer deterministic coordination, fake or controlled clocks, bounded polling on observable state, isolated synthetic data, recorded dependency responses, and representative resource limits. An arbitrary sleep can reduce occurrence without establishing ordering and can make the test slower or still flaky; use it only when real elapsed time is itself the behavior under test and state why.

Confirm the mechanism by changing one causal condition and observing the predicted result while preserving other relevant conditions. A fix that survives repeated uncontrolled runs is supporting evidence, not proof. Define a regression check that asserts the invariant and fails for the demonstrated mechanism.
