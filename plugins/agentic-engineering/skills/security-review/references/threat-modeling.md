# Focused threat modeling

Read this reference for architecture, multi-component, multi-tenant, or cross-boundary reviews where a compact threat model helps prioritize analysis. Do not require a complete threat-modeling methodology for a local code path that can be assessed directly.

## Build review paths

Identify only elements that change the assessment:

- assets and the confidentiality, integrity, availability, safety, privacy, or tenant consequence of losing them;
- actors, including ordinary users, tenant administrators, service identities, operators, build systems, external providers, and plausible attackers, with their actual starting capabilities;
- entry points and untrusted inputs through which those actors can influence the system;
- trust boundaries where identity, data, code, privilege, or administrative control changes;
- privileged operations and sensitive data flows;
- controls and the component that authoritatively enforces each one;
- assumptions whose failure would create or remove an attack path.

Express a candidate path compactly as actor and capability -> entry point -> trust boundary -> operation or sink -> asset and impact. Attach the existing control and its evidence to the boundary it is expected to protect. This is a prioritization model, not proof of a vulnerability.

## Challenge the model with evidence

Check whether the actor can reach the entry point, whether the input or identity retains the claimed influence, whether every boundary transition is represented, and whether the final capability produces the stated impact. Include alternate routes, asynchronous consumers, callbacks, administrative paths, cached decisions, and failure behavior only when the architecture contains them.

For tenant isolation, identify the authoritative tenant context, how it is bound to identity, how resource queries are constrained, and whether background or privileged paths preserve that binding. Treat tenant crossover as supported only when a feasible actor-to-resource path bypasses or misapplies those controls.

Model controls as effective only when evidence covers their placement, configuration, failure mode, and relevant path. A gateway control may not protect an internal consumer; a service check may make an apparent missing controller check safe. Conversely, a named control or design document does not prove its deployed enforcement.

## Scope and output

Prioritize paths with material assets and plausible actors. Do not enumerate a generic threat catalog, infer malicious actors without a relevant capability, or inflate severity because a path crosses many components. Record assumptions and unavailable deployment facts as limitations or verification questions.

Use the model to select code, configuration, dependency, and validation evidence. Report only candidates that satisfy the skill's evidence threshold; keep defensive improvements without a demonstrated weakness separate from vulnerability findings.

## Official guidance

- [OWASP Threat Modeling Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Threat_Modeling_Cheat_Sheet.html)
- [OWASP Application Security Verification Standard](https://owasp.org/projects/asvs)
