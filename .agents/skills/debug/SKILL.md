---
name: debug
description: Investigate observed failures in applications, tests, integrations, and runtime environments through evidence, falsifiable hypotheses, controlled experiments, and root-cause analysis. Use for troubleshooting and incident diagnosis; do not use primarily for code review, behavior-preserving refactoring, or test creation without a debugging objective.
---

# Debugging

## Outcome

Explain an observed failure with the strongest available evidence, distinguish facts from hypotheses, and recommend the smallest safe correction and regression protection. When evidence cannot establish root cause, provide a bounded leading hypothesis and the next discriminating experiment instead of forcing a diagnosis.

## Use and non-use

Use this skill to investigate failing applications or tests, intermittent behavior, integration failures, runtime and environment problems, incidents, and unexplained changes in correctness, availability, latency, or resource use.

Do not activate it merely to review a diff for possible defects; use code review for that outcome. Do not use it for behavior-preserving restructuring, or for planning and implementing tests when no failure investigation is required. A debugging task may use tests as evidence and define a regression test, but it does not authorize a broad refactor, production change, or test-suite expansion.

## Required context

Obtain the symptom, first and most recent occurrence, affected users or systems, severity, expected and observed behavior, environment, versions, frequency, inputs, reproducibility, and actions already attempted. Establish relevant time zones and clock quality before correlating events across systems.

Inventory available evidence without assuming it exists: logs, stack traces, metrics, distributed traces, events, dumps, failing tests, configuration, deployment and change history, dependency health, and infrastructure signals. Read [evidence sources](references/evidence-sources.md) only for sources that are available and relevant. Preserve raw evidence and provenance when practical; redact secrets and sensitive data.

## Workflow

1. Describe the symptom in observable terms and assess impact: who or what is affected, frequency, duration, severity, and operational urgency. Separate the user-visible failure from downstream symptoms.
2. Establish expected and observed behavior using contracts, tests, runbooks, prior baselines, service objectives, or domain evidence. Do not infer expectation solely from the current implementation.
3. Bound the problem by environment, version, region, tenant, input, time window, component, dependency, and success versus failure cohort. Narrow scope without prematurely excluding shared causes.
4. Collect the safest relevant evidence available and order it along the execution path. Identify the first point at which observed behavior is proven to diverge from expectation; distinguish it from the first place that reports the failure. Record source, timestamp, environment, query or command, filters, and limitations. Never invent logs, metrics, traces, dump contents, test results, or command output.
5. Build a timeline of recent code, configuration, dependency, data, infrastructure, traffic, and operational changes. Treat temporal proximity as a lead, not proof: require a mechanism and discriminating evidence before claiming causality.
6. Formulate falsifiable hypotheses from the first proven divergence. State the proposed mechanism, trigger, predicted observations, potential contributing factors, and evidence that would reject each explanation. Keep facts, inferences, and assumptions visibly separate.
7. Prioritize hypotheses using fit with current evidence, plausibility, impact, ease and safety of discrimination, and explanatory coverage. Do not rank a familiar cause above contradictory evidence.
8. Choose the smallest diagnostic experiment that distinguishes leading hypotheses. Define expected outcomes for each hypothesis, prerequisites, side effects, stop conditions, rollback, data handling, and what result would remain inconclusive.
9. Reproduce the problem when practical in the lowest-risk representative environment. Control one material variable at a time, capture exact inputs and versions, and avoid changing the system before preserving ephemeral evidence.
10. Compare observed experiment results with predictions. Confirm, weaken, or discard hypotheses explicitly, including the initial hypothesis; update the investigation rather than interpreting every result as support for the preferred theory.
11. Identify root cause only when evidence connects the initiating condition through a credible mechanism to the symptom and excludes material alternatives. Record the trigger and contributing factors separately. A fix that appears to work is supporting evidence, not by itself proof of root cause.
12. Propose the smallest correction that addresses the demonstrated mechanism and proportionate changes for contributing factors or detection gaps. Evaluate blast radius, compatibility, rollback, deployment order, observability, and operational risk; keep unrelated cleanup separate.
13. Define a regression test, production-safe invariant check, alert, reconciliation, or other durable verification that detects recurrence at the appropriate boundary. If implementing automated tests becomes the primary deliverable, use the testing workflow.
14. Document the symptom, impact, timeline, evidence, hypotheses and outcomes, confirmed root cause or leading hypothesis, confidence, correction, checks actually executed, gaps, and remaining risks.

## Hypothesis and confidence discipline

Use these labels consistently:

- **Symptom:** the observed user- or system-visible deviation that initiated the investigation.
- **Observed fact:** directly supported by identified evidence.
- **Inference:** a conclusion logically derived from facts, with the reasoning stated.
- **Hypothesis:** a testable proposed explanation that is not yet confirmed.
- **Trigger:** the event or condition that activates a latent defect or failure mechanism; removing it may prevent one occurrence without removing the underlying cause.
- **Contributing factor:** a condition that increases likelihood, duration, propagation, or impact but is neither necessary nor sufficient as the primary cause.
- **Confirmed root cause:** a demonstrated mechanism that explains the symptom and is supported by reproduction, discriminating evidence, correction validation, or an equivalently strong causal chain.

State confidence as **high**, **medium**, or **low** and explain what raises or limits it. Confidence describes evidentiary strength, not incident impact. Absence of a log entry, error, or reproduced failure is not proof that the event or defect did not occur unless the source is known to capture it reliably.

Do not use “root cause” for the first alert, last visible error, correlated deployment, high-utilization metric, or condition that merely made detection more likely. A root cause should explain why the first proven divergence occurred and how it propagated to the symptom. If the chain cannot be established, report a leading hypothesis and the next discriminating check.

## Distributed systems

Read [distributed systems](references/distributed-systems.md) when the path crosses processes, services, queues, databases, networks, regions, or infrastructure. Investigate timeouts, retries, transient failures, duplicate processing, concurrency, deadlocks, eventual consistency, communication, configuration, latency, saturation, and infrastructure through observable signals rather than technology assumptions.

Trace one failing operation end to end when correlation data permits. Account for partial failure, independent clocks, uncertain outcomes, retry amplification, queueing, backpressure, and different component versions. Do not assume the first service reporting an error caused it or that a downstream timeout means the downstream service was unavailable.

Correlate logs, metrics, traces, and events using operation identity, component/version, cohort, and time window while respecting sampling, aggregation, and clock limitations. Verify trace and correlation identifier creation and propagation across synchronous, asynchronous, retry, batch, and message boundaries. Missing or reused identifiers limit correlation; they do not prove unrelated or identical operations.

## Intermittent failures

Read [intermittent failures](references/intermittent-failures.md) when occurrence depends on timing, concurrency, load, resource availability, environment, test order, or an unreliable dependency. Prefer controlled scheduling, bounded polling on observable state, synthetic load, cohort comparison, and resource telemetry over arbitrary sleeps or repeated execution until failure.

## Operational safety

Classify each action before taking it:

- **Observation:** read existing code, configuration, telemetry, state, or artifacts without intentionally changing runtime behavior. Start here. Observation can still expose sensitive data or add load; minimize scope, time range, fields, cardinality, and privileges.
- **Reversible experiment:** introduce a bounded, temporary change in a controlled environment with known side effects, stop conditions, and rollback. Confirm the target and authorization when it affects shared resources.
- **Operational intervention:** change production state or behavior, including restart, rollback, traffic shift, feature flag, configuration, scaling, failover, data repair, cache clearing, or dependency action. Require explicit authorization for the exact scope and disclose impact and recovery steps first.

Do not run destructive or load-generating experiments indiscriminately, modify production without authorization, restart services automatically, delete evidence, or disable authentication, authorization, encryption, validation, audit, or other security controls to simplify diagnosis. Use synthetic or redacted data and non-production environments when they can answer the question faithfully.

Escalate from observation to reversible experiment and then to operational intervention only when the prior level cannot discriminate the material hypotheses. Before an action that could worsen an incident, increase load, change state, consume capacity, or affect recovery, require explicit authorization for the target and disclose predicted signals, blast radius, stop condition, and rollback.

Before capturing or sharing logs, traces, events, dumps, environment values, request bodies, or database results, minimize and redact credentials, tokens, keys, personal data, tenant data, and proprietary payloads. Do not place secrets into diagnostic commands, fixtures, issue reports, or regression tests.

## Report format

Keep the result concise and proportional to the incident:

```markdown
## Debugging result

- **Symptom:** observed failure and conditions
- **Impact:** affected scope, severity, frequency, and duration
- **Evidence:** relevant facts with source and time window
- **First proven divergence:** earliest evidenced departure from expected behavior, distinct from the reporting component
- **Hypotheses evaluated:** prediction, experiment or evidence, and disposition
- **Root cause or leading hypothesis:** confirmed mechanism, or explicitly unconfirmed explanation
- **Trigger and contributing factors:** distinct roles, or “not established”
- **Confidence:** high, medium, or low, with rationale
- **Recommended correction:** smallest proportional fix and operational considerations
- **Verifications executed:** exact checks and observed results
- **Gaps and remaining risks:** unavailable evidence, untested paths, and next safe step
```

Report checks not run and why. Do not state that a command, test, reproduction, query, deployment, rollback, or fix validation succeeded unless its execution and outcome were observed.

Separate evidence types in the report:

- **Automated verifications:** exact commands or tools actually run, environment, observed outcome, and relevant limitations.
- **Documented scenarios:** proposed reproductions or fixture cases that were not executed; never describe them as passing tests.
- **Executed behavioral evaluations:** platform or agent, exact input, observed response, evaluation criteria, disposition, and limitations. Do not report accuracy percentages without a defined dataset and observed results.

## Limits and failure handling

If reproduction is impossible, use passive evidence, cohort comparison, controlled simulation, or additional instrumentation as appropriate and label the reduced confidence. Instrumentation is a system change: assess performance, privacy, cardinality, retention, and deployment effects before proposing or enabling it.

If evidence conflicts, preserve the conflict and design an experiment that can resolve it. If access, retention, permissions, tooling, or environment prevents progress, state the precise blocker and the minimum evidence or authority needed. Preserve unrelated work and do not commit, push, post incident updates, or perform operational changes unless separately requested and authorized.
