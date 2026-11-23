from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIRECTORY = REPOSITORY_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS_DIRECTORY))

from package_plugins import (  # noqa: E402
    AGENT_PLUGINS_SCHEMA,
    DEFAULT_CATALOG,
    INVENTORY_NAME,
    PLUGIN_NAME,
    PLUGIN_RELATIVE,
    PackageError,
    check_distribution,
    generate_distribution,
    validate_claude_distribution,
    validate_codex_distribution,
    validate_copilot_distribution,
    verify_package,
)


def write_skill(catalog: Path, name: str, files: dict[str, bytes] | None = None) -> None:
    skill = catalog / name
    skill.mkdir(parents=True)
    contents = {
        "SKILL.md": (
            f"---\nname: {name}\ndescription: Test {name}. Use for tests.\n"
            f"---\n\n# {name}\n"
        ).encode(),
        **(files or {}),
    }
    for relative, content in contents.items():
        target = skill / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)


def snapshot(root: Path) -> dict[str, bytes]:
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }


class PackagePluginTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary_directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary_directory.cleanup)
        self.root = Path(self.temporary_directory.name)
        self.catalog = self.root / "canonical"
        self.catalog.mkdir()
        write_skill(
            self.catalog,
            "code-review",
            {
                "references/checks.md": b"# Checks\n",
                "assets/template.txt": b"template\x00bytes\n",
            },
        )
        write_skill(self.catalog, "testing")

    def test_generates_portable_and_legacy_manifests_with_complete_skills(self) -> None:
        output = self.root / "output"

        generate_distribution(catalog=self.catalog, output_root=output)

        package = output / PLUGIN_RELATIVE
        portable = json.loads((package / "plugin.json").read_text(encoding="utf-8"))
        claude = json.loads(
            (package / ".claude-plugin/plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(AGENT_PLUGINS_SCHEMA, portable["$schema"])
        self.assertEqual(PLUGIN_NAME, portable["name"])
        self.assertNotIn("skills", portable)
        self.assertNotIn("extensions", portable)
        self.assertNotIn("$schema", claude)
        self.assertEqual(
            b"template\x00bytes\n",
            (package / "skills/code-review/assets/template.txt").read_bytes(),
        )
        openai_marketplace = json.loads(
            (output / ".agents/plugins/marketplace.json").read_text(encoding="utf-8")
        )
        copilot_marketplace = json.loads(
            (output / ".github/plugin/marketplace.json").read_text(encoding="utf-8")
        )
        claude_marketplace = json.loads(
            (output / ".claude-plugin/marketplace.json").read_text(encoding="utf-8")
        )
        expected_source = f"./{PLUGIN_RELATIVE.as_posix()}"
        self.assertEqual(
            expected_source, openai_marketplace["plugins"][0]["source"]["path"]
        )
        self.assertEqual(
            {
                "installation": "AVAILABLE",
                "authentication": "ON_INSTALL",
            },
            openai_marketplace["plugins"][0]["policy"],
        )
        self.assertEqual(
            "Developer Tools", openai_marketplace["plugins"][0]["category"]
        )
        self.assertEqual(expected_source, copilot_marketplace["plugins"][0]["source"])
        self.assertEqual(expected_source, claude_marketplace["plugins"][0]["source"])
        self.assertEqual(
            package.resolve(), (output / Path(expected_source)).resolve()
        )
        for unused_component in ("mcp.json", ".mcp.json", "hooks", "agents", ".codex-plugin"):
            self.assertFalse((package / unused_component).exists())
        self.assertEqual(
            [],
            validate_codex_distribution(
                output_root=output, expected_skill_names={"code-review", "testing"}
            ),
        )
        self.assertEqual(
            [],
            validate_copilot_distribution(
                output_root=output, expected_skill_names={"code-review", "testing"}
            ),
        )
        self.assertEqual(
            [],
            validate_claude_distribution(
                output_root=output, expected_skill_names={"code-review", "testing"}
            ),
        )
        self.assertEqual([], verify_package(package))
        self.assertEqual([], check_distribution(catalog=self.catalog, output_root=output))

    def test_codex_validation_rejects_a_marketplace_path_outside_the_package(self) -> None:
        output = self.root / "output"
        generate_distribution(catalog=self.catalog, output_root=output)
        marketplace_path = output / ".agents/plugins/marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        marketplace["plugins"][0]["source"]["path"] = "./plugins/missing"
        marketplace_path.write_text(json.dumps(marketplace), encoding="utf-8")

        errors = validate_codex_distribution(
            output_root=output, expected_skill_names={"code-review", "testing"}
        )

        self.assertIn("Codex marketplace source.path resolves to the wrong plugin", errors)
        self.assertIn(
            "Codex marketplace source.path does not resolve to a plugin directory", errors
        )

    def test_copilot_validation_rejects_a_wrong_marketplace_path(self) -> None:
        output = self.root / "output"
        generate_distribution(catalog=self.catalog, output_root=output)
        marketplace_path = output / ".github/plugin/marketplace.json"
        marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
        marketplace["plugins"][0]["source"] = "./plugins/missing"
        marketplace_path.write_text(json.dumps(marketplace), encoding="utf-8")

        errors = validate_copilot_distribution(
            output_root=output, expected_skill_names={"code-review", "testing"}
        )

        self.assertIn("Copilot marketplace source resolves to the wrong plugin", errors)
        self.assertIn(
            "Copilot marketplace source does not resolve to a plugin directory", errors
        )

    def test_claude_validation_rejects_a_wrong_name_and_unused_component(self) -> None:
        output = self.root / "output"
        generate_distribution(catalog=self.catalog, output_root=output)
        package = output / PLUGIN_RELATIVE
        manifest_path = package / ".claude-plugin/plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["name"] = "wrong-name"
        manifest["hooks"] = "./hooks/hooks.json"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        errors = validate_claude_distribution(
            output_root=output, expected_skill_names={"code-review", "testing"}
        )

        self.assertIn("Claude plugin manifest has invalid 'name'", errors)
        self.assertIn("Claude plugin manifest declares unused component: hooks", errors)

    def test_marketplaces_keep_plugin_identity_and_description_consistent(self) -> None:
        output = self.root / "output"
        generate_distribution(catalog=self.catalog, output_root=output)
        paths = (
            ".agents/plugins/marketplace.json",
            ".github/plugin/marketplace.json",
            ".claude-plugin/marketplace.json",
        )
        marketplaces = [
            json.loads((output / path).read_text(encoding="utf-8")) for path in paths
        ]
        entries = [marketplace["plugins"][0] for marketplace in marketplaces]

        self.assertEqual(1, len({marketplace["name"] for marketplace in marketplaces}))
        self.assertEqual(1, len({entry["name"] for entry in entries}))
        self.assertEqual(1, len({entry["version"] for entry in entries}))
        self.assertEqual(1, len({entry["description"] for entry in entries}))

    def test_each_marketplace_rejects_malformed_json(self) -> None:
        validators = (
            (
                ".agents/plugins/marketplace.json",
                validate_codex_distribution,
                "cannot read Codex marketplace JSON",
            ),
            (
                ".github/plugin/marketplace.json",
                validate_copilot_distribution,
                "cannot read Copilot marketplace JSON",
            ),
            (
                ".claude-plugin/marketplace.json",
                validate_claude_distribution,
                "cannot read Claude marketplace JSON",
            ),
        )
        for relative, validator, expected_error in validators:
            with self.subTest(marketplace=relative):
                output = self.root / relative.split("/")[0].removeprefix(".")
                generate_distribution(catalog=self.catalog, output_root=output)
                (output / relative).write_text("{not-json", encoding="utf-8")

                errors = validator(
                    output_root=output,
                    expected_skill_names={"code-review", "testing"},
                )

                self.assertTrue(any(expected_error in error for error in errors))

    def test_marketplaces_require_platform_fields(self) -> None:
        cases = (
            (
                ".agents/plugins/marketplace.json",
                validate_codex_distribution,
                lambda value: value.pop("name"),
                "Codex marketplace requires a non-empty name",
            ),
            (
                ".github/plugin/marketplace.json",
                validate_copilot_distribution,
                lambda value: value.pop("owner"),
                "Copilot marketplace requires the expected owner",
            ),
            (
                ".claude-plugin/marketplace.json",
                validate_claude_distribution,
                lambda value: value["plugins"][0].pop("source"),
                "Claude marketplace source must start with './'",
            ),
        )
        for relative, validator, mutate, expected_error in cases:
            with self.subTest(marketplace=relative):
                output = self.root / ("required-" + relative.split("/")[0].removeprefix("."))
                generate_distribution(catalog=self.catalog, output_root=output)
                marketplace_path = output / relative
                marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
                mutate(marketplace)
                marketplace_path.write_text(json.dumps(marketplace), encoding="utf-8")

                errors = validator(
                    output_root=output,
                    expected_skill_names={"code-review", "testing"},
                )

                self.assertIn(expected_error, errors)

    def test_declared_agent_plugins_format_is_enforced(self) -> None:
        output = self.root / "format"
        generate_distribution(catalog=self.catalog, output_root=output)
        manifest_path = output / PLUGIN_RELATIVE / "plugin.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest["$schema"] = "https://agent-plugins.org/schemas/9.9.9/plugin.schema.json"
        manifest["skills"] = "./skills"
        manifest_path.write_text(json.dumps(manifest), encoding="utf-8")

        codex_errors = validate_codex_distribution(
            output_root=output, expected_skill_names={"code-review", "testing"}
        )
        copilot_errors = validate_copilot_distribution(
            output_root=output, expected_skill_names={"code-review", "testing"}
        )

        self.assertIn("portable plugin manifest has invalid '$schema'", codex_errors)
        self.assertIn(
            "portable plugin manifest has unsupported field: skills", codex_errors
        )
        self.assertIn("Copilot plugin does not declare Agent Plugins 1.0", copilot_errors)

    def test_marketplace_sources_cannot_escape_the_distribution_root(self) -> None:
        cases = (
            (
                ".agents/plugins/marketplace.json",
                validate_codex_distribution,
                lambda value: value["plugins"][0]["source"].update(
                    {"path": "./plugins/../../outside"}
                ),
                "Codex marketplace source.path must remain inside its root",
            ),
            (
                ".github/plugin/marketplace.json",
                validate_copilot_distribution,
                lambda value: value["plugins"][0].update(
                    {"source": "./plugins/../../outside"}
                ),
                "Copilot marketplace source must remain inside its root",
            ),
            (
                ".claude-plugin/marketplace.json",
                validate_claude_distribution,
                lambda value: value["plugins"][0].update(
                    {"source": "./plugins/../../outside"}
                ),
                "Claude marketplace source must remain inside its root",
            ),
        )
        for relative, validator, mutate, expected_error in cases:
            with self.subTest(marketplace=relative):
                output = self.root / ("unsafe-" + relative.split("/")[0].removeprefix("."))
                generate_distribution(catalog=self.catalog, output_root=output)
                marketplace_path = output / relative
                marketplace = json.loads(marketplace_path.read_text(encoding="utf-8"))
                mutate(marketplace)
                marketplace_path.write_text(json.dumps(marketplace), encoding="utf-8")

                errors = validator(
                    output_root=output,
                    expected_skill_names={"code-review", "testing"},
                )

                self.assertIn(expected_error, errors)

    def test_packaging_preserves_the_canonical_source_used_by_skills_cli(self) -> None:
        source = self.root / "npx-source/.agents/skills"
        source.mkdir(parents=True)
        write_skill(source, "testing", {"references/example.md": b"# Example\n"})
        before = snapshot(source)

        generate_distribution(catalog=source, output_root=self.root / "npx-output")

        self.assertEqual(before, snapshot(source))
        self.assertTrue((source / "testing/SKILL.md").is_file())

    def test_generation_is_reproducible(self) -> None:
        first = self.root / "first"
        second = self.root / "second"

        generate_distribution(catalog=self.catalog, output_root=first)
        generate_distribution(catalog=self.catalog, output_root=second)

        self.assertEqual(snapshot(first), snapshot(second))

    def test_check_detects_canonical_change_and_derived_edit(self) -> None:
        output = self.root / "output"
        generate_distribution(catalog=self.catalog, output_root=output)
        canonical = self.catalog / "testing/SKILL.md"
        canonical.write_text(canonical.read_text() + "\nUpdated.\n", encoding="utf-8")

        errors = check_distribution(catalog=self.catalog, output_root=output)

        self.assertTrue(any("skills/testing/SKILL.md" in error for error in errors))
        canonical.write_text(
            canonical.read_text().replace("\nUpdated.\n", ""), encoding="utf-8"
        )
        derived = output / PLUGIN_RELATIVE / "skills/testing/SKILL.md"
        derived.write_text("manual edit\n", encoding="utf-8")
        self.assertTrue(any("modified packaged file" in error for error in verify_package(output / PLUGIN_RELATIVE)))
        with self.assertRaisesRegex(PackageError, "refusing to replace modified"):
            generate_distribution(catalog=self.catalog, output_root=output)

    def test_check_detects_extra_package_file(self) -> None:
        output = self.root / "output"
        generate_distribution(catalog=self.catalog, output_root=output)
        (output / PLUGIN_RELATIVE / "manual.txt").write_text("manual\n", encoding="utf-8")

        errors = check_distribution(catalog=self.catalog, output_root=output)

        self.assertIn("unexpected generated package file: manual.txt", errors)

    def test_rejects_source_symlinks(self) -> None:
        target = self.catalog / "testing/details.txt"
        target.write_text("details\n", encoding="utf-8")
        link = self.catalog / "testing/alias.txt"
        try:
            link.symlink_to(target)
        except OSError as exc:
            self.skipTest(f"file symlinks are unavailable: {exc}")

        with self.assertRaisesRegex(PackageError, "non-regular files"):
            generate_distribution(catalog=self.catalog, output_root=self.root / "output")

    def test_rejects_a_symlinked_generated_output_parent(self) -> None:
        output = self.root / "output"
        output.mkdir()
        outside = self.root / "outside"
        outside.mkdir()
        linked_plugins = output / "plugins"
        try:
            linked_plugins.symlink_to(outside, target_is_directory=True)
        except OSError as exc:
            self.skipTest(f"directory symlinks are unavailable: {exc}")

        with self.assertRaisesRegex(
            PackageError, "generated output directory must be a regular directory"
        ):
            generate_distribution(catalog=self.catalog, output_root=output)

        self.assertEqual({}, snapshot(outside))


class CheckedInDistributionTests(unittest.TestCase):
    def test_checked_in_distribution_matches_canonical_catalog(self) -> None:
        self.assertEqual(
            [],
            check_distribution(catalog=DEFAULT_CATALOG, output_root=REPOSITORY_ROOT),
        )

    def test_checked_in_package_contains_all_ten_skills(self) -> None:
        package = REPOSITORY_ROOT / PLUGIN_RELATIVE
        skills = {path.name for path in (package / "skills").iterdir() if path.is_dir()}

        self.assertEqual(10, len(skills))
        self.assertEqual(
            {path.name for path in DEFAULT_CATALOG.iterdir() if path.is_dir()}, skills
        )
        inventory = json.loads((package / INVENTORY_NAME).read_text(encoding="utf-8"))
        self.assertEqual(PLUGIN_NAME, inventory["plugin"])
        self.assertEqual([], verify_package(package))

    def test_checked_in_package_files_match_the_canonical_catalog_byte_for_byte(self) -> None:
        package_skills = REPOSITORY_ROOT / PLUGIN_RELATIVE / "skills"

        canonical = snapshot(DEFAULT_CATALOG)
        distributed = snapshot(package_skills)

        self.assertEqual(canonical, distributed)
        self.assertTrue(
            any("/references/" in f"/{relative}" for relative in canonical),
            "the real-catalog comparison must cover supporting references",
        )


if __name__ == "__main__":
    unittest.main()
