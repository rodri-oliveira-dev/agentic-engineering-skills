# Correctness review

Read this reference when the diff changes business rules, nontrivial control flow, resource lifetime, state transitions, or behavior spread across files.

## Establish the contract

Derive expected behavior from the change objective, existing tests, callers, types, schemas, comments that define invariants, and user-visible behavior. Prefer executable or published contracts over naming conventions. Trace inputs through transformations and side effects to outputs, including early exits and failure paths.

For cross-component changes, map only the affected path: entry point, validation, orchestration, state change, external dependency, response mapping, and cleanup. At each boundary, identify the input and output contract, ownership transfer, error contract, and observable side effects. A locally correct function can still break the end-to-end behavior through a dropped value, reordered effect, stale assumption, or incompatible error translation.

## Validate candidate defects

- Construct a concrete triggering case and follow the changed path step by step.
- Check boundary values, absent or empty values, ordering, units, precision, overflow, identity, and equality only when the affected types and operations make them relevant.
- Compare all branches and state transitions with established preconditions and postconditions.
- Confirm ownership and lifetime for resources that must be closed, disposed, released, or returned.
- Trace mappings across layers for dropped, swapped, defaulted, or stale values.
- Trace exceptions and error values through catch, wrapping, translation, retry, fallback, and response mapping. Confirm that success is not returned after a failed required effect and that diagnostic context is preserved without leaking sensitive internals.
- Verify resource acquisition and release on success, failure, timeout, and cancellation paths. Establish whether ownership is transferred before reporting a leak, premature close, double release, or use-after-release concern.
- Compare changed dependency assumptions—return values, errors, ordering, version, availability, and side effects—with the actual adapter or declared contract when they affect the result.
- Determine whether a changed test asserts the meaningful outcome rather than merely executing the path.

Do not infer a domain invariant solely because a different design seems preferable. Do not demand tests mechanically; identify the specific regression case a test would protect. Report one root cause rather than each downstream symptom.
