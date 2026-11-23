# Security policy

## Supported versions

| Version or line | Security-fix status |
| --- | --- |
| Default branch (`main`) | Receives current security corrections |
| Latest stable release (`1.0.0`) | Supported; a fix may require users to update to a newer stable release when one is published |
| Versions older than `1.0.0` | Not supported |

This small open source project does not promise response times, guaranteed backports, long-term support, or continued support for a fixed release. Maintainers assess reports against the current default branch and latest stable release, then document any affected versions and available remediation. Publication of a fix depends on validation and maintainer capacity.

## Report a vulnerability

Do not disclose a vulnerability, exploit details, credentials, or sensitive repository data in a public issue.

Use [GitHub private vulnerability reporting](https://github.com/rodri-oliveira-dev/agentic-engineering-skills/security/advisories/new). If that option is unavailable, contact the maintainer through a private channel listed on the maintainer's GitHub profile and include only enough information to arrange a secure exchange. No response-time commitment is made.

Privately reported vulnerabilities are reviewed for reproducibility, impact, affected versions, upstream ownership, and a safe remediation. The maintainer may request more evidence, coordinate disclosure privately, or refer an upstream issue to the responsible vendor. A private report does not guarantee acceptance, a particular publication date, or a backport.

Include:

- the affected file, version, or commit;
- prerequisites and a minimal, non-destructive reproduction;
- observed and expected behavior;
- likely impact and any known mitigations;
- environment details, with secrets removed.

Reports may cover installer path handling, overwrite protection, validators, CI configuration, unsafe skill instructions, or prompt-injection boundaries. Vulnerabilities in Codex, GitHub Copilot, Claude Code, Python, PyYAML, or GitHub Actions should also be reported to the relevant upstream vendor.

## Safe research

Use disposable data and environments. Do not access data that is not yours, degrade services, execute destructive payloads, or test against third-party repositories without authorization. A proof of concept should demonstrate the boundary without exposing secrets or causing persistent changes.
