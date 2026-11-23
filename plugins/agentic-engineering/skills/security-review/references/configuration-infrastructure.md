# Configuration and infrastructure

Read this reference when security depends on runtime configuration, environment overlays, permissions, infrastructure as code, containers, orchestration, cloud resources, network exposure, TLS, headers, debug features, or deployment settings.

## Inspect effective state and boundaries

Trace defaults, committed files, templates, environment overrides, secret injection, flags, policy engines, deployment manifests, and runtime state to the effective setting. A secure source default does not prove the deployed value; a dangerous-looking development setting does not prove production exposure.

Relate each setting to a reachable attack path and asset. Check only applicable controls: public exposure, network or tenant boundary, identities and permissions, administrative interfaces, debug or diagnostic features, default accounts, TLS and certificate validation, CORS and browser policy, headers, storage access, container privilege, host mounts, metadata access, logging, backups, and audit.

Distinguish defense-in-depth hardening from a vulnerability. Missing a recommended header or benchmark setting is not automatically exploitable or high severity. Account for upstream gateways, service meshes, platform policies, private networks, and compensating controls only when their effective behavior is evidenced.

Classify environment-dependent settings according to the evidence available. A dangerous effective production setting on a reachable path can support a vulnerability; a setting selected only in development, overridden by an evidenced production control, should not. When environment selection, rendering, or exposure is unknown, state a conditional risk or verification question and identify the exact effective-state evidence needed. Do not silently promote a source default to a deployed fact.

## Safe validation and remediation

Prefer static policy evaluation, rendered-manifest inspection, read-only metadata, and isolated deployment tests. Configuration scanners produce candidates that require context. Do not apply infrastructure plans, open ports, change IAM, disable TLS verification, expose diagnostics, or alter production policy to test a concern.

Recommend least privilege and secure defaults with deployment compatibility, rollout order, lockout risk, availability, observability, and rollback considered. Tightening policy can break legitimate workloads; define pre-deployment checks and post-change monitoring.

## Official guidance

- [OWASP Application Security Verification Standard](https://owasp.org/projects/asvs)
- [OWASP Infrastructure as Code Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Infrastructure_as_Code_Security_Cheat_Sheet.html)
- [OWASP Transport Layer Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Transport_Layer_Security_Cheat_Sheet.html)
