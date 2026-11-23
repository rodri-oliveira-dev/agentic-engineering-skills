# Security policy

## Supported versions

The project has not published a stable release yet. Security fixes currently target the default branch. This policy will be updated with a supported-version table when the first release is published; do not infer support for an unreleased version from the readiness document.

## Report a vulnerability

Do not disclose a vulnerability, exploit details, credentials, or sensitive repository data in a public issue.

Use GitHub's private vulnerability reporting option in the repository **Security** tab when it is available. If that option is unavailable, contact the maintainer through a private channel listed on the maintainer's GitHub profile and include only enough information to arrange a secure exchange. No response-time commitment is made before a private reporting channel and maintainer capacity have been verified.

Include:

- the affected file, version, or commit;
- prerequisites and a minimal, non-destructive reproduction;
- observed and expected behavior;
- likely impact and any known mitigations;
- environment details, with secrets removed.

Reports may cover installer path handling, overwrite protection, validators, CI configuration, unsafe skill instructions, or prompt-injection boundaries. Vulnerabilities in Codex, GitHub Copilot, Claude Code, Python, PyYAML, or GitHub Actions should also be reported to the relevant upstream vendor.

## Safe research

Use disposable data and environments. Do not access data that is not yours, degrade services, execute destructive payloads, or test against third-party repositories without authorization. A proof of concept should demonstrate the boundary without exposing secrets or causing persistent changes.
