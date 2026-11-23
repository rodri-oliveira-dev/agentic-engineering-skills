# Data protection

Read this reference when the scope handles secrets, credentials, tokens, personal or regulated data, tenant data, cryptographic material, sensitive logs, exports, backups, or deletion.

## Follow the lifecycle

Classify the data and trace collection, validation, use, sharing, storage, caching, logging, analytics, backups, retention, deletion, and transport. Identify actors and components that need access and compare them with actual access. Minimize data and privileges before adding encryption as a compensating measure.

Check whether responses, exceptions, logs, metrics, traces, audit records, URLs, headers, filenames, temporary files, caches, and support tooling expose values beyond their purpose. Logging a hash or partial value may still be identifying or reusable; assess context rather than assuming redaction is safe.

## Secrets and cryptography

Distinguish an actual credential from an example, identifier, public key, test fixture, checksum, or scanner false positive. Establish provenance, parser acceptance, production references, privilege or service context, distribution, and history without exposing the value. A synthetic value confined to tests and rejected by the production parser is not an exposed production credential merely because it has high entropy or a familiar prefix.

If a live secret may be exposed, do not validate it against a service. Preserve minimal evidence, restrict disclosure, and recommend revocation or rotation, history cleanup, incident assessment, and dependent-key handling as appropriate. Exposure evidence does not prove misuse; state that distinction while treating a plausibly valid credential as sensitive.

For cryptography, identify the security goal, threat, algorithm and mode, key source, randomness, nonce or IV rules, authentication, storage, rotation, versioning, and failure behavior. Prefer established platform primitives and protocols. Do not invent custom encryption or prescribe an algorithm without compatibility and key-management context.

Hashing for password verification, integrity, pseudonymization, and general-purpose lookup have different requirements. Encryption at rest does not replace authorization, and TLS does not protect data after termination.

## Safe validation

Inspect metadata and data flow before values. Use redacted samples, synthetic records, and isolated keys. Do not copy production secrets or personal data into prompts, tickets, tests, commands, or reports.

## Official guidance

- [OWASP Secrets Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Secrets_Management_Cheat_Sheet.html)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
- [OWASP Logging Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html)
- [CWE-798: Use of Hard-coded Credentials](https://cwe.mitre.org/data/definitions/798.html)
