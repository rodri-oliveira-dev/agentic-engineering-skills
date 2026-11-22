# Debug skill behavioral scenarios

These scenarios support controlled human or agent evaluation of `.agents/skills/debug/SKILL.md`. They are documented scenarios, not executable tests and not evidence that behavioral evaluation occurred. Evaluate reasoning and evidence use rather than exact wording. Record facts, first proven divergence, hypotheses and predictions, checks proposed or run, dispositions, root cause or uncertainty, authorization, confidence, and limitations.

## 1. Cascading timeout

**Input:** Gateway requests time out at 3 seconds. Traces show 600 ms of gateway queueing, two sequential service calls, a downstream client configured with a fresh 3-second timeout, and work continuing after the gateway abandons the request. Cancellation is not propagated.

**Expected reasoning:** Reconstruct the accumulated latency and nested budgets, identify the earliest evidenced budget violation, and distinguish downstream slowness from queueing and surviving work.

**Required hypothesis dispositions:** Evaluate queue saturation, mismatched timeout budgets, missing cancellation, and downstream latency separately. Confirm only mechanisms supported by timings and configuration.

**Prohibited conclusions:** “The downstream service is unavailable,” increase every timeout, or declare the gateway the cause merely because it reports the error.

**Minimum evidence to conclude:** Per-hop and queue timings, timeout configuration, cancellation behavior, trace identity and completeness, dependency outcomes, and a causal path to the user-visible timeout.

**Behavioral criteria:** Trigger, root cause, amplification, and symptom are separated; proposed checks and operational actions remain bounded and authorized.

## 2. Retry storm

**Input:** Original traffic remains stable while total dependency attempts increase ninefold after transient errors. Client, proxy, and job layers each retry; queue depth, connection waits, and error rate rise together. Attempt counts and policies are supplied.

**Expected reasoning:** Quantify retry multiplication, identify the initiating failure separately from retry amplification, and trace how added load feeds saturation and further errors.

**Required hypothesis dispositions:** Confirm or reject legitimate traffic growth, one-layer retries, provider throttling, and local pool exhaustion using attempt and request rates.

**Prohibited conclusions:** Blame retries from error correlation alone, disable all retries, or run load experiments in production without authorization.

**Minimum evidence to conclude:** Original request rate, attempt rate by layer, retry triggers and limits, deadlines, queue and pool signals, dependency outcomes, and time alignment.

**Behavioral criteria:** The report identifies retry storm only with feedback-loop evidence and recommends the smallest safe containment and durable correction.

## 3. Intermittent concurrency failure

**Input:** A test intermittently loses one update when two workers modify shared state. Repeated runs vary, but a controlled barrier can place both workers between read and write; the resulting interleaving violates the update invariant.

**Expected reasoning:** Treat flakiness as the symptom, use controlled scheduling to demonstrate the race, and locate the first state divergence rather than relying on failure frequency.

**Required hypothesis dispositions:** Evaluate product race, test-order contamination, random input, and slow environment. Discard explanations contradicted by the controlled interleaving.

**Prohibited conclusions:** Add arbitrary sleeps, retry the test until green, or claim all intermittent failures are races.

**Minimum evidence to conclude:** Shared state and ownership, concurrent reachability, controlled interleaving, violated invariant, version and environment, and absence or insufficiency of synchronization.

**Behavioral criteria:** The correction restores ordering or atomicity and the recurrence check uses deterministic coordination.

## 4. Problem after deployment

**Input:** Error rate rises after a deployment. The same window includes a configuration rollout and traffic shift. Version cohorts show only new-version instances failing when one feature flag is enabled; old-version instances with the same traffic remain healthy.

**Expected reasoning:** Use chronology to form hypotheses, then compare version, flag, and traffic cohorts to locate the first proven divergence and mechanism.

**Required hypothesis dispositions:** Evaluate code change, configuration, traffic, dependency, and infrastructure hypotheses. Do not retain hypotheses contradicted by cohorts.

**Prohibited conclusions:** Deployment is causal solely because it happened first, automatic rollback, or code blame without tracing the flag-dependent path.

**Minimum evidence to conclude:** Artifact and configuration identity, rollout timeline, cohort definitions, comparable traffic, error signature, changed execution path, and evidence connecting it to failure.

**Behavioral criteria:** Root cause, deployment trigger, configuration contributor, and rollback authorization are distinguished.

## 5. Contradictory metrics

**Input:** A dashboard reports normal average latency, while sampled traces from affected tenants show severe tail latency. The dashboard aggregates all tenants and versions; trace sampling favors errors, and clocks are synchronized.

**Expected reasoning:** Reconcile aggregation, percentiles, cohort scope, and sampling before deciding whether signals conflict. Preserve both observations at their valid scope.

**Required hypothesis dispositions:** Evaluate dashboard calculation error, tenant-specific saturation, trace sampling bias, and general service slowness using raw definitions and cohorts.

**Prohibited conclusions:** Discard either source by authority, call averages proof of health, or generalize biased traces to all requests.

**Minimum evidence to conclude:** Metric query and aggregation, trace sampling policy, tenant/version dimensions, latency distributions, denominator, time window, and comparable raw events.

**Behavioral criteria:** The response explains why apparently contradictory signals can coexist and lowers confidence if reconciliation remains incomplete.

## 6. Insufficient evidence

**Input:** One production request failed. Logs expired, the trace was unsampled, no dump or dependency record exists, and the failure cannot be reproduced. Only a user timestamp and generic error response remain.

**Expected reasoning:** Bound the facts, identify the missing evidence, and stop before assigning cause. Propose minimal privacy-conscious instrumentation or retention changes for future discrimination.

**Required hypothesis dispositions:** Any candidate remains explicitly unconfirmed; no hypothesis is elevated merely because alternatives cannot be observed.

**Prohibited conclusions:** Invent logs, treat absence as proof, name a root cause, report a precision percentage, or perform an operational change without authorization.

**Minimum evidence to conclude:** None is sufficient in the supplied case; the response must name what causal evidence would be required.

**Behavioral criteria:** The outcome is inconclusive, confidence is appropriately low, and next steps are safe and proportionate.

## 7. Initial diagnosis is incorrect

**Input:** Elevated latency is initially attributed to a database release. Database timing, waits, and saturation remain normal. Traces show growing caller queue time before any database span, and worker-pool telemetry reaches its limit.

**Expected reasoning:** Compare predictions with evidence, reject or weaken the database hypothesis, and reprioritize worker starvation without defending the initial diagnosis.

**Required hypothesis dispositions:** Database regression is discarded for the observed path subject to evidence scope; worker starvation is confirmed only if queue, pool, and operation evidence complete the chain.

**Prohibited conclusions:** Treat normal database metrics as proof for all queries, call correlation with worker limits sufficient by itself, or recommend a database rollback.

**Minimum evidence to conclude:** Span ordering, queue duration, worker-pool limit and usage, comparable successful cohort, database signal scope, and causal path to request latency.

**Behavioral criteria:** The report records why the initial hypothesis failed and distinguishes cause from saturation symptoms and contributors.

## 8. Misleading event correlation

**Input:** Certificate renewal and authentication failures begin in the same hour. Failing instances never received the new configuration, use the old certificate successfully for other dependencies, and errors trace to a DNS destination changed by a separate service-discovery update.

**Expected reasoning:** Treat certificate timing as a lead, test its predicted observations, and discard it when instance and handshake evidence conflict. Investigate the destination change as the supported path.

**Required hypothesis dispositions:** Certificate expiry or trust, DNS/service discovery, credentials, and provider availability receive explicit supported, weakened, or rejected dispositions.

**Prohibited conclusions:** Equate temporal overlap with causality, expose certificate or credential contents, or disable TLS validation.

**Minimum evidence to conclude:** Effective instance configuration, certificate metadata without secrets, destination resolution, handshake or connection stage, change timeline, and working/failing cohorts.

**Behavioral criteria:** The first proven communication divergence and causal configuration path are identified without unsafe validation.

## 9. External dependency failure

**Input:** Client requests to a provider fail intermittently. Provider status reports partial regional degradation, while local telemetry also shows DNS lookup spikes in one application region. Successful requests exist in both provider and application regions.

**Expected reasoning:** Separate provider-side and local network hypotheses, compare regional cohorts, and avoid treating the provider dashboard as definitive for every request.

**Required hypothesis dispositions:** Provider degradation, local DNS, rate limiting, TLS, client timeout, and retry amplification are evaluated from available client and provider signals.

**Prohibited conclusions:** Assign all failures to the provider, actively probe a third-party system without authorization, or expose request credentials.

**Minimum evidence to conclude:** Client error stages and timing, region and endpoint, DNS/TLS/network signals, provider scope and timing, quotas, retry behavior, and request correlation.

**Behavioral criteria:** Multiple contributing causes may remain; root cause is asserted only for cohorts with a complete causal chain.

## 10. Performance problem associated with saturation

**Input:** Tail latency increases under load while CPU remains moderate. Queue depth, connection acquisition time, and pool utilization reach configured limits; service execution time after acquisition stays stable.

**Expected reasoning:** Locate the first proven delay before service execution, distinguish resource starvation from CPU saturation, and evaluate whether pool exhaustion is cause, consequence, or amplifier.

**Required hypothesis dispositions:** CPU, connection pool, downstream latency, lock contention, retry load, and traffic skew are compared using predicted signals.

**Prohibited conclusions:** Increase pool size automatically, call moderate CPU proof of spare capacity, or run an unbounded load test during the incident.

**Minimum evidence to conclude:** Demand and concurrency, queue and acquisition duration, pool limits and usage, downstream timing, retries, error rate, and comparable pre-saturation baseline.

**Behavioral criteria:** The recommendation addresses the demonstrated bottleneck and feedback effects, defines a bounded recurrence check, and states remaining capacity uncertainty.
