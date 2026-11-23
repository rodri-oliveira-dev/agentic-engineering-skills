# Concurrency and asynchronous review

Read this reference only when the change introduces or alters shared state, parallel execution, asynchronous operations, locks, queues, callbacks, cancellation, background work, or event ordering.

## Reason about interleavings

Identify mutable state, its owners, execution contexts, synchronization mechanism, and required ordering. For a race finding, show at least one feasible interleaving that violates an invariant; shared state alone is not proof of a race.

Before reporting, look for protection through confinement to one execution context, immutability after safe publication, atomic operations, locks, channels or queues, actor/event-loop serialization, database constraints or transactions, framework lifecycle guarantees, and caller synchronization. Verify that the protection covers every access in the proposed interleaving and the lifetime of the shared object. The presence of a non-thread-safe collection or a check-then-act shape is not a defect when reachable accesses are serialized by an evidenced boundary.

Check when relevant:

- compound read-modify-write operations and check-then-act sequences;
- publication and visibility of state across workers;
- lock scope, lock ordering, reentrancy, and work performed while holding a lock;
- atomicity across multiple objects or operations when one local atomic call is insufficient for the invariant;
- task or future lifetime, observation of failures, and structured ownership of background work;
- cancellation and timeout propagation without leaving partial effects;
- duplicate, lost, or reordered queue and event processing;
- thread-affine resources and concurrent use of objects whose contract is not thread-safe;
- blocking waits in execution models where they can deadlock or exhaust workers.

Distinguish deterministic deadlock, demonstrated race, and workload-dependent contention. For a deadlock, establish a feasible wait cycle and lock or resource ownership; long blocking alone is insufficient. Do not claim thread safety or lack of it without repository or platform evidence. Recommend the smallest synchronization, ownership, immutability, constraint, or sequencing correction that restores the invariant without introducing a new ordering or contention problem.
