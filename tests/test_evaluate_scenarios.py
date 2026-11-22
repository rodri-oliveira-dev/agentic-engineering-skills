from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIRECTORY = REPOSITORY_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from evaluate_scenarios import (  # noqa: E402
    DEFAULT_CATALOG,
    DEFAULT_FIXTURES,
    EvaluationError,
    _read_json,
    load_scenarios,
    prepare_record,
    validate_fixtures,
    validate_record,
)


class BehavioralFixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.scenarios, cls.coverage = validate_fixtures(DEFAULT_FIXTURES, DEFAULT_CATALOG)

    def test_every_canonical_skill_has_required_behavioral_coverage(self) -> None:
        self.assertEqual(10, len(self.scenarios))
        self.assertEqual(set(self.scenarios), set(self.coverage["skills"]))
        self.assertTrue(all(self.scenarios.values()))

    def test_fixture_rejects_an_empty_evaluation_expectation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixtures = Path(temporary_directory)
            skill = fixtures / "testing"
            skill.mkdir()
            (skill / "scenarios.md").write_text(
                "## 1. Empty expectation\n\n"
                "**Input:** Run the test.\n\n"
                "**Expected behavior:**\n",
                encoding="utf-8",
            )

            with self.assertRaisesRegex(EvaluationError, "empty evaluation expectation"):
                load_scenarios(fixtures)

    def test_pending_record_contains_reproducible_input_without_claiming_execution(self) -> None:
        scenario = self.scenarios["code-review"][1]

        record = prepare_record(scenario, "openai-codex", "record-before-run")

        validate_record(record, self.scenarios)
        self.assertEqual("pending", record["status"])
        self.assertEqual(scenario.fields["Input"], record["scenario"]["input"])
        self.assertIsNone(record["execution"]["output"])
        self.assertTrue(all(item["outcome"] == "pending" for item in record["criteria"]))

    def test_completed_record_requires_execution_evidence(self) -> None:
        scenario = self.scenarios["testing"][1]
        record = prepare_record(scenario, "openai-codex", "example-version")
        record["status"] = "completed"

        with self.assertRaisesRegex(EvaluationError, "timestamps, environment, and output"):
            validate_record(record, self.scenarios)

        record["execution"] = {
            "started_at": "2026-11-22T12:00:00-03:00",
            "completed_at": "2026-11-22T12:01:00-03:00",
            "environment": {"os": "isolated-test-environment"},
            "output": "Observed agent response.",
        }
        for criterion in record["criteria"]:
            criterion["outcome"] = "met"
            criterion["evidence"] = "Matched the recorded output."

        validate_record(record, self.scenarios)

    def test_completed_record_rejects_inverted_timestamps(self) -> None:
        scenario = self.scenarios["testing"][1]
        record = prepare_record(scenario, "openai-codex", "example-version")
        record["status"] = "completed"
        record["execution"] = {
            "started_at": "2026-11-22T12:01:00-03:00",
            "completed_at": "2026-11-22T12:00:00-03:00",
            "environment": {"os": "isolated-test-environment"},
            "output": "Observed agent response.",
        }
        for criterion in record["criteria"]:
            criterion["outcome"] = "met"
            criterion["evidence"] = "Matched the recorded output."

        with self.assertRaisesRegex(EvaluationError, "finish before it starts"):
            validate_record(record, self.scenarios)

    def test_json_reader_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            path = Path(temporary_directory) / "record.json"
            path.write_text('{"status":"pending","status":"completed"}', encoding="utf-8")

            with self.assertRaisesRegex(EvaluationError, "duplicate key"):
                _read_json(path)

    def test_record_becomes_stale_when_fixture_hash_changes(self) -> None:
        scenario = self.scenarios["docs"][1]
        record = prepare_record(scenario, "openai-codex", "example-version")
        stale = copy.deepcopy(record)
        stale["scenario"]["source_sha256"] = "0" * 64

        with self.assertRaisesRegex(EvaluationError, "is stale"):
            validate_record(stale, self.scenarios)

    def test_record_cannot_change_fixture_input_or_criteria(self) -> None:
        scenario = self.scenarios["docs"][1]
        record = prepare_record(scenario, "openai-codex", "example-version")
        changed_input = copy.deepcopy(record)
        changed_input["scenario"]["input"] = "Easier prompt"
        changed_criteria = copy.deepcopy(record)
        changed_criteria["criteria"].pop()

        with self.assertRaisesRegex(EvaluationError, "changed the fixture input"):
            validate_record(changed_input, self.scenarios)
        with self.assertRaisesRegex(EvaluationError, "criteria do not match"):
            validate_record(changed_criteria, self.scenarios)

    def test_record_rejects_non_string_membership_values(self) -> None:
        scenario = self.scenarios["testing"][1]

        invalid_skill = prepare_record(scenario, "openai-codex", "example-version")
        invalid_skill["scenario"]["skill"] = []
        with self.assertRaisesRegex(EvaluationError, "unknown scenario"):
            validate_record(invalid_skill, self.scenarios)

        invalid_status = prepare_record(scenario, "openai-codex", "example-version")
        invalid_status["status"] = []
        with self.assertRaisesRegex(EvaluationError, "evaluation status"):
            validate_record(invalid_status, self.scenarios)

        invalid_outcome = prepare_record(scenario, "openai-codex", "example-version")
        invalid_outcome["status"] = "completed"
        invalid_outcome["execution"] = {
            "started_at": "2026-11-22T12:00:00-03:00",
            "completed_at": "2026-11-22T12:01:00-03:00",
            "environment": {"os": "isolated-test-environment"},
            "output": "Observed agent response.",
        }
        for criterion in invalid_outcome["criteria"]:
            criterion["outcome"] = "met"
            criterion["evidence"] = "Matched the recorded output."
        invalid_outcome["criteria"][0]["outcome"] = []
        with self.assertRaisesRegex(EvaluationError, "unassessed criterion"):
            validate_record(invalid_outcome, self.scenarios)

    def test_cli_rejects_unknown_scenario_without_creating_a_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "record.json"
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIRECTORY / "evaluate_scenarios.py"),
                    "prepare",
                    "--skill",
                    "testing",
                    "--scenario",
                    "999",
                    "--platform",
                    "openai-codex",
                    "--agent-version",
                    "unknown",
                    "--output",
                    str(output),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertIn("requested scenario does not exist", result.stderr)
            self.assertFalse(output.exists())

    def test_cli_does_not_overwrite_an_existing_record(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output = Path(temporary_directory) / "record.json"
            output.write_text(json.dumps({"keep": True}), encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIRECTORY / "evaluate_scenarios.py"),
                    "prepare",
                    "--skill",
                    "testing",
                    "--scenario",
                    "1",
                    "--platform",
                    "openai-codex",
                    "--agent-version",
                    "unknown",
                    "--output",
                    str(output),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

            self.assertEqual(1, result.returncode)
            self.assertEqual({"keep": True}, json.loads(output.read_text(encoding="utf-8")))

    def test_cli_rejects_a_missing_records_directory(self) -> None:
        result = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS_DIRECTORY / "evaluate_scenarios.py"),
                "check",
                "--records",
                "does-not-exist",
            ],
            cwd=REPOSITORY_ROOT,
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )

        self.assertEqual(1, result.returncode)
        self.assertIn("records directory does not exist", result.stderr)

    def test_cli_reports_malformed_membership_types_without_a_traceback(self) -> None:
        scenario = self.scenarios["testing"][1]
        record = prepare_record(scenario, "openai-codex", "example-version")
        record["scenario"]["skill"] = []

        with tempfile.TemporaryDirectory() as temporary_directory:
            records_directory = Path(temporary_directory)
            (records_directory / "malformed.json").write_text(
                json.dumps(record), encoding="utf-8"
            )
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPTS_DIRECTORY / "evaluate_scenarios.py"),
                    "check",
                    "--records",
                    str(records_directory),
                ],
                cwd=REPOSITORY_ROOT,
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=False,
            )

        self.assertEqual(1, result.returncode)
        self.assertIn("unknown scenario", result.stderr)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
