---
name: api-design
description: Design or evolve APIs and integration contracts by identifying consumers, choosing an appropriate interaction style, and defining operations, errors, security, and compatibility. Use for API contract design or review; do not use for implementation-only work, dedicated vulnerability audits, or documentation-only updates.
---

# API design

## Outcome

Produce a comprehensible, testable API contract and an evidence-based design rationale that meet known consumer needs without unnecessary architectural or operational complexity. Make assumptions, trade-offs, compatibility risks, and unresolved questions explicit.

## Use and non-use

Use this skill to design a new API, review an API proposal, choose an integration style, or evolve a published contract.

Do not activate it for implementation with an already approved contract, documentation-only synchronization, general code refactoring, or a dedicated security vulnerability assessment. A design-only request does not authorize implementing endpoints, schemas, infrastructure, or clients.

## Required context

Identify the business capability, consumers, ownership boundary, deployment environment, existing technologies, published contracts, expected scale, data sensitivity, and operational constraints. Separate confirmed requirements from assumptions and ask only for missing information that materially changes the contract or integration choice.

## Workflow

1. Define the API's objective, bounded responsibility, success criteria, and explicit non-goals. Avoid exposing internal implementation structure as the contract by default.
2. Identify human, service, partner, device, or event consumers and their capabilities, trust boundaries, latency needs, release independence, and tolerance for change.
3. Capture functional requirements as consumer operations and observable outcomes. Record relevant quality attributes such as availability, latency, throughput, consistency, durability, privacy, auditability, evolvability, and operational cost.
4. Compare integration styles in context. HTTP resource or action APIs favor broad interoperability; gRPC can favor typed internal RPC and streaming; GraphQL can support client-shaped queries with added governance and execution complexity; events can decouple producers and consumers but require delivery, ordering, schema, idempotency, and observability decisions. Do not impose REST or any other style universally.
5. Model resources, commands, queries, events, and operation boundaries using domain terms already established by the project. Define identity, lifecycle, ownership, state transitions, and consistency boundaries without adding abstraction that has no requirement.
6. Specify inputs and outputs: required and optional fields, types, constraints, defaults, nullability, units, formats, ordering, metadata, and examples. Distinguish transport envelopes from domain data and minimize sensitive data exposure.
7. Define failures as part of the contract. Provide stable machine-readable codes, safe human-readable detail, correlation information where useful, retryability, and mappings to transport semantics. Do not leak secrets, internals, or resource existence across authorization boundaries.
8. Design authentication and authorization separately. Define access per resource and operation, tenant or ownership isolation, input and consumption limits, abuse controls, sensitive-data handling, and applicable audit events. Authentication alone does not make an API secure.
9. Analyze retries, timeouts, duplicate delivery, idempotency, concurrency, partial failure, cancellation, and recovery across the full interaction. Assign responsibility to clients, servers, intermediaries, and operators rather than leaving network behavior implicit.
10. Classify every evolution proposal as compatible, conditionally compatible, or breaking for published contracts and known consumers. Plan deprecation, observability, incremental migration, rollback, and removal; state consumer risks explicitly.
11. Validate the contract with representative consumer flows, boundary and negative cases, schema or specification checks, examples, and compatibility tests when available. Verify that implementation technology can support the design, but do not implement it unless requested.
12. Record decisions, alternatives, trade-offs, rejected complexity, operational impacts, assumptions, and open questions. Keep the result consistent with project terminology and existing platforms.

## HTTP contract guidance

For an HTTP API, always align method semantics, status codes, resource or action naming, input validation, error representation, access control, and compatibility expectations. Treat safe and idempotent method properties accurately: reads must not cause unintended state change, retries must not duplicate effects, and `POST`, `PUT`, `PATCH`, and `DELETE` semantics must be defined rather than inferred from naming. Choose success and error status codes that reflect the actual outcome, including asynchronous acceptance, conflicts, preconditions, authorization failures, throttling, and server failures.

Use Problem Details when it fits the project's standards and clients; otherwise define an equally consistent error schema. Do not adopt it as a label without specifying stable application error identifiers and safe details.

Apply these mechanisms only when requirements justify them:

- Paginate collections that can grow beyond safe response or query bounds; define stable ordering, cursor or offset behavior, limits, and consistency expectations.
- Define allowlisted filtering and sorting semantics, validation, cost limits, and deterministic tie-breaking.
- Use idempotency keys or another deduplication strategy for retryable operations whose repeated execution could duplicate effects; define key scope, lifetime, request matching, and replayed responses.
- Define end-to-end timeouts and cancellation. Recommend retries only for classified transient failures, with bounded attempts, backoff, jitter, and idempotency awareness.
- Add rate limits and abuse protection based on resource cost and threat context; document client-visible limits and retry guidance where appropriate.
- Define optimistic or pessimistic concurrency controls when lost updates or conflicting commands matter.
- Enable caching only with explicit freshness, validation, privacy, and invalidation semantics.
- Introduce URL, header, media-type, or schema versioning only with a demonstrated evolution need and a migration policy.
- Maintain OpenAPI when a machine-readable HTTP contract benefits validation, client generation, testing, or governance; keep it synchronized with approved behavior.

## Security and evolution safeguards

- Minimize returned and logged data; classify sensitive fields and prevent over-broad object serialization.
- Validate structure, semantics, size, ranges, and allowed values at the trust boundary. Consider query complexity and payload limits, not only field syntax.
- Enforce authorization for the specific resource and operation, including tenant isolation and indirect object access.
- Design errors, metrics, traces, and audit records to support operations without exposing credentials, personal data, internals, or forbidden resource existence.
- Identify changes to required fields, types, nullability, defaults, enum values, identifiers, ordering, error behavior, serialization, and timing as potential consumer breaks. Additive changes are not automatically safe for strict consumers.
- Account for deployed consumers and tolerant-reader behavior rather than reasoning from the latest schema alone. Prefer staged migration and measurable deprecation over abrupt removal.
- For a dedicated vulnerability assessment, compose this skill with `security-review`; keep baseline contract security decisions in this workflow and do not turn API design into an AppSec audit.

## Limits and uncertainty

- Respect the project's existing technologies and constraints unless evidence supports changing them.
- Do not recommend gateways, brokers, service meshes, new protocols, patterns, or versioning merely because they are common.
- Surface cost, latency, failure modes, consistency, deployment, monitoring, and support burden for each material option.
- If consumer, security, scale, or compatibility information is insufficient, provide a bounded proposal with labeled assumptions or stop before irreversible design or implementation.
- Do not claim a contract is secure, compatible, validated, or implemented without corresponding evidence. Report checks not run and why.
- Preserve unrelated work and do not commit or push automatically.
