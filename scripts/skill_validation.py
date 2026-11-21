"""Structural validation for the repository's Agent Skills catalog."""

from __future__ import annotations

import os
import re
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit

import yaml

ALLOWED_FIELDS = {
    "name",
    "description",
    "license",
    "compatibility",
    "metadata",
    "allowed-tools",
}
MAX_NAME_LENGTH = 64
MAX_DESCRIPTION_LENGTH = 1024
MAX_COMPATIBILITY_LENGTH = 500
ASCII_KEBAB_CASE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
INLINE_LINK = re.compile(
    r"!?\[[^\]]*\]\(\s*(?:<(?P<angle>[^>]+)>|(?P<plain>[^\s)]+))"
)
REFERENCE_LINK = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*(?:<(?P<angle>[^>]+)>|(?P<plain>\S+))", re.MULTILINE)
EXTERNAL_SCHEMES = {"http", "https", "mailto"}


class UniqueKeyLoader(yaml.SafeLoader):
    """Safe YAML loader that rejects duplicate mapping keys."""


def _construct_unique_mapping(
    loader: UniqueKeyLoader, node: yaml.nodes.MappingNode, deep: bool = False
) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in mapping
        except TypeError as exc:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                "found an unhashable mapping key",
                key_node.start_mark,
            ) from exc
        if duplicate:
            raise yaml.constructor.ConstructorError(
                "while constructing a mapping",
                node.start_mark,
                f"found duplicate key {key!r}",
                key_node.start_mark,
            )
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping
)


@dataclass(frozen=True)
class Issue:
    severity: str
    category: str
    path: Path
    message: str

    def format(self, root: Path) -> str:
        try:
            display_path = self.path.relative_to(root)
        except ValueError:
            display_path = self.path
        return f"{self.severity.upper()} [{self.category}] {display_path}: {self.message}"


@dataclass
class SkillResult:
    directory: Path
    name: str | None = None
    issues: list[Issue] = field(default_factory=list)


@dataclass
class CatalogReport:
    root: Path
    skills: list[SkillResult] = field(default_factory=list)
    catalog_issues: list[Issue] = field(default_factory=list)
    empty_catalog: bool = False

    @property
    def issues(self) -> list[Issue]:
        return self.catalog_issues + [issue for skill in self.skills for issue in skill.issues]

    @property
    def errors(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "error"]

    @property
    def warnings(self) -> list[Issue]:
        return [issue for issue in self.issues if issue.severity == "warning"]


def _issue(
    issues: list[Issue], severity: str, category: str, path: Path, message: str
) -> None:
    issues.append(Issue(severity, category, path, message))


def _is_within(candidate: Path, boundary: Path) -> bool:
    try:
        candidate.relative_to(boundary)
        return True
    except ValueError:
        return False


def _parse_skill_md(skill_md: Path, issues: list[Issue]) -> tuple[dict[str, Any] | None, str]:
    try:
        content = skill_md.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        _issue(issues, "error", "structure", skill_md, f"cannot read UTF-8 content: {exc}")
        return None, ""

    lines = content.splitlines()
    if not lines or lines[0] != "---":
        _issue(
            issues,
            "error",
            "specification",
            skill_md,
            "SKILL.md must start with a YAML frontmatter delimiter ('---')",
        )
        return None, ""

    try:
        closing_index = lines.index("---", 1)
    except ValueError:
        _issue(
            issues,
            "error",
            "specification",
            skill_md,
            "YAML frontmatter is missing its closing '---' delimiter",
        )
        return None, ""

    yaml_text = "\n".join(lines[1:closing_index])
    body = "\n".join(lines[closing_index + 1 :]).strip()
    try:
        metadata = yaml.load(yaml_text, Loader=UniqueKeyLoader)
    except yaml.YAMLError as exc:
        problem = getattr(exc, "problem", None) or str(exc).splitlines()[0]
        mark = getattr(exc, "problem_mark", None)
        location = f" at frontmatter line {mark.line + 2}, column {mark.column + 1}" if mark else ""
        _issue(issues, "error", "specification", skill_md, f"invalid YAML{location}: {problem}")
        return None, body

    if not isinstance(metadata, dict):
        _issue(
            issues,
            "error",
            "specification",
            skill_md,
            "YAML frontmatter must be a mapping of field names to values",
        )
        return None, body

    if not body:
        _issue(
            issues,
            "error",
            "specification",
            skill_md,
            "SKILL.md must contain Markdown instructions after the frontmatter",
        )
    return metadata, body


def _validate_metadata(
    metadata: dict[str, Any], skill_dir: Path, skill_md: Path, issues: list[Issue]
) -> str | None:
    non_string_keys = [key for key in metadata if not isinstance(key, str)]
    if non_string_keys:
        _issue(
            issues,
            "error",
            "specification",
            skill_md,
            "frontmatter field names must be strings",
        )

    extra_fields = sorted(
        (key for key in metadata if isinstance(key, str) and key not in ALLOWED_FIELDS)
    )
    if extra_fields:
        _issue(
            issues,
            "error",
            "specification",
            skill_md,
            f"unsupported frontmatter field(s): {', '.join(extra_fields)}",
        )

    name = metadata.get("name")
    normalized_name: str | None = None
    if not isinstance(name, str) or not name.strip():
        message = "missing required field 'name'" if "name" not in metadata else "field 'name' must be a non-empty string"
        _issue(issues, "error", "specification", skill_md, message)
    else:
        normalized_name = unicodedata.normalize("NFKC", name)
        if len(normalized_name) > MAX_NAME_LENGTH:
            _issue(
                issues,
                "error",
                "specification",
                skill_md,
                f"field 'name' exceeds {MAX_NAME_LENGTH} characters ({len(normalized_name)})",
            )
        if normalized_name != normalized_name.lower():
            _issue(issues, "error", "specification", skill_md, "field 'name' must be lowercase")
        if normalized_name.startswith("-") or normalized_name.endswith("-"):
            _issue(issues, "error", "specification", skill_md, "field 'name' cannot start or end with a hyphen")
        if "--" in normalized_name:
            _issue(issues, "error", "specification", skill_md, "field 'name' cannot contain consecutive hyphens")
        if not all(character.isalnum() or character == "-" for character in normalized_name):
            _issue(
                issues,
                "error",
                "specification",
                skill_md,
                "field 'name' may contain only lowercase alphanumeric characters and hyphens",
            )
        if unicodedata.normalize("NFKC", skill_dir.name) != normalized_name:
            _issue(
                issues,
                "error",
                "specification",
                skill_md,
                f"field 'name' ({name!r}) must match parent directory ({skill_dir.name!r})",
            )
        if not ASCII_KEBAB_CASE.fullmatch(name):
            _issue(
                issues,
                "warning",
                "project-convention",
                skill_md,
                "project skill names should use English ASCII kebab-case",
            )

    description = metadata.get("description")
    if not isinstance(description, str) or not description.strip():
        message = "missing required field 'description'" if "description" not in metadata else "field 'description' must be a non-empty string"
        _issue(issues, "error", "specification", skill_md, message)
    elif len(description) > MAX_DESCRIPTION_LENGTH:
        _issue(
            issues,
            "error",
            "specification",
            skill_md,
            f"field 'description' exceeds {MAX_DESCRIPTION_LENGTH} characters ({len(description)})",
        )

    compatibility = metadata.get("compatibility")
    if "compatibility" in metadata:
        if not isinstance(compatibility, str) or not compatibility:
            _issue(issues, "error", "specification", skill_md, "field 'compatibility' must be a non-empty string")
        elif len(compatibility) > MAX_COMPATIBILITY_LENGTH:
            _issue(
                issues,
                "error",
                "specification",
                skill_md,
                f"field 'compatibility' exceeds {MAX_COMPATIBILITY_LENGTH} characters ({len(compatibility)})",
            )

    if "license" in metadata and (not isinstance(metadata["license"], str) or not metadata["license"].strip()):
        _issue(issues, "error", "specification", skill_md, "field 'license' must be a non-empty string")
    if "allowed-tools" in metadata and not isinstance(metadata["allowed-tools"], str):
        _issue(issues, "error", "specification", skill_md, "field 'allowed-tools' must be a string")
    if "metadata" in metadata:
        nested = metadata["metadata"]
        if not isinstance(nested, dict) or any(
            not isinstance(key, str) or not isinstance(value, str) for key, value in getattr(nested, "items", lambda: [])()
        ):
            _issue(
                issues,
                "error",
                "specification",
                skill_md,
                "field 'metadata' must be a mapping of string keys to string values",
            )

    return normalized_name


def _markdown_files(skill_dir: Path, issues: list[Issue]) -> Iterable[Path]:
    boundary = skill_dir.resolve()
    for current, directories, files in os.walk(skill_dir, followlinks=False):
        current_path = Path(current)
        safe_directories: list[str] = []
        for directory in directories:
            candidate = current_path / directory
            resolved = candidate.resolve()
            if candidate.is_symlink() and not _is_within(resolved, boundary):
                _issue(
                    issues,
                    "error",
                    "security",
                    candidate,
                    "symlinked directory escapes the skill directory",
                )
            elif not candidate.is_symlink():
                safe_directories.append(directory)
        directories[:] = safe_directories

        for filename in files:
            candidate = current_path / filename
            if candidate.suffix.lower() != ".md":
                continue
            resolved = candidate.resolve()
            if not _is_within(resolved, boundary):
                _issue(
                    issues,
                    "error",
                    "security",
                    candidate,
                    "symlinked Markdown file escapes the skill directory",
                )
                continue
            yield candidate


def _link_targets(content: str) -> Iterable[str]:
    for pattern in (INLINE_LINK, REFERENCE_LINK):
        for match in pattern.finditer(content):
            yield match.group("angle") or match.group("plain")


def _validate_local_links(skill_dir: Path, issues: list[Issue]) -> None:
    boundary = skill_dir.resolve()
    for markdown_file in _markdown_files(skill_dir, issues):
        try:
            content = markdown_file.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as exc:
            _issue(issues, "error", "structure", markdown_file, f"cannot read UTF-8 content: {exc}")
            continue

        for raw_target in _link_targets(content):
            target = raw_target.strip()
            if not target or target.startswith("#"):
                continue
            try:
                parsed = urlsplit(target)
            except ValueError as exc:
                _issue(issues, "error", "structure", markdown_file, f"invalid link target {target!r}: {exc}")
                continue
            if parsed.scheme.lower() in EXTERNAL_SCHEMES or parsed.netloc:
                continue
            if parsed.scheme:
                if parsed.scheme.lower() == "file" or len(parsed.scheme) == 1:
                    _issue(
                        issues,
                        "error",
                        "security",
                        markdown_file,
                        f"local link must be relative, not absolute: {target!r}",
                    )
                continue

            local_part = unquote(parsed.path)
            if not local_part:
                continue
            if "\\" in local_part:
                _issue(
                    issues,
                    "error",
                    "structure",
                    markdown_file,
                    f"local link must use portable forward slashes: {target!r}",
                )
                continue
            local_path = Path(local_part)
            if local_path.is_absolute() or local_part.startswith(("/", "\\")):
                _issue(
                    issues,
                    "error",
                    "security",
                    markdown_file,
                    f"local link must be relative: {target!r}",
                )
                continue

            resolved = (markdown_file.parent / local_path).resolve()
            if not _is_within(resolved, boundary):
                _issue(
                    issues,
                    "error",
                    "security",
                    markdown_file,
                    f"local link escapes the skill directory: {target!r}",
                )
            elif not resolved.exists():
                _issue(
                    issues,
                    "error",
                    "structure",
                    markdown_file,
                    f"local link target does not exist: {target!r}",
                )


def validate_skill(skill_dir: Path, catalog_root: Path) -> SkillResult:
    result = SkillResult(directory=skill_dir)
    resolved_dir = skill_dir.resolve()
    if not _is_within(resolved_dir, catalog_root):
        _issue(
            result.issues,
            "error",
            "security",
            skill_dir,
            "skill directory resolves outside the catalog root",
        )
        return result

    skill_md = skill_dir / "SKILL.md"
    if not skill_md.is_file():
        _issue(
            result.issues,
            "error",
            "specification",
            skill_dir,
            "missing required file SKILL.md",
        )
        return result
    if not _is_within(skill_md.resolve(), resolved_dir):
        _issue(
            result.issues,
            "error",
            "security",
            skill_md,
            "SKILL.md resolves outside the skill directory",
        )
        return result

    metadata, _ = _parse_skill_md(skill_md, result.issues)
    if metadata is not None:
        result.name = _validate_metadata(metadata, skill_dir, skill_md, result.issues)
    _validate_local_links(skill_dir, result.issues)
    return result


def validate_catalog(
    catalog_root: Path, selected_skill: str | None = None, require_skills: bool = False
) -> CatalogReport:
    root = catalog_root.resolve()
    report = CatalogReport(root=root)

    if selected_skill is not None and (
        not selected_skill
        or selected_skill in {".", ".."}
        or Path(selected_skill).name != selected_skill
        or "/" in selected_skill
        or "\\" in selected_skill
    ):
        _issue(
            report.catalog_issues,
            "error",
            "security",
            root,
            "--skill must be a direct child directory name, not a path",
        )
        return report

    if not root.exists():
        if selected_skill is not None:
            _issue(report.catalog_issues, "error", "structure", root, "catalog directory does not exist")
            return report
        report.empty_catalog = True
    elif not root.is_dir():
        _issue(report.catalog_issues, "error", "structure", root, "catalog root is not a directory")
        return report
    else:
        candidates = sorted((path for path in root.iterdir() if path.is_dir()), key=lambda path: path.name)
        if selected_skill is not None:
            candidates = [path for path in candidates if path.name == selected_skill]
            if not candidates:
                _issue(
                    report.catalog_issues,
                    "error",
                    "structure",
                    root / selected_skill,
                    f"skill {selected_skill!r} was not found in the catalog",
                )
                return report
        if not candidates:
            report.empty_catalog = True
        for candidate in candidates:
            report.skills.append(validate_skill(candidate, root))

    if report.empty_catalog and require_skills:
        _issue(
            report.catalog_issues,
            "error",
            "structure",
            root,
            "catalog is empty but --require-skills was specified",
        )

    names: dict[str, list[SkillResult]] = {}
    for skill in report.skills:
        if skill.name:
            names.setdefault(skill.name, []).append(skill)
    for name, duplicates in names.items():
        if len(duplicates) > 1:
            locations = ", ".join(skill.directory.name for skill in duplicates)
            for skill in duplicates:
                _issue(
                    skill.issues,
                    "error",
                    "specification",
                    skill.directory / "SKILL.md",
                    f"duplicate skill name {name!r} appears in: {locations}",
                )

    return report
