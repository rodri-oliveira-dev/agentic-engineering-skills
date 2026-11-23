"""Produce a scoped supply-chain inventory and deterministic release archive.

Inventory hashes are integrity evidence, not publisher/build attestations.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import stat
import sys
import urllib.request
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PINNED_REQUIREMENT = re.compile(r"^([a-zA-Z0-9_.-]+)==([a-zA-Z0-9_.+!-]+)$")
ACTION_USE = re.compile(r"^\s*uses:\s*([^\s#]+)", re.MULTILINE)
REMOTE_ACTION = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+(?:/[A-Za-z0-9_.-]+)?@[0-9a-f]{40}$")
SAFE_VERSION = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?$")


def digest(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def pinned_requirements() -> list[dict[str, str]]:
    pins: list[dict[str, str]] = []
    for line in (ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines():
        stripped = line.split("#", 1)[0].strip()
        if not stripped:
            continue
        match = PINNED_REQUIREMENT.fullmatch(stripped)
        if not match:
            raise ValueError(f"Unsupported or unpinned requirement: {stripped}")
        pins.append({"name": match[1], "version": match[2]})
    if not pins:
        raise ValueError("No pinned Python dependencies found")
    return pins


def action_inventory() -> list[dict[str, str]]:
    actions = []
    for workflow in sorted((ROOT / ".github/workflows").glob("*.yml")):
        for value in ACTION_USE.findall(workflow.read_text(encoding="utf-8")):
            if not REMOTE_ACTION.fullmatch(value):
                raise ValueError(f"Unpinned or unsupported action in {workflow.name}: {value}")
            actions.append({"workflow": workflow.relative_to(ROOT).as_posix(), "reference": value})
    return actions


def wheel_inventory(directory: Path, pins: list[dict[str, str]]) -> list[dict[str, object]]:
    artifacts = sorted(path for path in directory.iterdir() if path.is_file())
    if len(artifacts) != len(pins):
        raise ValueError("Downloaded wheel count does not match pinned requirements")
    records = []
    for pin in pins:
        name = re.sub(r"[-_.]+", "_", pin["name"]).lower()
        wheels = [path for path in artifacts if path.name.lower().startswith(f"{name}-{pin['version']}-") and path.suffix == ".whl"]
        if len(wheels) != 1:
            raise ValueError(f"Expected exactly one binary distribution for {pin['name']}=={pin['version']}")
        wheel = wheels[0]
        url = f"https://pypi.org/pypi/{pin['name']}/{pin['version']}/json"
        request = urllib.request.Request(url, headers={"User-Agent": "agentic-engineering-skills-supply-chain/1"})
        with urllib.request.urlopen(request, timeout=30) as response:
            metadata = json.load(response)
        matches = [entry for entry in metadata["urls"] if entry["filename"] == wheel.name]
        if len(matches) != 1 or "sha256" not in matches[0].get("digests", {}):
            raise ValueError(f"PyPI metadata has no SHA-256 for {wheel.name}")
        local = digest(wheel)
        published = matches[0]["digests"]["sha256"]
        if local != published:
            raise ValueError(f"PyPI digest mismatch for {wheel.name}")
        records.append({
            "name": pin["name"], "version": pin["version"],
            "filename": wheel.name, "sha256": local,
            "pypi_metadata_url": url, "pypi_sha256_matches": True,
            "build_provenance": "not evaluated",
        })
    return records


def write_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def inventory(args: argparse.Namespace) -> None:
    pins = pinned_requirements()
    generated = ROOT / "plugins/agentic-engineering/.agentic-engineering-package.json"
    if not generated.is_file():
        raise ValueError("Generated plugin inventory is missing")
    write_json(Path(args.output), {
        "schema_version": 1,
        "collected_at_utc": dt.datetime.now(dt.timezone.utc).isoformat(),
        "repository_revision": os.environ.get("GITHUB_SHA", "local-unverified"),
        "requirements_sha256": digest(ROOT / "requirements.txt"),
        "generated_package_inventory_sha256": digest(generated),
        "dependencies": wheel_inventory(Path(args.wheel_dir), pins),
        "github_actions": action_inventory(),
        "scope": "Python requirements and referenced GitHub Actions; not a complete release SBOM",
        "limitations": [
            "Matching PyPI digests do not establish build provenance or publisher identity.",
            "Action SHAs identify commits but do not independently authenticate their authors.",
            "The plugin's embedded hashes are integrity checks, not independent signatures.",
            "Agent behavioral safety and runtime compatibility are outside this inventory.",
        ],
    })


def release_archive(args: argparse.Namespace) -> None:
    manifest = json.loads((ROOT / "plugins/agentic-engineering/plugin.json").read_text(encoding="utf-8"))
    version = manifest["version"]
    if not SAFE_VERSION.fullmatch(args.tag) or args.tag != version:
        raise ValueError(f"Release tag {args.tag!r} does not match plugin version {version!r}")
    root = ROOT / "plugins/agentic-engineering"
    files = sorted(p for p in root.rglob("*") if p.is_file() or p.is_symlink())
    if not files:
        raise ValueError("Plugin package is empty")
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(output, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root.resolve()):
                raise ValueError(f"Unsafe package entry: {path}")
            relative = path.relative_to(root).as_posix()
            info = zipfile.ZipInfo(f"agentic-engineering/{relative}", date_time=(1980, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (stat.S_IFREG | 0o644) << 16
            archive.writestr(info, path.read_bytes(), compress_type=zipfile.ZIP_DEFLATED, compresslevel=9)
    sha = digest(output)
    output.with_name(output.name + ".sha256").write_text(f"{sha}  {output.name}\n", encoding="ascii")
    print(f"Artifact SHA-256: {sha}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    inv = commands.add_parser("inventory")
    inv.add_argument("--wheel-dir", required=True)
    inv.add_argument("--output", required=True)
    package = commands.add_parser("package")
    package.add_argument("--tag", required=True)
    package.add_argument("--output", required=True)
    args = parser.parse_args()
    try:
        if args.command == "inventory":
            inventory(args)
        else:
            release_archive(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(f"Supply-chain evidence error: {exc}", file=sys.stderr)
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
