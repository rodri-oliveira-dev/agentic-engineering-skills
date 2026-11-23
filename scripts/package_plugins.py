#!/usr/bin/env python3
"""Build and verify marketplace plugin artifacts from canonical Agent Skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Iterable

if sys.version_info < (3, 11):
    print("ERROR [runtime] Python 3.11 or newer is required.", file=sys.stderr)
    raise SystemExit(2)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = REPOSITORY_ROOT / ".agents" / "skills"
PLUGIN_NAME = "agentic-engineering"
PLUGIN_VERSION = "1.0.0"
PLUGIN_DESCRIPTION = (
    "Reusable software-engineering workflows for design, review, debugging, "
    "delivery, documentation, SQL, and testing."
)
MARKETPLACE_NAME = "agentic-engineering-skills"
PLUGIN_RELATIVE = Path("plugins") / PLUGIN_NAME
INVENTORY_NAME = ".agentic-engineering-package.json"
AGENT_PLUGINS_SCHEMA = (
    "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
)
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class PackageError(Exception):
    """The plugin package cannot be built or verified safely."""


def _json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _sha256_bytes(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _lf_bytes(content: bytes) -> bytes:
    """Return portable text bytes independent of checkout line endings."""
    return content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def _path_exists(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _validate_safe_output_directory(output_root: Path, directory: Path) -> None:
    """Reject existing symlinks or non-directories in a generated output path."""
    root = Path(os.path.abspath(output_root.expanduser()))
    target = Path(os.path.abspath(directory.expanduser()))
    try:
        relative = target.relative_to(root)
    except ValueError as exc:
        raise PackageError(f"generated output directory escapes its root: {directory}") from exc
    candidates = [root]
    current = root
    for part in relative.parts:
        current /= part
        candidates.append(current)
    for candidate in candidates:
        if not _path_exists(candidate):
            continue
        if candidate.is_symlink() or not candidate.is_dir():
            raise PackageError(
                f"generated output directory must be a regular directory: {candidate}"
            )


def _regular_files(root: Path) -> dict[str, Path]:
    if root.is_symlink() or not root.is_dir():
        raise PackageError(f"directory must be a regular directory: {root}")
    boundary = root.resolve()
    files: dict[str, Path] = {}
    for current, directories, filenames in os.walk(root, followlinks=False):
        current_path = Path(current)
        for directory in list(directories):
            candidate = current_path / directory
            if candidate.is_symlink():
                raise PackageError(f"symlinked directories are not distributable: {candidate}")
        for filename in filenames:
            candidate = current_path / filename
            if candidate.is_symlink() or not candidate.is_file():
                raise PackageError(f"non-regular files are not distributable: {candidate}")
            resolved = candidate.resolve()
            if boundary != resolved and boundary not in resolved.parents:
                raise PackageError(f"file escapes its distribution root: {candidate}")
            files[candidate.relative_to(root).as_posix()] = candidate
    return dict(sorted(files.items()))


def _canonical_files(catalog: Path) -> dict[str, bytes]:
    catalog = catalog.expanduser()
    if catalog.is_symlink() or not catalog.is_dir():
        raise PackageError(f"canonical catalog must be a regular directory: {catalog}")
    skills = sorted(catalog.iterdir(), key=lambda path: path.name)
    if not skills:
        raise PackageError(f"canonical catalog is empty: {catalog}")
    output: dict[str, bytes] = {}
    for skill in skills:
        if skill.is_symlink() or not skill.is_dir():
            raise PackageError(f"canonical catalog contains a non-skill entry: {skill}")
        if not SKILL_NAME.fullmatch(skill.name):
            raise PackageError(f"invalid canonical skill directory name: {skill.name}")
        skill_files = _regular_files(skill)
        if "SKILL.md" not in skill_files:
            raise PackageError(f"canonical skill is missing SKILL.md: {skill.name}")
        for relative, source in skill_files.items():
            output[f"skills/{skill.name}/{relative}"] = _lf_bytes(source.read_bytes())
    return output


def _portable_manifest() -> bytes:
    return _json_bytes(
        {
            "$schema": AGENT_PLUGINS_SCHEMA,
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "author": {
                "name": "rodri-oliveira-dev",
                "url": "https://github.com/rodri-oliveira-dev",
            },
            "repository": (
                "https://github.com/rodri-oliveira-dev/agentic-engineering-skills"
            ),
            "license": "MIT",
            "keywords": ["agent-skills", "software-engineering", "developer-tools"],
        }
    )


def _claude_manifest() -> bytes:
    return _json_bytes(
        {
            "name": PLUGIN_NAME,
            "version": PLUGIN_VERSION,
            "description": PLUGIN_DESCRIPTION,
            "author": {
                "name": "rodri-oliveira-dev",
                "url": "https://github.com/rodri-oliveira-dev",
            },
            "repository": (
                "https://github.com/rodri-oliveira-dev/agentic-engineering-skills"
            ),
            "license": "MIT",
            "keywords": ["agent-skills", "software-engineering", "developer-tools"],
        }
    )


def _marketplaces() -> dict[str, bytes]:
    common_entry = {
        "name": PLUGIN_NAME,
        "source": f"./{PLUGIN_RELATIVE.as_posix()}",
        "description": PLUGIN_DESCRIPTION,
        "version": PLUGIN_VERSION,
    }
    portable_marketplace = {
        "name": MARKETPLACE_NAME,
        "interface": {"displayName": "Agentic Engineering Skills"},
        "plugins": [
            {
                "name": PLUGIN_NAME,
                "source": {
                    "source": "local",
                    "path": f"./{PLUGIN_RELATIVE.as_posix()}",
                },
                "description": PLUGIN_DESCRIPTION,
                "version": PLUGIN_VERSION,
                "policy": {
                    "installation": "AVAILABLE",
                    "authentication": "ON_INSTALL",
                },
                "category": "Developer Tools",
            }
        ],
    }
    legacy_marketplace = {
        "name": MARKETPLACE_NAME,
        "owner": {"name": "rodri-oliveira-dev"},
        "metadata": {
            "description": "Agentic Engineering Skills plugin marketplace.",
            "version": PLUGIN_VERSION,
        },
        "plugins": [common_entry],
    }
    claude_marketplace = {
        "name": MARKETPLACE_NAME,
        "description": "Agentic Engineering Skills plugin marketplace.",
        "owner": {"name": "rodri-oliveira-dev"},
        "plugins": [common_entry],
    }
    return {
        ".agents/plugins/marketplace.json": _json_bytes(portable_marketplace),
        ".github/plugin/marketplace.json": _json_bytes(legacy_marketplace),
        ".claude-plugin/marketplace.json": _json_bytes(claude_marketplace),
    }


def expected_distribution(catalog: Path) -> dict[str, bytes]:
    """Return every generated file, keyed relative to the marketplace root."""
    package_files = _canonical_files(catalog)
    package_files["plugin.json"] = _portable_manifest()
    package_files[".claude-plugin/plugin.json"] = _claude_manifest()
    package_files["LICENSE"] = _lf_bytes((REPOSITORY_ROOT / "LICENSE").read_bytes())
    package_files = dict(sorted(package_files.items()))
    inventory = {
        "schema_version": 1,
        "generated_by": "scripts/package_plugins.py",
        "canonical_source": ".agents/skills",
        "plugin": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "files": {
            relative: _sha256_bytes(content)
            for relative, content in package_files.items()
        },
    }
    output = {
        f"{PLUGIN_RELATIVE.as_posix()}/{relative}": content
        for relative, content in package_files.items()
    }
    output[f"{PLUGIN_RELATIVE.as_posix()}/{INVENTORY_NAME}"] = _json_bytes(inventory)
    output.update(_marketplaces())
    return dict(sorted(output.items()))


def verify_package(package: Path) -> list[str]:
    """Verify a generated package against its embedded SHA-256 inventory."""
    errors: list[str] = []
    inventory_path = package / INVENTORY_NAME
    if not inventory_path.is_file() or inventory_path.is_symlink():
        return [f"missing regular package inventory: {inventory_path}"]
    try:
        inventory = json.loads(inventory_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"cannot read package inventory: {exc}"]
    expected_keys = {
        "schema_version",
        "generated_by",
        "canonical_source",
        "plugin",
        "version",
        "files",
    }
    if not isinstance(inventory, dict) or set(inventory) != expected_keys:
        return ["package inventory has an unsupported structure"]
    if inventory.get("schema_version") != 1 or inventory.get("plugin") != PLUGIN_NAME:
        errors.append("package inventory identity or schema is unsupported")
    hashes = inventory.get("files")
    if not isinstance(hashes, dict):
        return [*errors, "package inventory files must be an object"]
    try:
        actual = _regular_files(package)
    except PackageError as exc:
        return [*errors, str(exc)]
    actual.pop(INVENTORY_NAME, None)
    expected_names = set(hashes)
    actual_names = set(actual)
    for missing in sorted(expected_names - actual_names):
        errors.append(f"missing packaged file: {missing}")
    for extra in sorted(actual_names - expected_names):
        errors.append(f"untracked packaged file: {extra}")
    for relative in sorted(expected_names & actual_names):
        digest = hashes[relative]
        if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
            errors.append(f"invalid recorded digest: {relative}")
        elif _sha256_file(actual[relative]) != digest:
            errors.append(f"modified packaged file: {relative}")
    return errors


def validate_codex_distribution(
    *, output_root: Path, expected_skill_names: set[str]
) -> list[str]:
    """Validate the Codex marketplace, portable manifest, and resolved package paths."""
    errors: list[str] = []
    marketplace_path = output_root / ".agents" / "plugins" / "marketplace.json"
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"cannot read Codex marketplace JSON: {exc}"]
    if not isinstance(marketplace, dict):
        return ["Codex marketplace must be a JSON object"]
    if not isinstance(marketplace.get("name"), str) or not marketplace["name"]:
        errors.append("Codex marketplace requires a non-empty name")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        errors.append("Codex marketplace must contain exactly one plugin entry")
        return errors
    entry = plugins[0]
    if not isinstance(entry, dict):
        return [*errors, "Codex marketplace plugin entry must be an object"]
    if entry.get("name") != PLUGIN_NAME:
        errors.append("Codex marketplace plugin name does not match the package")
    source = entry.get("source")
    if not isinstance(source, dict) or source.get("source") != "local":
        errors.append("Codex marketplace plugin source must be a local source object")
        return errors
    source_path = source.get("path")
    if not isinstance(source_path, str) or not source_path.startswith("./"):
        errors.append("Codex marketplace source.path must start with './'")
        return errors
    relative_source = Path(source_path)
    if relative_source.is_absolute() or ".." in relative_source.parts:
        errors.append("Codex marketplace source.path must remain inside its root")
        return errors
    marketplace_root = output_root.resolve()
    resolved_plugin = (output_root / relative_source).resolve()
    if marketplace_root != resolved_plugin and marketplace_root not in resolved_plugin.parents:
        errors.append("Codex marketplace source.path escapes its root")
        return errors
    if resolved_plugin != (output_root / PLUGIN_RELATIVE).resolve():
        errors.append("Codex marketplace source.path resolves to the wrong plugin")
    if not resolved_plugin.is_dir():
        errors.append("Codex marketplace source.path does not resolve to a plugin directory")
        return errors

    policy = entry.get("policy")
    if not isinstance(policy, dict):
        errors.append("Codex marketplace plugin entry requires a policy object")
    else:
        if policy.get("installation") != "AVAILABLE":
            errors.append("Codex marketplace plugin must be available for installation")
        if policy.get("authentication") not in {"ON_INSTALL", "ON_USE"}:
            errors.append("Codex marketplace plugin requires a supported auth policy value")
    if not isinstance(entry.get("category"), str) or not entry["category"]:
        errors.append("Codex marketplace plugin requires a category")

    manifest_path = resolved_plugin / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [*errors, f"cannot read portable plugin manifest JSON: {exc}"]
    if not isinstance(manifest, dict):
        return [*errors, "portable plugin manifest must be a JSON object"]
    required_manifest = {
        "$schema": AGENT_PLUGINS_SCHEMA,
        "name": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "description": PLUGIN_DESCRIPTION,
    }
    for field, expected in required_manifest.items():
        if manifest.get(field) != expected:
            errors.append(f"portable plugin manifest has invalid {field!r}")
    allowed_manifest_fields = {
        "$schema",
        "name",
        "version",
        "description",
        "author",
        "homepage",
        "repository",
        "license",
        "keywords",
        "extensions",
    }
    for field in sorted(set(manifest) - allowed_manifest_fields):
        errors.append(f"portable plugin manifest has unsupported field: {field}")
    if "extensions" in manifest:
        errors.append("portable plugin must not declare unused Codex extensions")

    for forbidden in ("mcp.json", ".mcp.json", "hooks", "agents", ".codex-plugin"):
        if _path_exists(resolved_plugin / forbidden):
            errors.append(f"Codex plugin contains unsupported unused component: {forbidden}")
    skills_root = resolved_plugin / "skills"
    if not skills_root.is_dir() or skills_root.is_symlink():
        errors.append("Codex plugin skills path must be a regular directory")
        return errors
    actual_skill_names: set[str] = set()
    for entry_path in skills_root.iterdir():
        if entry_path.is_symlink() or not entry_path.is_dir():
            errors.append(f"Codex plugin skills contains a non-skill entry: {entry_path.name}")
            continue
        actual_skill_names.add(entry_path.name)
        if not (entry_path / "SKILL.md").is_file():
            errors.append(f"Codex plugin skill is missing SKILL.md: {entry_path.name}")
    if actual_skill_names != expected_skill_names:
        errors.append("Codex plugin skill inventory does not match the canonical catalog")
    return errors


def _validate_legacy_marketplace(
    *,
    output_root: Path,
    marketplace_relative: Path,
    platform: str,
    expected_skill_names: set[str],
) -> tuple[list[str], Path | None]:
    """Validate a Copilot/Claude marketplace and its repository-relative source."""
    errors: list[str] = []
    marketplace_path = output_root / marketplace_relative
    try:
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [f"cannot read {platform} marketplace JSON: {exc}"], None
    if not isinstance(marketplace, dict):
        return [f"{platform} marketplace must be a JSON object"], None
    if marketplace.get("name") != MARKETPLACE_NAME:
        errors.append(f"{platform} marketplace name does not match the catalog")
    owner = marketplace.get("owner")
    if not isinstance(owner, dict) or owner.get("name") != "rodri-oliveira-dev":
        errors.append(f"{platform} marketplace requires the expected owner")
    plugins = marketplace.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        errors.append(f"{platform} marketplace must contain exactly one plugin entry")
        return errors, None
    entry = plugins[0]
    if not isinstance(entry, dict):
        return [*errors, f"{platform} marketplace plugin entry must be an object"], None
    expected_entry = {
        "name": PLUGIN_NAME,
        "description": PLUGIN_DESCRIPTION,
        "version": PLUGIN_VERSION,
    }
    for field, expected in expected_entry.items():
        if entry.get(field) != expected:
            errors.append(f"{platform} marketplace plugin has invalid {field!r}")
    source = entry.get("source")
    if not isinstance(source, str) or not source.startswith("./"):
        errors.append(f"{platform} marketplace source must start with './'")
        return errors, None
    relative_source = Path(source)
    if relative_source.is_absolute() or ".." in relative_source.parts:
        errors.append(f"{platform} marketplace source must remain inside its root")
        return errors, None
    marketplace_root = output_root.resolve()
    resolved_plugin = (output_root / relative_source).resolve()
    if marketplace_root != resolved_plugin and marketplace_root not in resolved_plugin.parents:
        errors.append(f"{platform} marketplace source escapes its root")
        return errors, None
    if resolved_plugin != (output_root / PLUGIN_RELATIVE).resolve():
        errors.append(f"{platform} marketplace source resolves to the wrong plugin")
    if not resolved_plugin.is_dir():
        errors.append(f"{platform} marketplace source does not resolve to a plugin directory")
        return errors, None
    skills_root = resolved_plugin / "skills"
    if not skills_root.is_dir() or skills_root.is_symlink():
        errors.append(f"{platform} plugin skills path must be a regular directory")
        return errors, resolved_plugin
    actual_skill_names = {
        path.name
        for path in skills_root.iterdir()
        if path.is_dir() and not path.is_symlink() and (path / "SKILL.md").is_file()
    }
    if actual_skill_names != expected_skill_names:
        errors.append(f"{platform} plugin skill inventory does not match the canonical catalog")
    return errors, resolved_plugin


def validate_copilot_distribution(
    *, output_root: Path, expected_skill_names: set[str]
) -> list[str]:
    """Validate the Copilot marketplace and Agent Plugins package contract."""
    errors, package = _validate_legacy_marketplace(
        output_root=output_root,
        marketplace_relative=Path(".github/plugin/marketplace.json"),
        platform="Copilot",
        expected_skill_names=expected_skill_names,
    )
    if package is None:
        return errors
    try:
        manifest = json.loads((package / "plugin.json").read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [*errors, f"cannot read Copilot portable plugin manifest JSON: {exc}"]
    if not isinstance(manifest, dict):
        return [*errors, "Copilot portable plugin manifest must be a JSON object"]
    if manifest.get("$schema") != AGENT_PLUGINS_SCHEMA:
        errors.append("Copilot plugin does not declare Agent Plugins 1.0")
    if manifest.get("name") != PLUGIN_NAME:
        errors.append("Copilot portable plugin name does not match the marketplace")
    if (output_root / ".github" / "copilot-instructions.md").exists():
        errors.append("Copilot distribution must not add global repository instructions")
    return errors


def validate_claude_distribution(
    *, output_root: Path, expected_skill_names: set[str]
) -> list[str]:
    """Validate the Claude marketplace and its compatibility manifest."""
    errors, package = _validate_legacy_marketplace(
        output_root=output_root,
        marketplace_relative=Path(".claude-plugin/marketplace.json"),
        platform="Claude",
        expected_skill_names=expected_skill_names,
    )
    if package is None:
        return errors
    manifest_path = package / ".claude-plugin" / "plugin.json"
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        return [*errors, f"cannot read Claude plugin manifest JSON: {exc}"]
    if not isinstance(manifest, dict):
        return [*errors, "Claude plugin manifest must be a JSON object"]
    expected_manifest = {
        "name": PLUGIN_NAME,
        "version": PLUGIN_VERSION,
        "description": PLUGIN_DESCRIPTION,
    }
    for field, expected in expected_manifest.items():
        if manifest.get(field) != expected:
            errors.append(f"Claude plugin manifest has invalid {field!r}")
    unused_fields = {
        "agents",
        "commands",
        "hooks",
        "mcpServers",
        "lspServers",
        "userConfig",
    }
    for field in sorted(unused_fields & set(manifest)):
        errors.append(f"Claude plugin manifest declares unused component: {field}")
    for forbidden in ("commands", "hooks", "agents", ".mcp.json", ".lsp.json"):
        if _path_exists(package / forbidden):
            errors.append(f"Claude plugin contains unsupported unused component: {forbidden}")
    return errors


def check_distribution(*, catalog: Path, output_root: Path) -> list[str]:
    """Compare generated output with the canonical catalog and generator metadata."""
    expected = expected_distribution(catalog)
    errors: list[str] = []
    output_directories = {
        (output_root / Path(relative)).parent for relative in expected
    }
    for directory in sorted(output_directories, key=lambda path: str(path)):
        try:
            _validate_safe_output_directory(output_root, directory)
        except PackageError as exc:
            errors.append(str(exc))
    for relative, content in expected.items():
        target = output_root / Path(relative)
        if not target.is_file() or target.is_symlink():
            errors.append(f"missing generated file: {relative}")
        elif target.read_bytes() != content:
            errors.append(f"generated file is stale or modified: {relative}")
    package = output_root / PLUGIN_RELATIVE
    if _path_exists(package):
        try:
            actual_package = _regular_files(package)
        except PackageError as exc:
            errors.append(str(exc))
        else:
            expected_package = {
                Path(relative).relative_to(PLUGIN_RELATIVE).as_posix()
                for relative in expected
                if Path(relative).is_relative_to(PLUGIN_RELATIVE)
            }
            for extra in sorted(set(actual_package) - expected_package):
                errors.append(f"unexpected generated package file: {extra}")
    expected_skill_names = {
        path.name for path in catalog.iterdir() if path.is_dir() and not path.is_symlink()
    }
    errors.extend(
        validate_codex_distribution(
            output_root=output_root, expected_skill_names=expected_skill_names
        )
    )
    errors.extend(
        validate_copilot_distribution(
            output_root=output_root, expected_skill_names=expected_skill_names
        )
    )
    errors.extend(
        validate_claude_distribution(
            output_root=output_root, expected_skill_names=expected_skill_names
        )
    )
    return errors


def _write_files(root: Path, files: dict[str, bytes]) -> None:
    for relative, content in files.items():
        target = root / Path(relative)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def generate_distribution(*, catalog: Path, output_root: Path) -> None:
    """Regenerate package and marketplace manifests after verifying old output."""
    expected = expected_distribution(catalog)
    output_directories = {
        (output_root / Path(relative)).parent for relative in expected
    }
    for directory in sorted(output_directories, key=lambda path: str(path)):
        _validate_safe_output_directory(output_root, directory)
    _validate_safe_output_directory(output_root, output_root)
    output_root.mkdir(parents=True, exist_ok=True)
    package = output_root / PLUGIN_RELATIVE
    if _path_exists(package):
        if package.is_symlink() or not package.is_dir():
            raise PackageError(f"generated package path is not a regular directory: {package}")
        errors = verify_package(package)
        if errors:
            joined = "; ".join(errors)
            raise PackageError(f"refusing to replace modified generated package: {joined}")

    _validate_safe_output_directory(output_root, package.parent)
    package.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(tempfile.mkdtemp(prefix=f".{PLUGIN_NAME}-", dir=package.parent))
    backup = package.parent / f".{PLUGIN_NAME}.previous"
    package_prefix = f"{PLUGIN_RELATIVE.as_posix()}/"
    package_files = {
        relative.removeprefix(package_prefix): content
        for relative, content in expected.items()
        if relative.startswith(package_prefix)
    }
    try:
        _write_files(temporary, package_files)
        temporary_errors = verify_package(temporary)
        if temporary_errors:
            raise PackageError(
                "generated temporary package failed verification: "
                + "; ".join(temporary_errors)
            )
        if _path_exists(backup):
            raise PackageError(f"stale package backup requires review: {backup}")
        if _path_exists(package):
            os.replace(package, backup)
        try:
            os.replace(temporary, package)
        except BaseException:
            if _path_exists(backup) and not _path_exists(package):
                os.replace(backup, package)
            raise
        if _path_exists(backup):
            shutil.rmtree(backup)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)

    for relative, content in expected.items():
        if relative.startswith(package_prefix):
            continue
        target = output_root / Path(relative)
        _validate_safe_output_directory(output_root, target.parent)
        target.parent.mkdir(parents=True, exist_ok=True)
        _validate_safe_output_directory(output_root, target.parent)
        descriptor, temporary_name = tempfile.mkstemp(
            prefix=f".{target.name}-", dir=target.parent
        )
        try:
            with os.fdopen(descriptor, "wb") as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
            os.replace(temporary_name, target)
        finally:
            if os.path.exists(temporary_name):
                os.unlink(temporary_name)


def _print_errors(errors: Iterable[str]) -> None:
    for error in errors:
        print(f"ERROR [distribution] {error}", file=sys.stderr)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Generate and verify plugin marketplace distributions."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("generate", "check"):
        child = subparsers.add_parser(command)
        child.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG)
        child.add_argument("--output-root", type=Path, default=REPOSITORY_ROOT)
    verify = subparsers.add_parser("verify")
    verify.add_argument(
        "--package", type=Path, default=REPOSITORY_ROOT / PLUGIN_RELATIVE
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.command == "generate":
            generate_distribution(
                catalog=arguments.catalog, output_root=arguments.output_root
            )
            print(f"Generated plugin {PLUGIN_NAME} {PLUGIN_VERSION}.")
            return 0
        if arguments.command == "check":
            errors = check_distribution(
                catalog=arguments.catalog, output_root=arguments.output_root
            )
        else:
            errors = verify_package(arguments.package)
    except (OSError, PackageError) as exc:
        print(f"ERROR [distribution] {exc}", file=sys.stderr)
        return 1
    if errors:
        _print_errors(errors)
        return 1
    print("Plugin distribution verified.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
