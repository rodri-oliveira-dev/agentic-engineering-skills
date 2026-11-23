# Identity and access

Read this reference when the scoped surface authenticates an actor, manages a session or token, recovers an account, propagates identity, or authorizes access to a resource or operation.

## Authentication

Trace identity proof from the untrusted boundary through verification, session or token issuance, propagation, renewal, revocation, logout, and sensitive reauthentication. Determine which component is authoritative and which claims downstream components actually verify.

Check only relevant concerns: credential storage and comparison, brute-force and enumeration resistance, multi-factor semantics, recovery and enrollment, session fixation, token audience and issuer, expiration, replay, key selection, service identity, and failure handling. Do not infer token security from its format or a library name; verify validation options and effective configuration.

## Authorization

For each sensitive operation, identify actor, requested action, resource, tenant or owner, policy, enforcement point, and data query. Test conceptually across anonymous, ordinary, owner, other-tenant, privileged, suspended, and stale-privilege states only where those roles exist.

Object identifiers are locators, not authorization. Confirm that server-side policy constrains both the operation and the selected resource before side effects or disclosure. Check alternate routes, background jobs, batch operations, nested resources, exports, administrative endpoints, and cached decisions when present.

For multi-tenant paths, verify that tenant context comes from an authoritative identity or server-side relationship rather than a caller-controlled field, and that lookup, mutation, cache keys, jobs, exports, and downstream calls preserve the same tenant constraint. A resource-level check is effective when it binds actor, action, resource, and tenant before use on every feasible path; do not report IDOR or BOLA merely because an identifier is supplied by the caller.

Account for time-of-check/time-of-use behavior where authorization or ownership can change concurrently. Determine whether the policy decision and protected side effect share an appropriate transaction, lock, version check, or atomic conditional operation. Report a security race only when a feasible interleaving can bypass policy or cross an isolation boundary, not whenever checks and use occur on different lines.

Differentiate missing authorization from a policy that is present but incorrect. Avoid recommending role-based access universally; attribute-, relationship-, ownership-, capability-, or policy-based approaches may fit the established model better.

## Safe validation

Prefer static policy and data-flow tracing plus authorized tests using synthetic identities and isolated resources. Do not use another person's account, enumerate real identifiers, bypass controls, or retain tokens merely to demonstrate impact.

## Official guidance

- [OWASP Authentication Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authentication_Cheat_Sheet.html)
- [OWASP Authorization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html)
- [CWE-862: Missing Authorization](https://cwe.mitre.org/data/definitions/862.html)
