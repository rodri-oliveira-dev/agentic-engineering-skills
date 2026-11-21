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

These commands are intentionally shell-neutral. The `Validate skills` GitHub Actions workflow runs the automated test suite and required-catalog validation on Ubuntu with Python 3.11 for pull requests to `main`, pushes to `main`, and manual dispatches.

The workflow grants the token read-only repository-content access, uses no secrets, and pins official actions to the full commit SHA corresponding to `actions/checkout@v7.0.0` and `actions/setup-python@v7.0.0`. Its checkout does not persist credentials. Because the repository now has implemented skills, CI uses `--require-skills` and fails if the canonical catalog is absent or empty.

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
- missing local targets, non-portable separators, absolute paths, traversal outside the skill, and escaping symlinks.

Link-shaped text inside fenced or inline Markdown code is treated as an example rather than a reference. HTTP, HTTPS, and email targets are deliberately not fetched. URL availability and Markdown fragments are not validated, so execution remains deterministic and offline.

### Internal conventions

The validator emits warnings for deterministic conventions that do not determine specification compliance, currently the English ASCII kebab-case naming rule. More subjective conventions in [Skill authoring](skill-authoring.md)—single responsibility, useful use/non-use boundaries, concise instructions, appropriate examples, and clear failure guidance—require review rather than unreliable keyword checks.

### Behavioral quality

Structural validation does not demonstrate that an agent activates a skill correctly, follows its workflow, produces a good response, detects real defects, or avoids invented results. Representative scenarios under `tests/fixtures/<skill>/scenarios.md` document inputs and expected behavior for later controlled evaluation; they are not executed by `unittest` or CI and must not be reported as passing behavioral tests. Those properties require human review and controlled tests using supported agents.

## YAML and the reference validator

The Agent Skills specification recommends `skills-ref`. The official reference implementation validates frontmatter and naming, but its own README describes it as demonstration software rather than production software. The similarly named PyPI distribution is not controlled by the official repository maintainers, so this project does not depend on it.

This validator follows the published constraints and uses PyYAML's safe loader for YAML syntax instead of implementing a partial parser. Its additional catalog, reference, path-safety, empty-state, and project-convention checks are outside the current `skills-ref` scope. Future CI may run a pinned official release as an independent compatibility check after its distribution and versioning strategy is evaluated.

## Adding test scenarios

Add a focused `unittest` method to `tests/test_validate_skills.py`. Create all catalog content under `tempfile.TemporaryDirectory`, use the local helper for valid baseline skills, change only the condition under test, and assert both severity/category and actionable message where relevant. CLI behavior should be tested through `sys.executable` so it works on Windows, macOS, and Linux.

Never place deliberately invalid fixtures in `.agents/skills/`. Tests must not use the network, execute skill scripts, depend on test order, or retain temporary files.
