# Compatibility and regression review

Read this reference when the change affects a consumed API, serialized format, schema, protocol, stored data, configuration, dependency, build target, platform, or observable behavior on which callers may rely.

## Identify consumers and overlap

Determine who consumes the contract, which versions coexist, what compatibility promise exists, and whether producer and consumer deployment is coordinated. Compare the before and after contract, including behavior not captured by type signatures.

Trace the changed contract to at least one evidenced consumer or published rule before reporting a break. Include exceptions, error identifiers, retryability, side-effect timing, callback order, resource ownership, and dependency behavior when callers can observe them. An internal symbol can still be compatibility-sensitive when independently deployed components, plugins, persisted data, generated clients, or external integrations consume it.

Check when relevant:

- removed or renamed operations, fields, values, configuration keys, commands, or artifacts;
- changed types, units, formats, defaults, nullability, validation, ordering, pagination, status codes, errors, or timing;
- additive fields or enum values that strict consumers may reject;
- persisted data and migrations read by old and new application versions;
- dependency or runtime changes against supported platforms and lock or resolution behavior;
- changed dependency methods, defaults, error modes, transitive versions, or platform guarantees relied on by the modified path;
- build, packaging, startup, environment, and deployment assumptions;
- staged rollout, feature flags, negotiation, deprecation, rollback, and removal criteria.

Do not call a change breaking solely because it is different. Cite an affected consumer expectation or published compatibility rule and a realistic overlap condition. When consumer evidence is unavailable, describe the uncertainty and request targeted compatibility verification instead of asserting a defect.
