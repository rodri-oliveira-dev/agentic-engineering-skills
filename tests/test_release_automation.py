from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import release_automation as releases  # noqa: E402


class ReleaseAutomationTests(unittest.TestCase):
    def test_semver_accepts_only_canonical_stable_versions(self) -> None:
        self.assertEqual((1, 0, 1), releases.version_tuple("1.0.1"))
        for invalid in ("v1.0.1", "01.0.1", "1.02.3", "1.0.0-rc.1", "1.0", "../x", ""):
            with self.subTest(invalid=invalid):
                with self.assertRaises(ValueError):
                    releases.version_tuple(invalid)

    def test_notes_must_be_nonempty_and_safe_for_workflows(self) -> None:
        for invalid in ("", "   ", "x\x00y", "x\x1by", "x" * 12001):
            with self.subTest(invalid=repr(invalid)[:30]):
                with self.assertRaises(ValueError):
                    releases.validate_notes(invalid)
        self.assertEqual("First change\nSecond change", releases.validate_notes("First change\r\nSecond change"))

    def _fixture_root(self, directory: str) -> Path:
        root = Path(directory)
        (root / "scripts").mkdir()
        (root / "scripts/package_plugins.py").write_text(
            'PLUGIN_VERSION = "1.0.0"\n', encoding="utf-8"
        )
        return root

    def test_prepare_writes_only_next_version_and_proposed_notes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            with patch.object(releases.subprocess, "run") as run:
                releases.prepare("1.0.1", "Fix validations", root)
                run.assert_called_once()
                self.assertTrue(run.call_args.kwargs["check"])
            self.assertEqual("1.0.1", releases.get_current_version(root))
            path = releases.notes_path(root, "1.0.1")
            self.assertTrue(path.is_file())
            self.assertIn("Fix validations", path.read_text(encoding="utf-8"))
            duplicate = releases.notes_path(root, "1.0.2")
            duplicate.write_text("Prior draft", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "already exist"):
                releases.prepare("1.0.2", "Same", root)

    def test_preparation_rejects_downgrade_before_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            with patch.object(releases.subprocess, "run") as run:
                with self.assertRaisesRegex(ValueError, "greater"):
                    releases.prepare("1.0.0", "Not newer", root)
                with self.assertRaises(ValueError):
                    releases.prepare("v1.0.1", "Invalid", root)
                run.assert_not_called()
            self.assertEqual("1.0.0", releases.get_current_version(root))

    def test_validate_fails_closed_on_inconsistent_manifests_and_notes(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = self._fixture_root(directory)
            version = "1.0.0"
            objects = {
                "plugins/agentic-engineering/plugin.json": {"version": version},
                ".agents/plugins/marketplace.json": {"plugins": [{"version": version}]},
                ".github/plugin/marketplace.json": {
                    "metadata": {"version": version}, "plugins": [{"version": version}]
                },
                ".claude-plugin/marketplace.json": {"plugins": [{"version": version}]},
            }
            for relative, payload in objects.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(payload), encoding="utf-8")
            notes = releases.notes_path(root, version)
            notes.parent.mkdir(parents=True, exist_ok=True)
            notes.write_text("# Release 1.0.0\n\nReal changes\n", encoding="utf-8")
            releases.validate(version, root)
            payload = objects[".github/plugin/marketplace.json"]
            payload["metadata"]["version"] = "0.9.0"
            (root / ".github/plugin/marketplace.json").write_text(
                json.dumps(payload), encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "version mismatch"):
                releases.validate(version, root)


if __name__ == "__main__":
    unittest.main()
