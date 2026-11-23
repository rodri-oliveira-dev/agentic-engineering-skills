# Security review

Read this reference when the diff changes a trust boundary, authentication or authorization, untrusted input, secrets, sensitive data, filesystem or network access, serialization, cryptography, or privileged operations.

## Build a concrete abuse path

Identify the actor, controlled input, privilege boundary, sensitive asset, enforcement point, and observable outcome. A security finding should explain how the changed code makes the path possible; a dangerous-looking API name alone is insufficient.

Check when relevant:

- authorization for the specific operation and resource, including ownership and tenant isolation;
- injection into queries, commands, templates, interpreters, paths, headers, logs, and redirects;
- server-side request destinations, path traversal, archive extraction, and unsafe file permissions;
- validation of structure, meaning, size, and allowed values at the trust boundary;
- exposure of credentials, tokens, personal data, internal identifiers, or forbidden resource existence through responses, logs, metrics, exceptions, and caches;
- unsafe deserialization, dynamic loading, or execution of attacker-controlled content;
- secret generation, storage, transport, comparison, rotation, and accidental repository inclusion;
- cryptographic choices only when their security properties are material to the changed behavior.

Separate exploitability from impact and confidence. Do not label a theoretical weakness exploitable without the required data flow and reachable condition. Recommend fixing the enforcement point or eliminating attacker control rather than adding unrelated defense-in-depth as the primary correction.
