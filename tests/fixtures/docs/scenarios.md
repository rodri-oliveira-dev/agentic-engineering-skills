# Docs skill behavioral scenarios

These scenarios support controlled human or agent evaluation of `.agents/skills/docs/SKILL.md`. They are specifications, not evidence that behavioral tests were executed. Evaluators should use disposable working copies and record observed outputs and actions.

## 1. Create a README from a real project

**Input:** In a real checked-out software project with source code, dependency manifests, configuration, tests, and no useful README, ask: "Create a README for developers who want to install, configure, run, and test this project."

**Expected behavior:** The agent identifies developers as the audience, inspects the actual project entry points and supporting files, and creates a concise README using the project's language and terminology. It includes only observed prerequisites, installation, configuration, run, and test instructions. Commands not executed are labeled unverified.

**Evaluation criteria:**

- Every named dependency, path, command, and configuration key is traceable to repository evidence.
- The README lets the stated audience find the essential workflow without duplicating low-value detail.
- The agent does not invent features or claim successful command execution without evidence.

## 2. Update documentation after an API change

**Input:** Provide a repository diff that changes an existing API operation's path, request field, response shape, or error contract, plus its current API documentation. Ask: "Update the API documentation for this change."

**Expected behavior:** The agent inspects the implementation, tests or schema, diff, and current documentation; updates only affected sections and examples; and checks other local references to the changed contract. It distinguishes released/current behavior from proposed behavior when the repository evidence does not establish release status.

**Evaluation criteria:**

- The documented method, path, inputs, outputs, and errors match observable contracts.
- Stale examples and directly affected cross-references are handled without rewriting unrelated sections.
- Any unexecuted request or response example is explicitly identified as unverified.

## 3. Document an architectural decision

**Input:** Provide code and discussion showing a choice between two persistence approaches and ask: "Document why the project chose this architecture."

**Expected behavior:** The agent finds the project's decision-record convention, or proposes a clearly identified location if none exists. It records context, decision, considered alternatives, trade-offs, consequences, and status. It labels conclusions not supported by the supplied evidence instead of presenting them as historical fact.

**Evaluation criteria:**

- The record separates observed rationale from inferred or proposed rationale.
- Component names and architectural boundaries match the repository.
- Material trade-offs and consequences are concise and decision-relevant.

## 4. Project without enough information

**Input:** In a repository containing only a package manifest and an empty source directory, ask: "Write complete installation, configuration, API, and architecture documentation."

**Expected behavior:** The agent inspects the available files, documents only facts they support, lists the missing or unverified information, and asks the minimum questions required to proceed. It does not fabricate commands, endpoints, configuration, or architecture.

**Evaluation criteria:**

- Known facts, hypotheses, proposals, and unknowns are visibly distinct.
- The response explains which evidence was inspected and why it is insufficient.
- Questions are limited to information indispensable for the requested documentation.

## 5. Request outside the skill scope

**Input:** Ask: "Refactor the authentication module and create a commit with a conventional commit message. Do not change documentation."

**Expected behavior:** The docs skill is not activated. The task is routed to implementation, refactoring, and Git workflows as available, with no unsolicited documentation rewrite.

**Evaluation criteria:**

- No documentation file is created or edited merely because code changes are requested.
- The agent does not treat commit-message generation as technical documentation work.
- The explicit instruction not to change documentation is preserved.
