# DBMS differences

Read this reference when syntax or behavior depends on PostgreSQL, SQL Server, MySQL, or another relational engine. It is a routing guide, not a substitute for authoritative documentation for the deployed version.

## Verify instead of translating mechanically

Check the actual DBMS/version for:

- identifier quoting, case folding, parameter markers, literals, and reserved words;
- `LIMIT`/`OFFSET`, `TOP`, `FETCH`, keyset predicates, and null ordering;
- upsert, merge, returning/output clauses, generated identities, and sequence behavior;
- boolean, date/time, interval, JSON, array, text, numeric, collation, and null semantics;
- transaction isolation, MVCC, locking hints or clauses, deadlock handling, and DDL transactions;
- partial/filtered, included/covering, expression, clustered, online/concurrent, and invisible index capabilities;
- estimated versus actual plan commands and whether analysis executes the statement;
- temporary object scope, procedural SQL, batch separators, routines, triggers, and migration syntax.

## Engine-specific cautions

For **PostgreSQL**, distinguish estimate-only `EXPLAIN` from options that execute the statement; verify MVCC visibility, lock levels, concurrent index restrictions, statistics, operator classes, expression/partial index predicates, and extension-dependent behavior.

For **SQL Server**, distinguish estimated and actual execution plans; verify compatibility level, parameter sensitivity, locking or row-versioning configuration, clustered and included-column behavior, online operation support, batch syntax handled by client tooling, and transaction effects of each DDL operation.

For **MySQL**, identify the storage engine and exact version; verify transaction and foreign-key support, isolation and gap-lock behavior, collation, generated columns, index prefix and visibility rules, online DDL algorithm/lock behavior, and whether the chosen plan-analysis form executes the statement.

For **other engines**, obtain their authoritative syntax, transaction, optimizer, index, and DDL guarantees before adapting a proposal. Standards-compliant syntax does not guarantee identical types, plans, isolation, or operational effects.

## Communicate portability

Label dialect-specific SQL and name the tested or intended engine/version. When portability is required, define the supported engine set and choose the shared behavior deliberately; otherwise provide separate variants. Do not hide semantic differences behind a single query whose correctness varies by engine.
