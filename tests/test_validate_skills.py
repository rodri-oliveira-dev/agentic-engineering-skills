from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIRECTORY = REPOSITORY_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from skill_validation import validate_catalog  # noqa: E402


def write_skill(
    catalog: Path,
    directory_name: str,
    *,
    name: str | None = None,
    description: str = "Perform a focused task. Use when that task is requested.",
    body: str = "# Instructions\n\nFollow the documented workflow.",
    frontmatter: str | None = None,
) -> Path:
    skill_directory = catalog / directory_name
    skill_directory.mkdir(parents=True)
    if frontmatter is None:
        frontmatter = f"name: {name or directory_name}\ndescription: {description}"
    (skill_directory / "SKILL.md").write_text(
        f"---\n{frontmatter}\n---\n\n{body}\n", encoding="utf-8"
    )
    return skill_directory


class ValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.catalog = Path(self.temporary_directory.name) / ".agents" / "skills"
        self.catalog.mkdir(parents=True)

    def messages(self, report) -> str:
        return "\n".join(issue.message for issue in report.issues)

    def test_structurally_valid_skill(self) -> None:
        skill = write_skill(
            self.catalog,
            "valid-skill",
            body="# Instructions\n\nSee [details](references/details.md).",
        )
        references = skill / "references"
        references.mkdir()
        (references / "details.md").write_text("# Details\n", encoding="utf-8")

        report = validate_catalog(self.catalog)

        self.assertEqual([], report.errors)
        self.assertEqual(1, len(report.skills))

    def test_invalid_yaml(self) -> None:
        write_skill(
            self.catalog,
            "bad-yaml",
            frontmatter="name: bad-yaml\ndescription: [unterminated",
        )

        report = validate_catalog(self.catalog)

        self.assertIn("invalid YAML", self.messages(report))

    def test_duplicate_yaml_key_is_invalid(self) -> None:
        write_skill(
            self.catalog,
            "duplicate-key",
            frontmatter="name: duplicate-key\nname: duplicate-key\ndescription: Use for a task.",
        )

        report = validate_catalog(self.catalog)

        self.assertIn("duplicate key", self.messages(report))

    def test_missing_required_metadata(self) -> None:
        write_skill(self.catalog, "missing-description", frontmatter="name: missing-description")

        report = validate_catalog(self.catalog)

        self.assertIn("missing required field 'description'", self.messages(report))

    def test_invalid_name_pattern(self) -> None:
        write_skill(self.catalog, "Bad_Name", name="Bad_Name")

        report = validate_catalog(self.catalog)

        messages = self.messages(report)
        self.assertIn("must be lowercase", messages)
        self.assertIn("may contain only", messages)

    def test_name_must_match_directory(self) -> None:
        write_skill(self.catalog, "directory-name", name="different-name")

        report = validate_catalog(self.catalog)

        self.assertIn("must match parent directory", self.messages(report))

    def test_directory_without_skill_md(self) -> None:
        (self.catalog / "missing-file").mkdir()

        report = validate_catalog(self.catalog)

        self.assertIn("missing required file SKILL.md", self.messages(report))

    def test_duplicate_names(self) -> None:
        write_skill(self.catalog, "first-directory", name="shared-name")
        write_skill(self.catalog, "second-directory", name="shared-name")

        report = validate_catalog(self.catalog)

        duplicate_errors = [
            issue for issue in report.errors if "duplicate skill name 'shared-name'" in issue.message
        ]
        self.assertEqual(2, len(duplicate_errors))

    def test_broken_local_reference(self) -> None:
        write_skill(
            self.catalog,
            "broken-reference",
            body="# Instructions\n\nRead [missing](references/missing.md).",
        )

        report = validate_catalog(self.catalog)

        self.assertIn("local link target does not exist", self.messages(report))

    def test_reference_cannot_escape_skill_directory(self) -> None:
        write_skill(
            self.catalog,
            "escape-reference",
            body="# Instructions\n\nRead [outside](../../../outside.md).",
        )

        report = validate_catalog(self.catalog)

        security_errors = [issue for issue in report.errors if issue.category == "security"]
        self.assertTrue(security_errors)
        self.assertIn("escapes the skill directory", self.messages(report))

    def test_empty_catalog_is_allowed_by_default(self) -> None:
        report = validate_catalog(self.catalog)

        self.assertTrue(report.empty_catalog)
        self.assertEqual([], report.errors)
        self.assertEqual([], report.skills)

    def test_missing_catalog_is_an_allowed_empty_catalog(self) -> None:
        report = validate_catalog(self.catalog / "not-created")

        self.assertTrue(report.empty_catalog)
        self.assertEqual([], report.errors)

    def test_empty_catalog_can_be_required(self) -> None:
        report = validate_catalog(self.catalog, require_skills=True)

        self.assertTrue(report.errors)
        self.assertIn("--require-skills", self.messages(report))

    def test_multiple_valid_skills(self) -> None:
        write_skill(self.catalog, "first-skill")
        write_skill(self.catalog, "second-skill")

        report = validate_catalog(self.catalog)

        self.assertEqual(2, len(report.skills))
        self.assertEqual([], report.errors)

    def test_specific_skill_selection(self) -> None:
        write_skill(self.catalog, "first-skill")
        write_skill(self.catalog, "second-skill")

        report = validate_catalog(self.catalog, selected_skill="second-skill")

        self.assertEqual(["second-skill"], [skill.directory.name for skill in report.skills])

    def test_specific_skill_rejects_path_traversal(self) -> None:
        report = validate_catalog(self.catalog, selected_skill="../outside")

        self.assertTrue(report.errors)
        self.assertEqual("security", report.errors[0].category)

    def test_skill_scripts_are_not_executed(self) -> None:
        skill = write_skill(self.catalog, "safe-validation")
        scripts = skill / "scripts"
        scripts.mkdir()
        marker = skill / "executed.txt"
        (scripts / "danger.py").write_text(
            f"from pathlib import Path\nPath({str(marker)!r}).write_text('executed')\n",
            encoding="utf-8",
        )

        report = validate_catalog(self.catalog)

        self.assertEqual([], report.errors)
        self.assertFalse(marker.exists())

    def test_unicode_spec_name_produces_project_warning_only(self) -> None:
        write_skill(self.catalog, "revisão")

        report = validate_catalog(self.catalog)

        self.assertEqual([], report.errors)
        self.assertTrue(any(issue.category == "project-convention" for issue in report.warnings))


class CliTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.catalog = Path(self.temporary_directory.name) / "skills"
        self.catalog.mkdir()
        self.command = [
            sys.executable,
            str(REPOSITORY_ROOT / "scripts" / "validate_skills.py"),
            "--root",
            str(self.catalog),
        ]

    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [*self.command, *arguments],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

    def test_cli_returns_zero_for_valid_catalog(self) -> None:
        write_skill(self.catalog, "valid-skill")

        result = self.run_cli()

        self.assertEqual(0, result.returncode, result.stderr)
        self.assertIn("Checked 1 skill(s): 0 error(s)", result.stdout)

    def test_cli_returns_nonzero_for_invalid_catalog(self) -> None:
        write_skill(self.catalog, "invalid-skill", frontmatter="name: invalid-skill")

        result = self.run_cli()

        self.assertEqual(1, result.returncode)
        self.assertIn("ERROR [specification]", result.stderr)

    def test_cli_reports_empty_without_claiming_validation(self) -> None:
        result = self.run_cli()

        self.assertEqual(0, result.returncode)
        self.assertIn("No skills were validated", result.stdout)

    def test_cli_returns_nonzero_when_skills_are_required(self) -> None:
        result = self.run_cli("--require-skills")

        self.assertEqual(1, result.returncode)
        self.assertIn("catalog is empty", result.stderr)


if __name__ == "__main__":
    unittest.main()
