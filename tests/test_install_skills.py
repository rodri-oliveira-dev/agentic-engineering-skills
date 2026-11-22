from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIRECTORY = REPOSITORY_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from install_skills import (  # noqa: E402
    DEFAULT_CATALOG,
    MANIFEST_NAME,
    InstallError,
    install_skills,
    uninstall_skills,
)
from skill_validation import validate_catalog  # noqa: E402


def write_skill(catalog: Path, name: str, files: dict[str, str] | None = None) -> Path:
    skill = catalog / name
    skill.mkdir(parents=True)
    content = {
        "SKILL.md": (
            f"---\nname: {name}\ndescription: Test {name}. "
            f"Use for tests.\n---\n\n# {name}\n"
        ),
        **(files or {}),
    }
    for relative, text in content.items():
        target = skill / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return skill


class InstallerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.catalog = self.root / ".agents" / "skills"
        self.destination = self.root / "project" / ".claude" / "skills"
        self.catalog.mkdir(parents=True)

    def install(self, *, skill: str | None = None, dry_run: bool = False):
        return install_skills(
            catalog=self.catalog,
            destination=self.destination,
            platform="claude-code",
            selected_skill=skill,
            dry_run=dry_run,
        )

    def manifest(self) -> dict:
        return json.loads((self.destination / MANIFEST_NAME).read_text(encoding="utf-8"))

    def test_installs_all_skills_and_supporting_content(self) -> None:
        write_skill(
            self.catalog,
            "code-review",
            {
                "references/checks.md": "# Checks\n",
                "scripts/helper.py": "print('helper')\n",
                "assets/template.txt": "template\n",
            },
        )
        write_skill(self.catalog, "testing")

        result = self.install()

        self.assertTrue(result.changed)
        self.assertEqual(
            "# Checks\n",
            (self.destination / "code-review/references/checks.md").read_text(),
        )
        self.assertEqual(
            "print('helper')\n",
            (self.destination / "code-review/scripts/helper.py").read_text(),
        )
        self.assertEqual(
            "template\n",
            (self.destination / "code-review/assets/template.txt").read_text(),
        )
        self.assertEqual({"code-review", "testing"}, set(self.manifest()["skills"]))

    def test_installs_only_selected_skill(self) -> None:
        write_skill(self.catalog, "code-review")
        write_skill(self.catalog, "testing")

        self.install(skill="testing")

        self.assertFalse((self.destination / "code-review").exists())
        self.assertTrue((self.destination / "testing/SKILL.md").is_file())
        self.assertEqual({"testing"}, set(self.manifest()["skills"]))

    def test_dry_run_does_not_create_destination(self) -> None:
        write_skill(self.catalog, "testing")

        result = self.install(dry_run=True)

        self.assertTrue(result.changed)
        self.assertFalse(self.destination.exists())

    def test_repeated_install_is_idempotent(self) -> None:
        write_skill(self.catalog, "testing", {"references/details.md": "details\n"})
        first = self.install()
        skill_mtime = (self.destination / "testing/SKILL.md").stat().st_mtime_ns
        manifest_mtime = (self.destination / MANIFEST_NAME).stat().st_mtime_ns

        second = self.install()

        self.assertTrue(first.changed)
        self.assertFalse(second.changed)
        self.assertEqual(skill_mtime, (self.destination / "testing/SKILL.md").stat().st_mtime_ns)
        self.assertEqual(manifest_mtime, (self.destination / MANIFEST_NAME).stat().st_mtime_ns)

    def test_updates_an_unchanged_managed_file(self) -> None:
        skill = write_skill(self.catalog, "testing")
        self.install()
        (skill / "SKILL.md").write_text("updated canonical content\n", encoding="utf-8")

        result = self.install()

        self.assertTrue(result.changed)
        self.assertEqual(
            "updated canonical content\n",
            (self.destination / "testing/SKILL.md").read_text(encoding="utf-8"),
        )

    def test_refuses_to_replace_unmanaged_skill_directory(self) -> None:
        write_skill(self.catalog, "testing")
        unmanaged = self.destination / "testing"
        unmanaged.mkdir(parents=True)
        original = unmanaged / "notes.txt"
        original.write_text("keep me\n", encoding="utf-8")

        with self.assertRaisesRegex(InstallError, "unmanaged skill directory"):
            self.install()

        self.assertEqual("keep me\n", original.read_text(encoding="utf-8"))
        self.assertFalse((self.destination / MANIFEST_NAME).exists())

    def test_refuses_to_overwrite_a_modified_managed_file(self) -> None:
        write_skill(self.catalog, "testing")
        self.install()
        installed = self.destination / "testing/SKILL.md"
        installed.write_text("local edit\n", encoding="utf-8")
        (self.catalog / "testing/SKILL.md").write_text("canonical update\n", encoding="utf-8")

        with self.assertRaisesRegex(InstallError, "modified locally"):
            self.install()

        self.assertEqual("local edit\n", installed.read_text(encoding="utf-8"))

    def test_conflict_preflight_prevents_partial_multi_skill_install(self) -> None:
        write_skill(self.catalog, "code-review")
        write_skill(self.catalog, "testing")
        unmanaged = self.destination / "testing"
        unmanaged.mkdir(parents=True)

        with self.assertRaises(InstallError):
            self.install()

        self.assertFalse((self.destination / "code-review").exists())
        self.assertFalse((self.destination / MANIFEST_NAME).exists())

    def test_rejects_skill_name_path_traversal(self) -> None:
        write_skill(self.catalog, "testing")

        with self.assertRaisesRegex(InstallError, "skill name must"):
            self.install(skill="../testing")

        self.assertFalse(self.destination.exists())

    def test_rejects_a_claude_code_reserved_skill_name(self) -> None:
        write_skill(self.catalog, "synced")

        with self.assertRaisesRegex(InstallError, "reserved by Claude Code"):
            self.install()

        self.assertFalse(self.destination.exists())

    def test_parent_file_conflict_is_detected_before_any_write(self) -> None:
        write_skill(self.catalog, "code-review")
        write_skill(self.catalog, "testing", {"references/details.md": "details\n"})
        self.destination.mkdir(parents=True)
        manifest = {
            "schema_version": 1,
            "managed_by": "agentic-engineering-skills",
            "platform": "claude-code",
            "skills": {"testing": {"files": {}}},
        }
        (self.destination / MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")
        target_skill = self.destination / "testing"
        target_skill.mkdir()
        (target_skill / "references").write_text("unmanaged parent\n", encoding="utf-8")

        with self.assertRaisesRegex(InstallError, "parent is not a regular directory"):
            self.install()

        self.assertFalse((self.destination / "code-review").exists())
        self.assertEqual("unmanaged parent\n", (target_skill / "references").read_text())

    def test_rejects_manifest_path_traversal(self) -> None:
        write_skill(self.catalog, "testing")
        self.destination.mkdir(parents=True)
        outside = self.root / "outside.txt"
        outside.write_text("keep me\n", encoding="utf-8")
        manifest = {
            "schema_version": 1,
            "managed_by": "agentic-engineering-skills",
            "platform": "claude-code",
            "skills": {"testing": {"files": {"../../../outside.txt": "0" * 64}}},
        }
        (self.destination / MANIFEST_NAME).write_text(json.dumps(manifest), encoding="utf-8")

        with self.assertRaisesRegex(InstallError, "unsafe path"):
            self.install()

        self.assertEqual("keep me\n", outside.read_text(encoding="utf-8"))

    def test_refuses_broken_symlink_at_an_unmanaged_skill_path(self) -> None:
        write_skill(self.catalog, "testing")
        self.destination.mkdir(parents=True)
        link = self.destination / "testing"
        try:
            link.symlink_to(self.destination / "missing-target", target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlinks are unavailable: {exc}")

        with self.assertRaisesRegex(InstallError, "unmanaged skill directory"):
            self.install()

        self.assertTrue(link.is_symlink())

    def test_uninstalls_only_selected_intact_skill(self) -> None:
        write_skill(self.catalog, "code-review")
        write_skill(self.catalog, "testing")
        self.install()

        result = uninstall_skills(
            destination=self.destination,
            platform="claude-code",
            selected_skill="testing",
        )

        self.assertTrue(result.changed)
        self.assertFalse((self.destination / "testing").exists())
        self.assertTrue((self.destination / "code-review/SKILL.md").is_file())
        self.assertEqual({"code-review"}, set(self.manifest()["skills"]))

    def test_uninstall_refuses_modified_or_unmanaged_content(self) -> None:
        write_skill(self.catalog, "testing")
        self.install()
        (self.destination / "testing/notes.txt").write_text("unmanaged\n", encoding="utf-8")

        with self.assertRaisesRegex(InstallError, "unmanaged file"):
            uninstall_skills(
                destination=self.destination,
                platform="claude-code",
                selected_skill="testing",
            )

        self.assertTrue((self.destination / "testing/SKILL.md").is_file())

    def test_uninstall_refuses_a_modified_managed_file(self) -> None:
        write_skill(self.catalog, "testing")
        self.install()
        installed = self.destination / "testing/SKILL.md"
        installed.write_text("local edit\n", encoding="utf-8")

        with self.assertRaisesRegex(InstallError, "modified locally"):
            uninstall_skills(
                destination=self.destination,
                platform="claude-code",
                selected_skill="testing",
            )

        self.assertEqual("local edit\n", installed.read_text(encoding="utf-8"))

    def test_uninstall_dry_run_and_reexecution_are_safe(self) -> None:
        write_skill(self.catalog, "testing")
        self.install()

        preview = uninstall_skills(
            destination=self.destination,
            platform="claude-code",
            selected_skill=None,
            dry_run=True,
        )
        self.assertTrue(preview.changed)
        self.assertTrue((self.destination / "testing/SKILL.md").is_file())

        removed = uninstall_skills(
            destination=self.destination,
            platform="claude-code",
            selected_skill=None,
        )
        repeated = uninstall_skills(
            destination=self.destination,
            platform="claude-code",
            selected_skill=None,
        )

        self.assertTrue(removed.changed)
        self.assertFalse(repeated.changed)
        self.assertFalse((self.destination / MANIFEST_NAME).exists())

    def test_removes_only_unchanged_obsolete_managed_files(self) -> None:
        skill = write_skill(self.catalog, "testing", {"references/old.md": "old\n"})
        self.install()
        (skill / "references/old.md").unlink()

        result = self.install()

        self.assertTrue(result.changed)
        self.assertFalse((self.destination / "testing/references/old.md").exists())

    def test_refuses_to_remove_modified_obsolete_managed_file(self) -> None:
        skill = write_skill(self.catalog, "testing", {"references/old.md": "old\n"})
        self.install()
        installed = self.destination / "testing/references/old.md"
        installed.write_text("local edit\n", encoding="utf-8")
        (skill / "references/old.md").unlink()

        with self.assertRaisesRegex(InstallError, "obsolete managed file was modified"):
            self.install()

        self.assertEqual("local edit\n", installed.read_text(encoding="utf-8"))


class InstallerCliTests(unittest.TestCase):
    def test_real_catalog_can_be_distributed_and_reinstalled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / ".claude" / "skills"
            canonical_before = {
                path.relative_to(DEFAULT_CATALOG): path.read_bytes()
                for path in DEFAULT_CATALOG.rglob("*")
                if path.is_file()
            }

            first = install_skills(
                catalog=DEFAULT_CATALOG,
                destination=destination,
                platform="claude-code",
                selected_skill=None,
            )
            second = install_skills(
                catalog=DEFAULT_CATALOG,
                destination=destination,
                platform="claude-code",
                selected_skill=None,
            )
            distributed_report = validate_catalog(destination, require_skills=True)
            canonical_after = {
                path.relative_to(DEFAULT_CATALOG): path.read_bytes()
                for path in DEFAULT_CATALOG.rglob("*")
                if path.is_file()
            }

            self.assertTrue(first.changed)
            self.assertFalse(second.changed)
            self.assertEqual([], distributed_report.errors)
            self.assertEqual([], distributed_report.warnings)
            self.assertEqual(canonical_before, canonical_after)
            for relative, content in canonical_before.items():
                self.assertEqual(content, (destination / relative).read_bytes())
            manifest = json.loads((destination / MANIFEST_NAME).read_text(encoding="utf-8"))
            self.assertEqual(10, len(manifest["skills"]))

    def test_cli_dry_run_uses_no_claude_installation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            destination = Path(temporary_directory) / ".claude" / "skills"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIRECTORY / "install_skills.py"),
                    "--platform",
                    "claude-code",
                    "--destination",
                    str(destination),
                    "--skill",
                    "testing",
                    "--dry-run",
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(0, result.returncode, result.stderr)
            self.assertIn("Would create: testing/SKILL.md", result.stdout)
            self.assertFalse(destination.exists())


if __name__ == "__main__":
    unittest.main()
