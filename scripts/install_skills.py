#!/usr/bin/env python3
"""Install generated platform distributions from the canonical skills catalog."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

if sys.version_info < (3, 11):
    print("ERROR [runtime] Python 3.11 or newer is required.", file=sys.stderr)
    raise SystemExit(2)

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CATALOG = REPOSITORY_ROOT / ".agents" / "skills"
MANIFEST_NAME = ".agentic-engineering-skills.json"
MANAGED_BY = "agentic-engineering-skills"
SCHEMA_VERSION = 1
SUPPORTED_PLATFORMS = ("claude-code",)
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CLAUDE_CODE_RESERVED_NAMES = {"anthropic-skills", "synced"}


class InstallError(Exception):
    """An installation cannot proceed without risking unmanaged data."""


@dataclass(frozen=True)
class FileOperation:
    action: str
    path: Path


@dataclass(frozen=True)
class InstallResult:
    operations: tuple[FileOperation, ...]

    @property
    def changed(self) -> bool:
        return bool(self.operations)


def _is_within(candidate: Path, boundary: Path) -> bool:
    try:
        candidate.relative_to(boundary)
        return True
    except ValueError:
        return False


def _safe_target(destination: Path, relative_path: Path) -> Path:
    if relative_path.is_absolute() or ".." in relative_path.parts:
        raise InstallError(f"unsafe relative path: {relative_path}")
    target = destination / relative_path
    resolved = target.resolve(strict=False)
    if not _is_within(resolved, destination):
        raise InstallError(f"path escapes destination directory: {relative_path}")
    return target


def _assert_safe_parents(destination: Path, target: Path) -> None:
    parent = target.parent
    while parent != destination:
        if not _is_within(parent.resolve(strict=False), destination):
            raise InstallError(f"path escapes destination directory: {target}")
        if _path_exists(parent) and (parent.is_symlink() or not parent.is_dir()):
            raise InstallError(f"destination parent is not a regular directory: {parent}")
        parent = parent.parent


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _path_exists(path: Path) -> bool:
    """Treat broken symlinks as existing paths that must not be replaced."""
    return path.exists() or path.is_symlink()


def _source_files(skill_directory: Path) -> dict[str, Path]:
    boundary = skill_directory.resolve()
    files: dict[str, Path] = {}
    for current, directories, filenames in os.walk(skill_directory, followlinks=False):
        current_path = Path(current)
        for directory in list(directories):
            candidate = current_path / directory
            if candidate.is_symlink():
                raise InstallError(
                    f"source skill contains a symlinked directory: {candidate}"
                )
        for filename in filenames:
            candidate = current_path / filename
            if candidate.is_symlink():
                raise InstallError(f"source skill contains a symlinked file: {candidate}")
            if not candidate.is_file():
                raise InstallError(f"source skill contains a non-regular file: {candidate}")
            resolved = candidate.resolve()
            if not _is_within(resolved, boundary):
                raise InstallError(f"source file escapes skill directory: {candidate}")
            relative = candidate.relative_to(skill_directory).as_posix()
            files[relative] = candidate
    if "SKILL.md" not in files:
        raise InstallError(f"source skill is missing SKILL.md: {skill_directory.name}")
    return files


def _select_skills(catalog: Path, selected_skill: str | None) -> list[Path]:
    catalog = catalog.resolve()
    if not catalog.is_dir():
        raise InstallError(f"canonical catalog does not exist: {catalog}")

    if selected_skill is not None:
        if not SKILL_NAME.fullmatch(selected_skill):
            raise InstallError(
                "skill name must use lowercase ASCII letters, digits, and single hyphens"
            )
        if selected_skill in CLAUDE_CODE_RESERVED_NAMES:
            raise InstallError(f"skill name is reserved by Claude Code: {selected_skill}")
        skill = catalog / selected_skill
        if not skill.is_dir() or skill.is_symlink():
            raise InstallError(f"unknown canonical skill: {selected_skill}")
        if not _is_within(skill.resolve(), catalog):
            raise InstallError(f"skill escapes canonical catalog: {selected_skill}")
        return [skill]

    skills = [
        path
        for path in sorted(catalog.iterdir(), key=lambda item: item.name)
        if path.is_dir() and not path.is_symlink()
    ]
    if not skills:
        raise InstallError(f"canonical catalog is empty: {catalog}")
    for skill in skills:
        if not SKILL_NAME.fullmatch(skill.name):
            raise InstallError(f"invalid canonical skill directory name: {skill.name}")
        if skill.name in CLAUDE_CODE_RESERVED_NAMES:
            raise InstallError(f"skill name is reserved by Claude Code: {skill.name}")
    return skills


def _empty_manifest(platform: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "managed_by": MANAGED_BY,
        "platform": platform,
        "skills": {},
    }


def _validate_manifest_file_path(skill_name: str, value: object) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise InstallError(f"manifest contains an invalid path for skill {skill_name!r}")
    path = Path(value)
    if path.is_absolute() or ".." in path.parts or path.as_posix() != value:
        raise InstallError(f"manifest contains an unsafe path for skill {skill_name!r}: {value!r}")
    return value


def _load_manifest(destination: Path, platform: str) -> dict[str, Any]:
    manifest_path = destination / MANIFEST_NAME
    if not _path_exists(manifest_path):
        return _empty_manifest(platform)
    if manifest_path.is_symlink() or not manifest_path.is_file():
        raise InstallError(f"managed manifest is not a regular file: {manifest_path}")
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise InstallError(f"cannot read managed manifest {manifest_path}: {exc}") from exc
    if not isinstance(manifest, dict):
        raise InstallError(f"managed manifest must be a JSON object: {manifest_path}")
    allowed_keys = {"schema_version", "managed_by", "platform", "skills"}
    if set(manifest) != allowed_keys:
        raise InstallError(
            f"managed manifest must contain exactly: {', '.join(sorted(allowed_keys))}"
        )
    expected = {
        "schema_version": SCHEMA_VERSION,
        "managed_by": MANAGED_BY,
        "platform": platform,
    }
    for key, value in expected.items():
        if manifest.get(key) != value:
            raise InstallError(
                f"managed manifest has unsupported {key!r}: {manifest.get(key)!r}"
            )
    skills = manifest.get("skills")
    if not isinstance(skills, dict):
        raise InstallError("managed manifest field 'skills' must be an object")
    for skill_name, skill_record in skills.items():
        if not isinstance(skill_name, str) or not SKILL_NAME.fullmatch(skill_name):
            raise InstallError(f"managed manifest contains an invalid skill name: {skill_name!r}")
        if not isinstance(skill_record, dict) or set(skill_record) != {"files"}:
            raise InstallError(f"managed manifest has an invalid record for skill {skill_name!r}")
        files = skill_record["files"]
        if not isinstance(files, dict):
            raise InstallError(f"managed manifest files must be an object for skill {skill_name!r}")
        for relative, digest in files.items():
            _validate_manifest_file_path(skill_name, relative)
            if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-f]{64}", digest):
                raise InstallError(
                    f"managed manifest contains an invalid digest for {skill_name}/{relative}"
                )
    return manifest


def _render_manifest(manifest: dict[str, Any]) -> bytes:
    return (json.dumps(manifest, indent=2, sort_keys=True) + "\n").encode("utf-8")


def _assert_regular_destination_file(path: Path, relative: Path) -> None:
    if path.is_symlink() or not path.is_file():
        raise InstallError(f"managed path is not a regular file: {relative.as_posix()}")


def _atomic_copy(source: Path, target: Path, expected_digest: str) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".install-skills-", dir=target.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        shutil.copy2(source, temporary)
        if _sha256(temporary) != expected_digest:
            raise InstallError(f"source changed while copying: {source}")
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def _atomic_write(target: Path, content: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary_name = tempfile.mkstemp(prefix=".install-skills-", dir=target.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, target)
    finally:
        if temporary.exists():
            temporary.unlink()


def install_skills(
    *,
    catalog: Path,
    destination: Path,
    platform: str,
    selected_skill: str | None,
    dry_run: bool = False,
) -> InstallResult:
    """Synchronize selected canonical skills into a managed distribution."""
    if platform not in SUPPORTED_PLATFORMS:
        raise InstallError(f"unsupported platform: {platform}")

    destination = destination.expanduser().resolve(strict=False)
    if destination.exists() and (destination.is_symlink() or not destination.is_dir()):
        raise InstallError(f"destination is not a regular directory: {destination}")

    selected = _select_skills(catalog, selected_skill)
    manifest = _load_manifest(destination, platform)
    updated_manifest = json.loads(json.dumps(manifest))
    operations: list[FileOperation] = []
    copies: list[tuple[Path, Path, str]] = []
    removals: list[Path] = []

    for skill_directory in selected:
        skill_name = skill_directory.name
        relative_skill = Path(skill_name)
        target_skill = _safe_target(destination, relative_skill)
        existing_record = manifest["skills"].get(skill_name)
        if existing_record is None and _path_exists(target_skill):
            raise InstallError(
                f"refusing to replace unmanaged skill directory: {target_skill}"
            )
        if _path_exists(target_skill) and (
            target_skill.is_symlink() or not target_skill.is_dir()
        ):
            raise InstallError(f"managed skill path is not a regular directory: {target_skill}")

        sources = _source_files(skill_directory)
        source_hashes = {relative: _sha256(path) for relative, path in sources.items()}
        old_hashes: dict[str, str] = existing_record["files"] if existing_record else {}

        for relative, source in sources.items():
            relative_path = relative_skill / Path(relative)
            target = _safe_target(destination, relative_path)
            _assert_safe_parents(destination, target)
            source_digest = source_hashes[relative]
            old_digest = old_hashes.get(relative)
            if _path_exists(target):
                _assert_regular_destination_file(target, relative_path)
                current_digest = _sha256(target)
                if old_digest is None:
                    raise InstallError(
                        f"refusing to overwrite unmanaged file: {relative_path.as_posix()}"
                    )
                if current_digest not in {old_digest, source_digest}:
                    raise InstallError(
                        f"managed file was modified locally: {relative_path.as_posix()}"
                    )
                if current_digest == source_digest:
                    continue
                action = "update"
            else:
                action = "create"
            copies.append((source, target, source_digest))
            operations.append(FileOperation(action, relative_path))

        for relative, old_digest in old_hashes.items():
            if relative in sources:
                continue
            relative_path = relative_skill / Path(relative)
            target = _safe_target(destination, relative_path)
            _assert_safe_parents(destination, target)
            if not _path_exists(target):
                continue
            _assert_regular_destination_file(target, relative_path)
            if _sha256(target) != old_digest:
                raise InstallError(
                    f"obsolete managed file was modified locally: {relative_path.as_posix()}"
                )
            removals.append(target)
            operations.append(FileOperation("remove", relative_path))

        updated_manifest["skills"][skill_name] = {"files": source_hashes}

    manifest_path = destination / MANIFEST_NAME
    manifest_content = _render_manifest(updated_manifest)
    current_manifest_content = manifest_path.read_bytes() if _path_exists(manifest_path) else None
    if current_manifest_content != manifest_content:
        operations.append(FileOperation("write-manifest", Path(MANIFEST_NAME)))

    if dry_run:
        return InstallResult(tuple(operations))

    for source, target, digest in copies:
        _atomic_copy(source, target, digest)
    for target in removals:
        target.unlink()
    if current_manifest_content != manifest_content:
        _atomic_write(manifest_path, manifest_content)
    return InstallResult(tuple(operations))


def uninstall_skills(
    *,
    destination: Path,
    platform: str,
    selected_skill: str | None,
    dry_run: bool = False,
) -> InstallResult:
    """Remove only intact files recorded in the managed distribution manifest."""
    if platform not in SUPPORTED_PLATFORMS:
        raise InstallError(f"unsupported platform: {platform}")
    if selected_skill is not None and not SKILL_NAME.fullmatch(selected_skill):
        raise InstallError(
            "skill name must use lowercase ASCII letters, digits, and single hyphens"
        )

    destination = destination.expanduser().resolve(strict=False)
    if not destination.exists():
        return InstallResult(())
    if destination.is_symlink() or not destination.is_dir():
        raise InstallError(f"destination is not a regular directory: {destination}")

    manifest_path = destination / MANIFEST_NAME
    if not _path_exists(manifest_path):
        return InstallResult(())
    manifest = _load_manifest(destination, platform)
    managed_names = sorted(manifest["skills"])
    names = [selected_skill] if selected_skill is not None else managed_names
    names = [name for name in names if name in manifest["skills"]]
    operations: list[FileOperation] = []
    targets_to_remove: list[Path] = []
    updated_manifest = json.loads(json.dumps(manifest))

    for skill_name in names:
        skill_path = _safe_target(destination, Path(skill_name))
        tracked: dict[str, str] = manifest["skills"][skill_name]["files"]
        if _path_exists(skill_path):
            if skill_path.is_symlink() or not skill_path.is_dir():
                raise InstallError(f"managed skill path is not a regular directory: {skill_path}")
            tracked_directories = {
                parent.as_posix()
                for relative in tracked
                for parent in Path(relative).parents
                if parent != Path(".")
            }
            for current, directories, filenames in os.walk(skill_path, followlinks=False):
                current_path = Path(current)
                for directory in directories:
                    candidate = current_path / directory
                    if candidate.is_symlink():
                        raise InstallError(
                            f"refusing to remove skill containing an untracked symlink: {candidate}"
                        )
                    relative_directory = candidate.relative_to(skill_path).as_posix()
                    if relative_directory not in tracked_directories:
                        raise InstallError(
                            f"refusing to remove skill containing an unmanaged directory: "
                            f"{skill_name}/{relative_directory}"
                        )
                for filename in filenames:
                    candidate = current_path / filename
                    relative = candidate.relative_to(skill_path).as_posix()
                    if relative not in tracked:
                        raise InstallError(
                            f"refusing to remove skill containing an unmanaged file: "
                            f"{skill_name}/{relative}"
                        )
                    _assert_regular_destination_file(candidate, Path(skill_name) / relative)
                    if _sha256(candidate) != tracked[relative]:
                        raise InstallError(
                            f"managed file was modified locally: {skill_name}/{relative}"
                        )
            targets_to_remove.append(skill_path)
            operations.append(FileOperation("remove-skill", Path(skill_name)))
        del updated_manifest["skills"][skill_name]

    remove_manifest = not updated_manifest["skills"]
    if names:
        operations.append(
            FileOperation(
                "remove-manifest" if remove_manifest else "write-manifest",
                Path(MANIFEST_NAME),
            )
        )
    if dry_run:
        return InstallResult(tuple(operations))

    for skill_path in targets_to_remove:
        for current, directories, filenames in os.walk(skill_path, topdown=False):
            current_path = Path(current)
            for filename in filenames:
                (current_path / filename).unlink()
            for directory in directories:
                (current_path / directory).rmdir()
        skill_path.rmdir()
    if names:
        if remove_manifest:
            manifest_path.unlink()
        else:
            _atomic_write(manifest_path, _render_manifest(updated_manifest))
    return InstallResult(tuple(operations))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=(
            "Install generated platform distributions from the canonical .agents/skills catalog."
        )
    )
    parser.add_argument(
        "--platform",
        required=True,
        choices=SUPPORTED_PLATFORMS,
        help="target agent platform",
    )
    parser.add_argument(
        "--destination",
        required=True,
        type=Path,
        help="target skills directory, such as .claude/skills",
    )
    selection = parser.add_mutually_exclusive_group(required=True)
    selection.add_argument("--all", action="store_true", help="install every canonical skill")
    selection.add_argument("--skill", metavar="NAME", help="install one canonical skill")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="show planned changes without writing files",
    )
    parser.add_argument(
        "--uninstall",
        action="store_true",
        help="safely remove intact files recorded in the managed manifest",
    )
    return parser


def _render_operations(operations: Iterable[FileOperation], *, dry_run: bool) -> None:
    prefix = "Would" if dry_run else "Did"
    count = 0
    for operation in operations:
        print(f"{prefix} {operation.action}: {operation.path.as_posix()}")
        count += 1
    if count == 0:
        print("No changes required.")


def main(argv: list[str] | None = None) -> int:
    arguments = build_parser().parse_args(argv)
    try:
        if arguments.uninstall:
            result = uninstall_skills(
                destination=arguments.destination,
                platform=arguments.platform,
                selected_skill=arguments.skill,
                dry_run=arguments.dry_run,
            )
        else:
            result = install_skills(
                catalog=DEFAULT_CATALOG,
                destination=arguments.destination,
                platform=arguments.platform,
                selected_skill=arguments.skill,
                dry_run=arguments.dry_run,
            )
    except InstallError as exc:
        print(f"ERROR [installation] {exc}", file=sys.stderr)
        return 1
    except OSError as exc:
        print(f"ERROR [filesystem] {exc}", file=sys.stderr)
        return 1
    _render_operations(result.operations, dry_run=arguments.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
