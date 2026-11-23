# Rollout and recovery

Read this reference when readiness depends on deployment strategy, blast-radius control, feature flags, availability during change, rollback, roll-forward, or failure recovery.

## Choose a strategy from constraints

Identify deployment units, statefulness, compatibility window, traffic control, spare capacity, warm-up, session behavior, regional dependencies, release duration, detection time, and acceptable blast radius. Then select the simplest strategy the platform supports.

- A **rolling** deployment limits simultaneous replacement but requires old/new compatibility and sufficient capacity during turnover.
- A **canary** provides a bounded cohort only when traffic or workload selection is representative and signals can distinguish the cohort quickly.
- **Blue-green** can enable rapid traffic reversal but requires duplicate capacity, state compatibility, controlled cutover, and confidence that shared dependencies remain reversible.
- **Recreate**, maintenance-window, regional, ring, or manual staged approaches may be appropriate when constraints make other strategies misleading or wasteful.

Do not recommend a named strategy without its prerequisites. For rolling updates, verify surge or unavailable capacity, draining, termination behavior, and mixed-version compatibility. For canaries, define a representative cohort, comparison baseline, minimum observation window, progression gates, and automatic or owned stop action; degraded canary indicators block progression even when aggregate fleet signals remain healthy. For blue-green, verify duplicate capacity, traffic-switch semantics, connection draining, shared state, schema and message compatibility, and whether traffic reversal can undo the actual effects.

A feature flag can separate deployment from exposure but introduces configuration, stale-path, ownership, cleanup, and recovery concerns; it is not automatically safer. Establish the safe default, eligible cohort, dependency and schema compatibility in both states, responsible owner, disable procedure, propagation time, observation signal, expiry or removal plan, and behavior if the flag service is unavailable. A flag without a credible and timely disable path is not a recovery control.

## Define progression and interruption

For each stage, specify cohort or unit, start condition, minimum observation period, health and business signals, acceptable ranges, manual or automated decision owner, maximum blast radius, pause threshold, abort threshold, and action after failure. Account for delayed jobs, caches, eventual consistency, and low-traffic paths that may not produce immediate evidence.

Health checks should represent the instance's ability to accept the work assigned to it. Separate process liveness, readiness for traffic, dependency degradation, and deep diagnostics where the platform supports those concepts; avoid health checks that amplify dependency failures.

## Establish recovery

List credible recovery options in order: pause progression, disable exposure, reverse traffic, restore configuration, deploy the prior compatible artifact, roll forward, repair or restore data, fail over, or enter controlled degradation. For each, state prerequisites, operator, commands or runbook location, expected time, data implications, validation, and point beyond which it no longer works.

Rollback must include compatibility with current schema, data, messages, configuration, and dependencies. Evidence can come from a recent representative exercise, a verified deterministic procedure, or platform guarantees appropriate to the risk; the mere existence of an old artifact is insufficient.

Never execute rollout or recovery actions during readiness assessment. If recovery is untested, label that fact and evaluate whether the remaining uncertainty is a blocker or bounded risk based on impact and alternatives.
