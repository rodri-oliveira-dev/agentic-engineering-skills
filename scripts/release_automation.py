#!/usr/bin/env python3
"""Prepare a version PR and validate the pinned version across plugin manifests.

Release notes are proposed by the maintainer. Preparation never publishes a
tag, a release, or fabricated validation/provenance claims.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = re.compile(r"(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)")
ASSIGNMENT = re.compile(r'^PLUGIN_VERSION = "([^"]+)"$', re.MULTILINE)
MAX_NOTES_LENGTH = 12000

MANIFESTS = (
    ("plugins/agentic-engineering/plugin.json", ("version",)),
    (".agents/plugins/marketplace.json", ("plugins", 0, "version")),
    (".github/plugin/marketplace.json", ("plugins", 0, "version")),
    (".github/plugin/marketplace.json", ("metadata", "version")),
    (".claude-plugin/marketplace.json", ("plugins", 0, "version")),
)


def version_tuple(value: str) -> tuple[int, int, int]:
    match = VERSION.fullmatch(value)
    if not match:
        raise ValueError(f"Expected canonical stable SemVer X.Y.Z, got {value!r}")
    return tuple(map(int, match.groups()))


def get_current_version(root: Path = ROOT) -> str:
    content = (root / "scripts/package_plugins.py").read_text(encoding="utf-8")
    matches = ASSIGNMENT.findall(content)
    if len(matches) != 1:
        raise ValueError("Expected exactly one PLUGIN_VERSION assignment in package_plugins.py")
    version_tuple(matches[0])
    return matches[0]


def notes_path(root: Path, version: str) -> Path:
    version_tuple(version)
    return root / "docs" / "releases" / f"{version}-notes.md"


def validate_notes(notes: str) -> str:
    clean = notes.replace("\r\n", "\n").replace("\r", "\n").strip()
    if not clean or len(clean) > MAX_NOTES_LENGTH or "\x00" in clean:
        raise ValueError("Release notes must be nonempty, <=12000 characters, and contain no NUL")
    if any(ord(char) < 32 and char not in "\n\t" for char in clean):
        raise ValueError("Release notes contain unsupported control characters")
    return clean


def prepare(version: str, notes: str, root: Path = ROOT) -> None:
    candidate = version_tuple(version)
    current = get_current_version(root)
    if candidate <= version_tuple(current):
        raise ValueError(f"New version {version} must be greater than current {current}")
    clean_notes = validate_notes(notes)
    destination = notes_path(root, version)
    if destination.exists() or destination.is_symlink():
        raise ValueError(f"Release notes already exist: {destination}")
    generator = root / "scripts/package_plugins.py"
    original = generator.read_text(encoding="utf-8")
    revised, count = ASSIGNMENT.subn(f'PLUGIN_VERSION = "{version}"', original)
    if count != 1:
        raise ValueError("Cannot safely update version assignment")
    generator.write_text(revised, encoding="utf-8")
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(
        f"# Release {version}\n\n"
        "Approved release notes for the proposed version. This document alone "
        "does not attest that the version was published.\n\n"
        f"{clean_notes}\n",
        encoding="utf-8",
    )
    subprocess.run(
        [sys.executable, str(generator), "generate"],
        check=True,
        cwd=root,
    )


def validate(version: str, root: Path = ROOT) -> None:
    version_tuple(version)
    actual = get_current_version(root)
    if actual != version:
        raise ValueError(f"Repository version is {actual}, not requested {version}")
    for relative, selectors in MANIFESTS:
        item: object = json.loads((root / relative).read_text(encoding="utf-8"))
        for selector in selectors:
            if isinstance(selector, int):
                if not isinstance(item, list):
                    raise ValueError(f"Malformed manifest list in {relative}")
                item = item[selector]
            else:
                if not isinstance(item, dict):
                    raise ValueError(f"Malformed manifest object in {relative}")
                item = item[selector]
        if item != version:
            raise ValueError(f"Manifest version mismatch in {relative}: {item!r}")
    notes = notes_path(root, version)
    if not notes.is_file() or notes.is_symlink():
        raise ValueError(f"Missing regular release notes: {notes}")
    contents = notes.read_text(encoding="utf-8")
    if not contents.startswith(f"# Release {version}\n"):
        raise ValueError(f"Release notes heading does not match version {version}")
    validate_notes(contents)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    prep = subparsers.add_parser("prepare")
    prep.add_argument("--version", required=True)
    prep.add_argument("--notes", required=True)
    check = subparsers.add_parser("check")
    check.add_argument("--version", required=True)
    args = parser.parse_args()
    try:
        if args.command == "prepare":
            prepare(args.version, args.notes)
        else:
            validate(args.version)
    except (OSError, ValueError, KeyError, IndexError, TypeError, json.JSONDecodeError,
            subprocess.CalledProcessError) as exc:
        print(f"ERROR [release] {exc}", file=sys.stderr)
        return 1
    print(f"Release {args.version}: {args.command} passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
