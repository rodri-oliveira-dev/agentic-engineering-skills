from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import supply_chain_evidence as evidence  # noqa: E402


class SupplyChainEvidenceTests(unittest.TestCase):
    def test_repository_dependencies_are_pinned_and_actions_use_full_shas(self) -> None:
        self.assertTrue(evidence.pinned_requirements())
        self.assertTrue(evidence.action_inventory())

    def test_rejects_unpinned_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "requirements.txt").write_text("PyYAML>=6\n", encoding="utf-8")
            with patch.object(evidence, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "unpinned"):
                    evidence.pinned_requirements()

    def test_rejects_unpinned_workflow_action(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflows = root / ".github/workflows"
            workflows.mkdir(parents=True)
            (workflows / "ci.yml").write_text("steps:\n  - uses: actions/checkout@main\n", encoding="utf-8")
            with patch.object(evidence, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "Unpinned"):
                    evidence.action_inventory()

    def test_release_archive_is_reproducible_and_checksum_is_correct(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / "plugins/agentic-engineering"
            (plugin / "skills/example").mkdir(parents=True)
            (plugin / "plugin.json").write_text('{"version":"1.0.1"}', encoding="utf-8")
            (plugin / "skills/example/SKILL.md").write_text("skill contents", encoding="utf-8")
            first, second = root / "first.zip", root / "second.zip"
            with patch.object(evidence, "ROOT", root):
                evidence.release_archive(Namespace(tag="1.0.1", output=str(first)))
                evidence.release_archive(Namespace(tag="1.0.1", output=str(second)))
                with self.assertRaisesRegex(ValueError, "does not match"):
                    evidence.release_archive(Namespace(tag="1.0.2", output=str(root / "bad.zip")))
            self.assertEqual(first.read_bytes(), second.read_bytes())
            self.assertEqual(
                first.with_name("first.zip.sha256").read_text(encoding="ascii"),
                f"{hashlib.sha256(first.read_bytes()).hexdigest()}  first.zip\n",
            )

    def test_rejects_symlinked_release_content(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plugin = root / "plugins/agentic-engineering"
            plugin.mkdir(parents=True)
            (plugin / "plugin.json").write_text('{"version":"1.0.1"}', encoding="utf-8")
            try:
                (plugin / "leak").symlink_to(root / "missing")
            except (NotImplementedError, OSError):
                self.skipTest("Filesystem does not allow symlinks")
            with patch.object(evidence, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "Unsafe"):
                    evidence.release_archive(Namespace(tag="1.0.1", output=str(root / "bad.zip")))


if __name__ == "__main__":
    unittest.main()
