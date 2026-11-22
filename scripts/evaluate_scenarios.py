#!/usr/bin/env python3
"""Validate behavioral fixtures and prepare reproducible evaluation records."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_FIXTURES = REPOSITORY_ROOT / "tests" / "fixtures"
DEFAULT_CATALOG = REPOSITORY_ROOT / ".agents" / "skills"
COVERAGE_NAME = "coverage.json"
REQUIRED_CATEGORIES = {
    "expected_usage",
    "non_activation",
    "insufficient_information",
    "operational_failure_or_limitation",
}
SCENARIO_HEADING = re.compile(r"^## ([1-9][0-9]*)\. (.+?)\s*$", re.MULTILINE)
FIELD_HEADING = re.compile(r"^\*\*([^*\n]+):\*\*\s*", re.MULTILINE)


class EvaluationError(Exception):
    """A fixture or evaluation record is incomplete or inconsistent."""


def _unique_json_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise EvaluationError(f"JSON contains duplicate key: {key!r}")
        result[key] = value
    return result


@dataclass(frozen=True)
class Scenario:
    skill: str
    number: int
    title: str
    source: Path
    markdown: str
    fields: dict[str, str]

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.markdown.encode("utf-8")).hexdigest()


def _is_timestamp(value: object) -> bool:
    if not isinstance(value, str) or not value.strip():
        return False
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return False
    return parsed.utcoffset() is not None


def _read_json(path: Path) -> Any:
    try:
        return json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_unique_json_object,
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise EvaluationError(f"cannot read JSON {path}: {exc}") from exc


def _fields(markdown: str) -> dict[str, str]:
    matches = list(FIELD_HEADING.finditer(markdown))
    result: dict[str, str] = {}
    for index, match in enumerate(matches):
        label = match.group(1).strip()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(markdown)
        value = markdown[match.end() : end].strip()
        if label in result:
            raise EvaluationError(f"duplicate scenario field {label!r}")
        result[label] = value
    return result


def load_scenarios(fixtures: Path) -> dict[str, dict[int, Scenario]]:
    scenarios: dict[str, dict[int, Scenario]] = {}
    for source in sorted(fixtures.glob("*/scenarios.md")):
        skill = source.parent.name
        try:
            content = source.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            raise EvaluationError(f"cannot read fixture {source}: {exc}") from exc
        headings = list(SCENARIO_HEADING.finditer(content))
        if not headings:
            raise EvaluationError(f"fixture contains no numbered scenarios: {source}")
        skill_scenarios: dict[int, Scenario] = {}
        for index, heading in enumerate(headings):
            number = int(heading.group(1))
            end = headings[index + 1].start() if index + 1 < len(headings) else len(content)
            markdown = content[heading.start() : end].strip() + "\n"
            if number in skill_scenarios:
                raise EvaluationError(f"duplicate scenario {skill}#{number}")
            fields = _fields(markdown)
            if not fields.get("Input"):
                raise EvaluationError(f"scenario {skill}#{number} has no non-empty Input field")
            if len(fields) < 2:
                raise EvaluationError(f"scenario {skill}#{number} has no evaluation expectations")
            skill_scenarios[number] = Scenario(
                skill, number, heading.group(2).strip(), source, markdown, fields
            )
        expected_numbers = list(range(1, len(skill_scenarios) + 1))
        if sorted(skill_scenarios) != expected_numbers:
            raise EvaluationError(f"scenario numbering is not contiguous for {skill}")
        scenarios[skill] = skill_scenarios
    return scenarios


def validate_fixtures(
    fixtures: Path = DEFAULT_FIXTURES, catalog: Path = DEFAULT_CATALOG
) -> tuple[dict[str, dict[int, Scenario]], dict[str, Any]]:
    scenarios = load_scenarios(fixtures)
    coverage = _read_json(fixtures / COVERAGE_NAME)
    if not isinstance(coverage, dict) or coverage.get("schema_version") != 1:
        raise EvaluationError("coverage manifest must use schema_version 1")
    entries = coverage.get("skills")
    if not isinstance(entries, dict):
        raise EvaluationError("coverage manifest field 'skills' must be an object")
    catalog_skills = {
        path.name
        for path in catalog.iterdir()
        if path.is_dir() and not path.is_symlink()
    }
    if set(scenarios) != catalog_skills or set(entries) != catalog_skills:
        raise EvaluationError(
            "catalog, fixture directories, and coverage manifest must contain the same skills"
        )

    for skill, item in entries.items():
        if not isinstance(item, dict):
            raise EvaluationError(f"coverage entry for {skill} must be an object")
        if set(item) != REQUIRED_CATEGORIES | {"destructive_operation"}:
            raise EvaluationError(f"coverage entry for {skill} has missing or unknown categories")
        available = scenarios[skill]
        for category in REQUIRED_CATEGORIES:
            references = item[category]
            if not isinstance(references, list) or not references:
                raise EvaluationError(f"coverage {skill}.{category} must reference a scenario")
            if any(not isinstance(number, int) or number not in available for number in references):
                raise EvaluationError(f"coverage {skill}.{category} references an unknown scenario")
        destructive = item["destructive_operation"]
        if not isinstance(destructive, dict) or set(destructive) != {
            "applicable",
            "scenarios",
            "rationale",
        }:
            raise EvaluationError(f"coverage {skill}.destructive_operation is invalid")
        references = destructive["scenarios"]
        if not isinstance(destructive["applicable"], bool) or not isinstance(references, list):
            raise EvaluationError(f"coverage {skill}.destructive_operation has invalid types")
        if any(not isinstance(number, int) or number not in available for number in references):
            raise EvaluationError(
                f"coverage {skill}.destructive_operation references an unknown scenario"
            )
        if destructive["applicable"] and not references:
            raise EvaluationError(f"coverage {skill} requires a destructive-operation scenario")
        if not destructive["applicable"] and references:
            raise EvaluationError(f"coverage {skill} marks destructive operation not applicable")
        if not isinstance(destructive["rationale"], str) or not destructive["rationale"].strip():
            raise EvaluationError(f"coverage {skill}.destructive_operation needs a rationale")
    return scenarios, coverage


def prepare_record(scenario: Scenario, platform: str, agent_version: str) -> dict[str, Any]:
    criteria = [
        {"label": label, "text": value, "outcome": "pending", "evidence": None}
        for label, value in scenario.fields.items()
        if label != "Input"
    ]
    return {
        "schema_version": 1,
        "status": "pending",
        "prepared_at": datetime.now(timezone.utc).isoformat(),
        "scenario": {
            "skill": scenario.skill,
            "number": scenario.number,
            "title": scenario.title,
            "source_sha256": scenario.digest,
            "input": scenario.fields["Input"],
        },
        "agent": {"platform": platform, "version": agent_version},
        "execution": {
            "started_at": None,
            "completed_at": None,
            "environment": {},
            "output": None,
        },
        "criteria": criteria,
        "limitations": [],
        "notes": None,
    }


def validate_record(record: Any, scenarios: dict[str, dict[int, Scenario]]) -> None:
    if not isinstance(record, dict) or record.get("schema_version") != 1:
        raise EvaluationError("evaluation record must use schema_version 1")
    if not _is_timestamp(record.get("prepared_at")):
        raise EvaluationError("evaluation record must contain a timezone-aware preparation time")
    identity = record.get("scenario")
    if not isinstance(identity, dict):
        raise EvaluationError("evaluation record has no scenario identity")
    skill, number = identity.get("skill"), identity.get("number")
    if skill not in scenarios or not isinstance(number, int) or number not in scenarios[skill]:
        raise EvaluationError("evaluation record references an unknown scenario")
    scenario = scenarios[skill][number]
    if identity.get("source_sha256") != scenario.digest:
        raise EvaluationError(f"evaluation record for {skill}#{number} is stale")
    if identity.get("title") != scenario.title or identity.get("input") != scenario.fields["Input"]:
        raise EvaluationError(f"evaluation record for {skill}#{number} changed the fixture input")
    status = record.get("status")
    if status not in {"pending", "completed"}:
        raise EvaluationError("evaluation status must be 'pending' or 'completed'")
    criteria = record.get("criteria")
    if not isinstance(criteria, list) or not criteria:
        raise EvaluationError("evaluation record must contain criteria")
    expected_criteria = [
        (label, text) for label, text in scenario.fields.items() if label != "Input"
    ]
    if any(not isinstance(item, dict) for item in criteria) or [
        (item.get("label"), item.get("text")) for item in criteria
    ] != expected_criteria:
        raise EvaluationError("evaluation record criteria do not match the fixture")
    if status == "pending":
        if any(item.get("outcome") != "pending" for item in criteria if isinstance(item, dict)):
            raise EvaluationError("pending evaluations cannot contain assessed criteria")
        return
    agent = record.get("agent")
    execution = record.get("execution")
    if not isinstance(agent, dict) or not all(
        isinstance(agent.get(key), str) and agent[key].strip() for key in ("platform", "version")
    ):
        raise EvaluationError("completed evaluation must identify platform and agent version")
    if agent["version"].strip().lower() in {"unknown", "version", "n/a"}:
        raise EvaluationError("completed evaluation must contain the exact agent version")
    if (
        not isinstance(execution, dict)
        or not _is_timestamp(execution.get("started_at"))
        or not _is_timestamp(execution.get("completed_at"))
        or not isinstance(execution.get("environment"), dict)
        or not execution["environment"]
        or not isinstance(execution.get("output"), str)
        or not execution["output"].strip()
    ):
        raise EvaluationError("completed evaluation must record timestamps, environment, and output")
    if datetime.fromisoformat(execution["completed_at"]) < datetime.fromisoformat(
        execution["started_at"]
    ):
        raise EvaluationError("completed evaluation cannot finish before it starts")
    for item in criteria:
        if not isinstance(item, dict) or item.get("outcome") not in {
            "met",
            "not_met",
            "not_applicable",
        }:
            raise EvaluationError("completed evaluation has an unassessed criterion")
        if not isinstance(item.get("evidence"), str) or not item["evidence"].strip():
            raise EvaluationError("completed evaluation criteria require evidence")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixtures", type=Path, default=DEFAULT_FIXTURES)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
    subparsers = parser.add_subparsers(dest="command", required=True)
    check = subparsers.add_parser("check", help="validate fixtures and optional records")
    check.add_argument("--records", type=Path)
    prepare = subparsers.add_parser("prepare", help="create one pending evaluation record")
    prepare.add_argument("--skill", required=True)
    prepare.add_argument("--scenario", required=True, type=int)
    prepare.add_argument("--platform", required=True)
    prepare.add_argument("--agent-version", required=True)
    prepare.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        scenarios, _ = validate_fixtures(arguments.fixtures, arguments.catalog)
        if arguments.command == "prepare":
            if arguments.skill not in scenarios or arguments.scenario not in scenarios[arguments.skill]:
                raise EvaluationError("requested scenario does not exist")
            record = prepare_record(
                scenarios[arguments.skill][arguments.scenario],
                arguments.platform,
                arguments.agent_version,
            )
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            with arguments.output.open("x", encoding="utf-8", newline="\n") as stream:
                json.dump(record, stream, indent=2, ensure_ascii=False)
                stream.write("\n")
            print(f"Prepared pending evaluation: {arguments.output}")
            return 0
        if arguments.records is not None and not arguments.records.is_dir():
            raise EvaluationError(f"records directory does not exist: {arguments.records}")
        records = [] if arguments.records is None else sorted(arguments.records.glob("*.json"))
        for path in records:
            validate_record(_read_json(path), scenarios)
        count = sum(len(items) for items in scenarios.values())
        print(
            f"Checked {count} behavioral scenario(s) for {len(scenarios)} skill(s) "
            f"and {len(records)} evaluation record(s). No agent execution was performed."
        )
        return 0
    except (EvaluationError, OSError) as exc:
        print(f"ERROR [behavioral-evaluation] {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
