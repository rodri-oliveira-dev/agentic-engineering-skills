#!/usr/bin/env python3
"""Command-line entry point for validating the Agent Skills catalog."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

if sys.version_info < (3, 11):
    print("ERROR [runtime] Python 3.11 or newer is required.", file=sys.stderr)
    raise SystemExit(2)

try:
    from skill_validation import CatalogReport, validate_catalog
except ModuleNotFoundError as exc:
    if exc.name == "yaml":
        print(
            "ERROR [runtime] PyYAML is not installed. Run: python -m pip install -r requirements.txt",
            file=sys.stderr,
        )
        raise SystemExit(2) from exc
    raise

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = REPOSITORY_ROOT / ".agents" / "skills"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Validate Agent Skills structure and project conventions without executing skill scripts."
    )
    parser.add_argument(
        "--root",
        type=Path,
        default=DEFAULT_CATALOG,
        help="catalog root (default: repository .agents/skills)",
    )
    parser.add_argument(
        "--skill",
        metavar="NAME",
        help="validate one direct child of the catalog instead of all skills",
    )
    parser.add_argument(
        "--require-skills",
        action="store_true",
        help="treat an empty catalog as an error",
    )
    return parser


def render_report(report: CatalogReport) -> None:
    for issue in sorted(
        report.issues,
        key=lambda item: (item.severity != "error", str(item.path), item.message),
    ):
        stream = sys.stderr if issue.severity == "error" else sys.stdout
        print(issue.format(report.root), file=stream)

    if report.empty_catalog and not report.errors:
        print(
            "Catalog is empty; this is allowed during foundation work. "
            "No skills were validated. Use --require-skills when at least one skill is expected."
        )
    else:
        print(
            f"Checked {len(report.skills)} skill(s): "
            f"{len(report.errors)} error(s), {len(report.warnings)} warning(s)."
        )


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    report = validate_catalog(
        arguments.root,
        selected_skill=arguments.skill,
        require_skills=arguments.require_skills,
    )
    render_report(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
