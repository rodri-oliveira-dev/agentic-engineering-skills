# API design skill behavioral scenarios

These scenarios support controlled human or agent evaluation of `.agents/skills/api-design/SKILL.md`. They specify expected behavior but are not evidence that behavioral tests were executed. Evaluators should record the proposal, assumptions, evidence, and any actions taken.

## 1. Simple HTTP API

**Input:** Design an internal HTTP API that lets support staff retrieve an order by identifier and cancel an eligible order.

**Expected behavior:** The agent identifies consumers, authorization boundary, order lifecycle, retrieval and cancellation semantics, request and response contracts, failure cases, and compatibility expectations before proposing operations.

**Evaluation criteria:** Methods and status codes match the stated semantics; cancellation eligibility and repeated requests are defined; unauthorized and nonexistent resources do not leak information; no implementation or infrastructure is created.

## 2. Evolve an existing contract

**Input:** An existing mobile API must add an optional delivery instruction to order creation while old app versions remain deployed.

**Expected behavior:** The agent inspects the published schema and consumer behavior, defines absence and validation semantics, classifies the additive change conditionally, and proposes compatibility tests and rollout observation.

**Evaluation criteria:** Old requests remain valid; default or absence behavior is explicit; serialization and strict-client risk are considered; assumptions about deployed clients are labeled.

## 3. Idempotent operation

**Input:** Design a payment-creation endpoint that clients may retry after a timeout.

**Expected behavior:** The agent treats timeout outcome as uncertain, defines an idempotency mechanism with key scope, lifetime, request matching, stored outcome, and concurrent duplicate handling, and separates transport retry from payment state.

**Evaluation criteria:** Repeated equivalent requests cannot create duplicate payments; mismatched reuse is rejected predictably; retryable failures and client guidance are explicit; sensitive payment data is minimized.

## 4. Collection pagination

**Input:** Design an endpoint listing a customer's transactions, with filtering by date and stable navigation while new transactions arrive.

**Expected behavior:** The agent compares cursor and offset behavior against the consistency need, defines deterministic ordering and tie-breaking, limits page size and filters, and states how inserts affect traversal.

**Evaluation criteria:** The contract has bounded page size, stable continuation data, validated filters, and explicit consistency semantics; it does not promise impossible snapshot behavior without supporting infrastructure.

## 5. Error handling

**Input:** Standardize errors across several HTTP endpoints whose clients currently parse free-form messages.

**Expected behavior:** The agent defines stable machine-readable error identifiers, safe details, field validation information, correlation support, retryability, and transport mappings. It evaluates Problem Details against existing project conventions.

**Evaluation criteria:** Clients need not parse prose; validation, authorization, conflict, throttling, and server failures are distinguishable; internal stack or secret data is not exposed; migration from existing errors is addressed.

## 6. Breaking published API change

**Input:** Rename a required response field and remove an enum value from a partner API already in production.

**Expected behavior:** The agent flags both changes as potentially breaking, identifies affected consumers, and proposes a staged deprecation or versioned migration with telemetry, overlap, rollback, and removal criteria.

**Evaluation criteria:** Risk is explicit; the proposal does not silently modify the published contract; consumer migration and serialization compatibility are covered; a deadline alone is not treated as proof of readiness.

## 7. Excessive data exposure

**Input:** A proposed user endpoint returns the persistence entity, including password hash, internal risk score, and tenant metadata, to any authenticated user.

**Expected behavior:** The agent rejects direct entity exposure, defines a minimal response model, and requires resource- and operation-level authorization, tenant isolation, safe logging, and audit decisions where applicable.

**Evaluation criteria:** Authentication is not accepted as sufficient; sensitive and internal fields are excluded; ownership and privileged access are explicit; errors do not reveal forbidden resources.

## 8. Synchronous versus asynchronous communication

**Input:** An order service must notify fulfillment; the business needs rapid order acceptance but fulfillment may be temporarily unavailable.

**Expected behavior:** The agent compares synchronous calls and durable events using latency, availability coupling, consistency, delivery, ordering, duplicate handling, observability, and operational cost. It recommends an option only after relating trade-offs to requirements.

**Evaluation criteria:** No style is treated as universally superior; failure and recovery responsibilities are defined; event delivery semantics and idempotency are addressed if asynchronous communication is chosen; added infrastructure cost is visible.

## 9. Implementation request without sufficient context

**Input:** Ask to implement a public customer API without specifying consumers, operations, data sensitivity, authentication model, compatibility target, or project technology.

**Expected behavior:** The agent inspects available repository evidence, states material unknowns, and asks the minimum design questions before implementation. It may provide a bounded outline with labeled assumptions but does not invent a contract or framework.

**Evaluation criteria:** No server, dependency, or endpoint is created prematurely; consumer, security, compatibility, and operational unknowns are surfaced; questions are decision-relevant rather than exhaustive.

## 10. Request outside design scope

**Input:** An approved OpenAPI contract already exists; ask only to fix a handler bug that returns the wrong mapped value.

**Expected behavior:** The API design skill is not selected as the primary workflow. The existing contract is treated as evidence for the bug fix, and no unrelated redesign is proposed.

**Evaluation criteria:** The response does not reopen settled design decisions, expand the public contract, or confuse implementation correction with API design.
