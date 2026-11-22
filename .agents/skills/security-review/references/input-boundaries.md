# Input boundaries

Read this reference when untrusted data can influence queries, commands, interpreters, templates, paths, network destinations, file handling, parsers, deserialization, redirects, headers, logs, or resource consumption.

## Trace data to a security-sensitive sink

Identify the actor-controlled source, decoding and normalization steps, validation, transformations, security boundary, sink, and execution context. Confirm whether the data changes syntax or control rather than remaining data. Framework escaping, validation, or parameter binding must match the actual sink and context.

Distinguish validation, sanitization, encoding, and structural separation. Validation accepts or rejects values against a trusted contract; sanitization transforms values and is effective only for a defined grammar; encoding protects a specific output context; parameterization keeps data outside interpreter syntax. A control for one context does not automatically protect another.

For injection, prefer APIs that structurally separate code from data. Verify that parameter binding is used for every attacker-influenced value and that dynamic table names, sort expressions, fragments, or commands are not concatenated outside the binding boundary. Correct parameterization that leaves input as data defeats the proposed SQL injection path and must not be reported as vulnerable. Allowlist dynamic identifiers or operations that cannot be parameterized. Context-specific output encoding does not replace safe construction at SQL, shell, LDAP, template, expression, or other interpreter boundaries.

For paths and files, reason from canonical destination and permitted root after decoding and normalization. Include archive entries, links, alternate separators, uploads, content type, size, storage, serving behavior, and permissions only when present.

For SSRF, trace control over scheme, host, port, address resolution, redirects, credentials, proxies, and response handling. Evaluate destination controls after parsing and canonicalization, including allowed schemes and ports, hostname and IP forms, DNS resolution and re-resolution, redirect targets, proxy behavior, and egress policy where applicable. Confirm that the enforced allowlist or broker covers the actual connection destination; when it does, do not report the blocked path as SSRF. Consider access to internal services or metadata only when network reachability and destination control are supported; an outbound request feature is not automatically SSRF.

For deserialization and parsing, identify accepted types, constructors or hooks, polymorphism, object activation, resource limits, integrity protection, and trust of the payload. Do not label ordinary data parsing unsafe without a dangerous capability or material resource impact.

## Validation and false positives

Validation should cover syntax, semantics, size, and allowed values at a trusted boundary. A denylist alone rarely establishes safety, but its presence is not proof of exploitation. Account for canonicalization order and alternate encodings only when the platform accepts them.

Evaluate every control against a concrete bypass hypothesis and the platform's documented behavior. Do not assume a framework helper is sufficient from its name, but do not disregard it without tracing how it parses, normalizes, binds, or rejects the reviewed input.

Validate statically or in an isolated environment with inert, synthetic inputs that demonstrate control without damaging data or reaching unauthorized systems. Do not place executable payloads in production logs, queues, files, or databases merely to prove reachability.

## Official guidance

- [OWASP Input Validation Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html)
- [OWASP SSRF Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html)
- [OWASP Path Traversal guidance](https://owasp.org/www-community/attacks/Path_Traversal)
- [OWASP Deserialization Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Deserialization_Cheat_Sheet.html)
- [CWE-89: SQL Injection](https://cwe.mitre.org/data/definitions/89.html)
- [CWE-918: Server-Side Request Forgery](https://cwe.mitre.org/data/definitions/918.html)
