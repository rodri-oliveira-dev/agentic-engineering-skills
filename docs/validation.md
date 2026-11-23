# Validation and testing

The repository validator checks structural conformance and selected maintainability rules without executing any code bundled with a skill. It requires Python 3.11 or newer and one pinned runtime dependency, `PyYAML==6.0.4`.

## Setup and commands

Install the declared dependency in a virtual environment:

```shell
python -m venv .venv
python -m pip install -r requirements.txt
```

Activate the environment using the command appropriate for the operating system, then validate the required canonical catalog:

```shell
python scripts/validate_skills.py --require-skills
```

Useful modes:

```shell
# Validate one direct child of .agents/skills
python scripts/validate_skills.py --skill code-review

# Fail if the catalog contains no skills (intended for CI after skills exist)
python scripts/validate_skills.py --require-skills

# Validate an isolated catalog, useful for local test scenarios
python scripts/validate_skills.py --root path/to/skills
```

Run all automated tests from the repository root:

```shell
python -m unittest discover -s tests -v
```

Check the behavioral fixture inventory without running an agent:

```shell
python scripts/evaluate_scenarios.py check
```

Preview a generated Claude Code distribution without writing it:

```shell
python scripts/install_skills.py --platform claude-code --destination path/to/project/.claude/skills --all --dry-run
```

Check the tracked marketplace package against the canonical skills and then verify its embedded file hashes:

```shell
python scripts/package_plugins.py check
python scripts/package_plugins.py verify
```

These commands are intentionally shell-neutral. The `Validate skills` GitHub Actions workflow runs the automated test suite, required-catalog validation, generated-distribution reconstruction, and embedded package-inventory verification for pull requests to `main`, pushes to `main`, and manual dispatches. Its minimal compatibility matrix uses Ubuntu with Python 3.11 (the minimum supported runtime) and Windows with Python 3.13. This gives the installer and path-safety code both POSIX and Windows coverage without multiplying every supported Python and operating-system combination. macOS remains a manual compatibility target.

The workflow grants the token read-only repository-content access, uses no secrets, and pins official actions to the full commit SHA corresponding to `actions/checkout@v7.0.1` and `actions/setup-python@v7.1.0`. Its checkout does not persist credentials. Because the repository now has implemented skills, CI uses `--require-skills` and fails if the canonical catalog is absent or empty.

## Results and exit codes

- Exit code `0` means no validation errors were found. Warnings may still be present.
- Exit code `1` means the catalog or a skill has validation errors.
- Exit code `2` means command usage or the local Python environment is invalid.

Messages include a severity and category. `ERROR [specification]` identifies a violated Agent Skills requirement. `ERROR [structure]` identifies an unusable catalog, file, or local reference. `ERROR [security]` identifies an unsafe path. `WARNING [project-convention]` identifies a portable skill that does not follow an additional repository convention.

The validator still accepts an absent or empty `.agents/skills/` by default for isolated foundation and test scenarios, reporting **zero skills validated** rather than a passing skill catalog. Repository CI uses `--require-skills` because the canonical catalog must contain implemented skills.

## Quality levels

### Structural conformance

The validator automatically checks:

- presence and UTF-8 readability of `SKILL.md`;
- YAML frontmatter delimiters, syntax, mapping shape, and duplicate keys;
- required and supported fields, value types, and documented length limits;
- specification name rules and correspondence with the parent directory;
- duplicate skill names within the validated catalog;
- non-empty Markdown instructions;
- local Markdown links and reference-style link definitions;
- missing local targets, non-portable separators, absolute paths, traversal outside the skill, and unsupported URI schemes;
- symlinks anywhere in a skill or as catalog entries, because the installer intentionally refuses to distribute them;
- unexpected files at the catalog root, except the installer's managed manifest in a generated distribution.

The automated suite also applies these checks to the real canonical catalog, asserts the preserved ten-skill inventory, requires the stricter ASCII kebab-case project convention without warnings, and verifies that no independent `.github/skills/` tree has been introduced. Together these checks cover the format and project location shared by Codex and Copilot. They do not launch either agent host.

Installer tests use temporary directories to exercise complete and single-skill distributions, nested supporting files, dry runs, repeat installation, managed updates, safe removal, path traversal rejection, malformed and duplicate-key manifests, reserved names, and conflicts with unmanaged or locally modified files. The tests assert that invalid preflight states do not modify the destination. They do not require or launch Claude Code.

Plugin packaging tests generate isolated marketplace roots, compare reproducible outputs, preserve binary and nested skill resources, validate the three marketplace manifests plus the portable and Claude plugin manifests, resolve and confine every repository-relative source, verify the embedded SHA-256 inventory, detect canonical drift and manual derived edits, reject symlinks, and assert that the tracked package contains exactly the ten canonical skills. They do not install or launch any agent client.

Link-shaped text inside fenced or inline Markdown code is treated as an example rather than a reference. HTTP, HTTPS, and email targets are deliberately not fetched. The skill validator does not interpret fragments; a separate documentation regression test verifies local Markdown file targets and heading fragments. External URL availability remains outside the offline suite.

### Internal conventions

The validator emits warnings for deterministic conventions that do not determine specification compliance, currently the English ASCII kebab-case naming rule. More subjective conventions in [Skill authoring](skill-authoring.md)—single responsibility, useful use/non-use boundaries, concise instructions, appropriate examples, and clear failure guidance—require review rather than unreliable keyword checks.

### Behavioral quality

Structural validation does not demonstrate that an agent discovers or activates a skill correctly, follows its workflow, produces a good response, detects real defects, or avoids invented results. Representative scenarios under `tests/fixtures/<skill>/scenarios.md` document inputs and expected behavior for later controlled evaluation. `tests/fixtures/coverage.json` maps every skill to expected use, non-activation, insufficient-information, operational-failure-or-limitation, and applicable destructive-operation scenarios.

The automated suite checks fixture syntax, contiguous identifiers, catalog-to-fixture inventory, coverage references, and evaluation-record completeness. It does **not** send fixture inputs to an agent or score an answer. A passing fixture test therefore means only that the evaluation material is internally consistent. Passing compatibility and installer checks establish structural compatibility and safe distribution; they are not verified behavioral execution on Codex, Copilot, or Claude Code.

No real-agent result is generated by CI, and no completed agent-evaluation record is currently part of the repository. Scenarios remain pending until an evaluator performs and records a controlled run.

### Reproducible manual behavioral evaluation

1. Choose a scenario and record the exact agent platform and version. Use a disposable repository or isolated environment whenever the input involves files, Git, SQL, deployment, or another mutable resource.
2. Create a pending record. The command uses exclusive creation and refuses to overwrite an existing result:

   ```shell
   python scripts/evaluate_scenarios.py prepare --skill code-review --scenario 1 --platform openai-codex --agent-version VERSION --output tests/evaluations/records/DATE-code-review-1.json
   ```

3. Submit the record's `scenario.input` verbatim, together with only the synthetic context required by that fixture. Do not use production credentials, paid services, live infrastructure, or network access. Do not authorize destructive actions merely because a scenario discusses them.
4. In the JSON record, change `status` to `completed`; preserve the complete observed output; record start and completion timestamps, relevant environment details, platform, and exact agent version; then mark each criterion `met`, `not_met`, or `not_applicable` with concrete evidence. Record unavailable capabilities or deviations under `limitations`.
5. Validate completed records and rerun the offline suite:

   ```shell
   python scripts/evaluate_scenarios.py check --records tests/evaluations/records
   python -m unittest discover -s tests -v
   ```

The scenario hash makes a record stale when its source fixture changes. Keep a stale run for audit only if its result is clearly separated from current records; create a new run before drawing a current conclusion. Never convert a pending template into a claimed result without the observed agent output and criterion evidence.

## YAML and the reference validator

The Agent Skills specification recommends `skills-ref`. The official reference implementation validates frontmatter and naming, but its own README describes it as demonstration software rather than production software. The similarly named PyPI distribution is not controlled by the official repository maintainers, so this project does not depend on it.

This validator follows the published constraints and uses PyYAML's safe loader for YAML syntax instead of implementing a partial parser. Its additional catalog, reference, path-safety, empty-state, and project-convention checks are outside the current `skills-ref` scope. Future CI may run a pinned official release as an independent compatibility check after its distribution and versioning strategy is evaluated.

## Adding test scenarios

Add a focused `unittest` method to `tests/test_validate_skills.py`. Create all catalog content under `tempfile.TemporaryDirectory`, use the local helper for valid baseline skills, change only the condition under test, and assert both severity/category and actionable message where relevant. CLI behavior should be tested through `sys.executable` so it works on Windows, macOS, and Linux.

For behavioral fixtures, add or update a numbered section in `tests/fixtures/<skill>/scenarios.md` and keep its references in `tests/fixtures/coverage.json` accurate. Each scenario needs a non-empty `Input` field and at least one expectation or evaluation field. Do not add a completed evaluation record unless an agent was actually run and the required evidence was captured.

Never place deliberately invalid fixtures in `.agents/skills/`. Tests must not use the network, execute skill scripts, depend on test order, or retain temporary files.
