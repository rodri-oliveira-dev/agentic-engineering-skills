# Dependencies and supply chain

Read this reference when the scope includes third-party packages, lock files, containers, build plugins, downloaded tools, generated artifacts, update mechanisms, CI/CD workflows, package registries, provenance, or vulnerability advisories.

## Establish the component and path

Identify the resolved component name, ecosystem, version, source, integrity or signature information, transitive path, artifact actually deployed, supported platform, and environment. A manifest range or scanner match may not equal the resolved or reachable production component.

For an advisory, verify affected versions and configurations, vulnerable feature or symbol, deployment reachability, attacker path, existing mitigations, exploit maturity when relevant, and authoritative vendor or database status. Distinguish “package present,” “version affected,” “vulnerable code reachable,” and “exploitable in this environment.” An outdated or end-of-support version may create maintenance risk, but age alone is not evidence of a specific exploitable vulnerability.

When reachability or runtime configuration is unknown, report the advisory match or maintenance state as conditional exposure with the missing evidence rather than inventing exploitability. Conversely, do not dismiss an affected component solely because no public exploit is known; use the supported weakness, path, controls, and impact.

Review install and build scripts, unpinned remote actions or images, registry and namespace ambiguity, dependency confusion, artifact substitution, compromised maintainer risk, excessive CI permissions, secret exposure, provenance, and update channel only where the actual pipeline contains those surfaces.

## Remediation

Prefer a vendor-fixed compatible version or removal of unused functionality. Assess lockfile consistency, transitive constraints, API and data compatibility, build reproducibility, platform support, regression scope, and rollback. A forced override can introduce incompatibility or leave another copy unresolved; verify the final dependency graph and deployed artifact.

Do not execute package scripts, download untrusted proof-of-concept code, or publish a dependency update as part of review. If no fix exists, describe a verified mitigation, affected feature isolation, monitoring, or acceptance decision with an owner and expiry rather than claiming the dependency is safe.

## Official guidance

- [OWASP Vulnerable Dependency Management Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Vulnerable_Dependency_Management_Cheat_Sheet.html)
- [OWASP Software Supply Chain Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Software_Supply_Chain_Security_Cheat_Sheet.html)
- [CWE-1104: Use of Unmaintained Third Party Components](https://cwe.mitre.org/data/definitions/1104.html)
