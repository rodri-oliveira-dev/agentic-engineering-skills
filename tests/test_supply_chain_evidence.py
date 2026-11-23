from __future__ import annotations

import hashlib
import sys
import tempfile
import unittest
import yaml
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

    def test_all_supported_workflow_extensions_are_scanned(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            workflows = root / ".github/workflows"
            workflows.mkdir(parents=True)
            sha = "a" * 40
            (workflows / "one.yml").write_text(
                f"steps:\n  - uses: actions/checkout@{sha}\n", encoding="utf-8"
            )
            (workflows / "two.yaml").write_text(
                f"steps:\n  - uses: actions/setup-python@{sha}\n", encoding="utf-8"
            )
            with patch.object(evidence, "ROOT", root):
                self.assertEqual(2, len(evidence.action_inventory()))
            (workflows / "two.yaml").write_text(
                "steps:\n  - uses: actions/setup-python@main\n", encoding="utf-8"
            )
            with patch.object(evidence, "ROOT", root):
                with self.assertRaisesRegex(ValueError, "Unpinned"):
                    evidence.action_inventory()

    def test_release_workflow_is_manually_gated_and_uses_read_only_build(self) -> None:
        audit_file = evidence.ROOT / ".github/workflows/security-audit.yml"
        release_file = evidence.ROOT / ".github/workflows/publish-release.yml"
        audit = yaml.safe_load(audit_file.read_text(encoding="utf-8"))
        workflow = yaml.safe_load(release_file.read_text(encoding="utf-8"))
        events = workflow.get("on", workflow.get(True))
        self.assertIn("workflow_dispatch", events)
        self.assertNotIn("release", events)
        self.assertIn("workflow_call:", audit_file.read_text(encoding="utf-8"))
        self.assertEqual({"contents": "read"}, audit["permissions"])
        self.assertEqual({"contents": "read"}, workflow["permissions"])

        jobs = workflow["jobs"]
        self.assertEqual({"contents": "read"}, jobs["preflight"]["permissions"])
        self.assertEqual({"contents": "read"}, jobs["audit"]["permissions"])
        self.assertEqual({"contents": "read"}, jobs["release-package"]["permissions"])
        self.assertEqual("./.github/workflows/security-audit.yml", jobs["audit"]["uses"])
        self.assertEqual("audit", jobs["release-package"]["needs"])
        self.assertEqual("release-package", jobs["publish"]["needs"])
        self.assertEqual({"name": "release"}, jobs["publish"]["environment"])
        self.assertEqual(
            {"contents": "write", "id-token": "write", "attestations": "write"},
            jobs["publish"]["permissions"],
        )
        self.assertFalse(
            any("actions/checkout@" in step.get("uses", "") for step in jobs["publish"]["steps"])
        )
        self.assertFalse(
            any("python " in step.get("run", "") for step in jobs["publish"]["steps"])
        )
        self.assertTrue(
            any("download-artifact@" in step.get("uses", "") for step in jobs["publish"]["steps"])
        )
        self.assertEqual(
            "${{ github.sha }}",
            jobs["release-package"]["steps"][0]["with"]["ref"],
        )
        names = [step["name"] for step in jobs["publish"]["steps"]]
        self.assertLess(
            names.index("Verify cryptographic provenance before release creation"),
            names.index("Create draft release with verified assets"),
        )
        self.assertLess(
            names.index("Download draft assets and compare published bytes"),
            names.index("Publish after successful artifact readback"),
        )

    def test_prepare_workflow_dispatches_required_checks(self) -> None:
        workflow_file = evidence.ROOT / ".github/workflows/prepare-release.yml"
        workflow = yaml.safe_load(workflow_file.read_text(encoding="utf-8"))
        events = workflow.get("on", workflow.get(True))
        self.assertEqual(["notes", "version"], sorted(events["workflow_dispatch"]["inputs"]))
        self.assertEqual({"contents": "read"}, workflow["permissions"])
        job = workflow["jobs"]["prepare"]
        self.assertEqual(
            {"contents": "write", "pull-requests": "write", "actions": "write"},
            job["permissions"],
        )
        script = "\n".join(step.get("run", "") for step in job["steps"])
        self.assertIn("gh pr create", script)
        self.assertIn("gh workflow run validate-skills.yml", script)
        self.assertIn("gh workflow run security-audit.yml", script)
        for step in job["steps"]:
            self.assertNotIn("${{ inputs.notes }}", step.get("run", ""))
            self.assertNotIn("${{ inputs.version }}", step.get("run", ""))

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
