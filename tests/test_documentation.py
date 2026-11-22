from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIRECTORY = REPOSITORY_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from skill_validation import _link_targets  # noqa: E402

CANONICAL_SKILLS = {
    "api-design",
    "code-review",
    "commits",
    "debug",
    "deployment-readiness",
    "docs",
    "refactor",
    "security-review",
    "sql",
    "testing",
}


def documentation_files() -> list[Path]:
    root_files = [
        REPOSITORY_ROOT / name
        for name in (
            "README.md",
            "README.pt-BR.md",
            "CONTRIBUTING.md",
            "SECURITY.md",
            "THIRD_PARTY_NOTICES.md",
        )
    ]
    return root_files + sorted((REPOSITORY_ROOT / "docs").rglob("*.md"))


def heading_anchors(markdown: str) -> set[str]:
    anchors: set[str] = set()
    occurrences: dict[str, int] = {}
    for heading in re.findall(r"^#{1,6}\s+(.+?)\s*#*\s*$", markdown, re.MULTILINE):
        plain = re.sub(r"\[([^]]+)\]\([^)]+\)", r"\1", heading)
        plain = plain.replace("`", "").strip().lower()
        anchor = re.sub(r"[^\w\- ]", "", plain, flags=re.UNICODE).replace(" ", "-")
        count = occurrences.get(anchor, 0)
        occurrences[anchor] = count + 1
        anchors.add(anchor if count == 0 else f"{anchor}-{count}")
    return anchors


class DocumentationTests(unittest.TestCase):
    def test_local_markdown_links_and_fragments_resolve(self) -> None:
        repository = REPOSITORY_ROOT.resolve()
        for source in documentation_files():
            with self.subTest(source=source.relative_to(REPOSITORY_ROOT)):
                self.assertTrue(source.is_file(), f"missing documentation file: {source}")
                content = source.read_text(encoding="utf-8")
                for raw_target in _link_targets(content):
                    parsed = urlsplit(raw_target)
                    if parsed.scheme or parsed.netloc:
                        continue
                    local_part = unquote(parsed.path)
                    target = source if not local_part else source.parent / local_part
                    resolved = target.resolve()
                    self.assertTrue(
                        resolved == repository or repository in resolved.parents,
                        f"link escapes repository: {source} -> {raw_target}",
                    )
                    self.assertTrue(target.exists(), f"broken link: {source} -> {raw_target}")
                    if parsed.fragment and target.is_file() and target.suffix.lower() == ".md":
                        anchors = heading_anchors(target.read_text(encoding="utf-8"))
                        self.assertIn(
                            unquote(parsed.fragment).lower(),
                            anchors,
                            f"broken fragment: {source} -> {raw_target}",
                        )

    def test_every_skill_reference_is_directly_linked_from_its_skill(self) -> None:
        for skill_md in sorted((REPOSITORY_ROOT / ".agents" / "skills").glob("*/SKILL.md")):
            linked = {
                unquote(urlsplit(target).path)
                for target in _link_targets(skill_md.read_text(encoding="utf-8"))
                if unquote(urlsplit(target).path).startswith("references/")
            }
            references = {
                path.relative_to(skill_md.parent).as_posix()
                for path in skill_md.parent.glob("references/*.md")
            }
            with self.subTest(skill=skill_md.parent.name):
                self.assertEqual(references, linked)

    def test_english_and_portuguese_readmes_list_the_canonical_catalog(self) -> None:
        pattern = re.compile(r"^- `([a-z0-9-]+)`: ", re.MULTILINE)
        for name in ("README.md", "README.pt-BR.md"):
            with self.subTest(readme=name):
                listed = set(pattern.findall((REPOSITORY_ROOT / name).read_text(encoding="utf-8")))
                self.assertEqual(CANONICAL_SKILLS, listed)

    def test_readme_installer_examples_use_supported_options(self) -> None:
        required = {
            "--platform claude-code",
            "--destination .claude/skills",
            "--all",
            "--dry-run",
        }
        for name in ("README.md", "README.pt-BR.md"):
            with self.subTest(readme=name):
                content = (REPOSITORY_ROOT / name).read_text(encoding="utf-8")
                for option in required:
                    self.assertIn(option, content)
                self.assertNotIn("--scope", content)


if __name__ == "__main__":
    unittest.main()
