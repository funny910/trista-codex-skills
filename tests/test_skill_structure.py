from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_SKILLS = {
    "codex-implement-change",
    "codex-readonly-review",
    "codex-verify-change",
}
REQUIRED_FILES = {"SKILL.md", "agents/openai.yaml"}


class SkillStructureTests(unittest.TestCase):
    def test_exact_skill_inventory(self):
        skills_dir = ROOT / "skills"
        self.assertTrue(skills_dir.is_dir(), "skills/ must exist")
        actual = {item.name for item in skills_dir.iterdir() if item.is_dir()}
        self.assertEqual(EXPECTED_SKILLS, actual)

    def test_each_skill_has_required_files(self):
        for skill_name in sorted(EXPECTED_SKILLS):
            skill_dir = ROOT / "skills" / skill_name
            self.assertTrue(skill_dir.is_dir(), f"missing skill directory {skill_name}")
            for relative_path in REQUIRED_FILES:
                self.assertTrue(
                    (skill_dir / relative_path).is_file(),
                    f"missing {skill_name}/{relative_path}",
                )

    def test_frontmatter_name_matches_directory(self):
        for skill_name in sorted(EXPECTED_SKILLS):
            skill_file = ROOT / "skills" / skill_name / "SKILL.md"
            self.assertTrue(skill_file.is_file(), f"missing {skill_name}/SKILL.md")
            content = skill_file.read_text()
            self.assertTrue(content.startswith("---\n"))
            frontmatter = content.split("---\n", 2)[1]
            self.assertIn(f"name: {skill_name}", frontmatter)
            self.assertIn("description: Use when", frontmatter)


class ValidatorTests(unittest.TestCase):
    def _copy_skills(self, directory):
        fixture = Path(directory)
        shutil.copytree(ROOT / "skills", fixture / "skills")
        return fixture

    def _run_validator(self, fixture):
        return subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_skills.py"), str(fixture)],
            capture_output=True,
            text=True,
        )

    def _skill_file(self, fixture, skill_name="codex-implement-change"):
        return Path(fixture) / "skills" / skill_name / "SKILL.md"

    def _metadata_file(self, fixture, skill_name="codex-implement-change"):
        return Path(fixture) / "skills" / skill_name / "agents" / "openai.yaml"

    def _assert_rejected(self, fixture, expected_rule):
        result = self._run_validator(fixture)
        self.assertEqual(1, result.returncode, result.stdout + result.stderr)
        self.assertEqual("", result.stderr)
        self.assertIn(expected_rule, result.stdout)

    def test_validator_accepts_repository(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "scripts" / "validate_skills.py"), str(ROOT)],
            capture_output=True,
            text=True,
        )
        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_validator_rejects_frontmatter_name_mismatch(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = Path(directory)
            skill = fixture / "skills" / "codex-implement-change"
            (skill / "agents").mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: wrong-name\ndescription: Use when testing a fixture.\n---\n"
            )
            (skill / "agents" / "openai.yaml").write_text(
                'interface:\n  default_prompt: "Use $codex-implement-change."\n'
            )
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / "validate_skills.py"), str(fixture)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("frontmatter name", result.stdout)

    def test_validator_rejects_orphan_frontmatter_sequence_line(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            skill_file = self._skill_file(fixture)
            skill_file.write_text(
                skill_file.read_text().replace(
                    "description: Use when",
                    "- orphan-sequence-item\ndescription: Use when",
                    1,
                )
            )

            self._assert_rejected(
                fixture,
                "frontmatter must contain only top-level scalar mappings for "
                "name and description",
            )

    def test_validator_rejects_empty_use_when_trigger(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            skill_file = self._skill_file(fixture)
            lines = skill_file.read_text().splitlines()
            lines[2] = "description: Use when"
            skill_file.write_text("\n".join(lines) + "\n")

            self._assert_rejected(
                fixture,
                "frontmatter description must begin with Use when and include "
                "trigger text",
            )

    def test_validator_rejects_duplicate_frontmatter_key(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            skill_file = self._skill_file(fixture)
            skill_file.write_text(
                skill_file.read_text().replace(
                    "name: codex-implement-change",
                    "name: codex-implement-change\nname: codex-implement-change",
                    1,
                )
            )

            self._assert_rejected(
                fixture, "frontmatter key name must not be duplicated"
            )

    def test_validator_rejects_plain_scalar_yaml_breakers(self):
        invalid_descriptions = (
            "description: Use when foo: bar",
            "description: Use when foo:",
            "description: Use when foo # inline comment",
        )
        for description in invalid_descriptions:
            with (
                self.subTest(description=description),
                tempfile.TemporaryDirectory() as directory,
            ):
                fixture = self._copy_skills(directory)
                skill_file = self._skill_file(fixture)
                lines = skill_file.read_text().splitlines()
                lines[2] = description
                skill_file.write_text("\n".join(lines) + "\n")

                self._assert_rejected(
                    fixture,
                    "frontmatter plain scalar values must not contain YAML "
                    "mapping or comment syntax",
                )

    def test_validator_rejects_tabs_in_frontmatter(self):
        invalid_lines = (
            "name:\tcodex-implement-change",
            "description: Use when foo\tbar",
        )
        for line in invalid_lines:
            with (
                self.subTest(line=line),
                tempfile.TemporaryDirectory() as directory,
            ):
                fixture = self._copy_skills(directory)
                skill_file = self._skill_file(fixture)
                lines = skill_file.read_text().splitlines()
                lines[1 if line.startswith("name") else 2] = line
                skill_file.write_text("\n".join(lines) + "\n")

                self._assert_rejected(
                    fixture, "frontmatter must not contain tab characters"
                )

    def test_validator_rejects_punctuation_only_trigger_text(self):
        for trigger in ("---", "?!"):
            with (
                self.subTest(trigger=trigger),
                tempfile.TemporaryDirectory() as directory,
            ):
                fixture = self._copy_skills(directory)
                skill_file = self._skill_file(fixture)
                lines = skill_file.read_text().splitlines()
                lines[2] = f"description: Use when {trigger}"
                skill_file.write_text("\n".join(lines) + "\n")

                self._assert_rejected(
                    fixture,
                    "frontmatter description must begin with Use when and "
                    "include trigger text",
                )

    def test_validator_rejects_non_alphanumeric_trigger_text(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            skill_file = self._skill_file(fixture)
            lines = skill_file.read_text().splitlines()
            lines[2] = "description: Use when ___"
            skill_file.write_text("\n".join(lines) + "\n")

            self._assert_rejected(
                fixture,
                "frontmatter description must begin with Use when and include "
                "trigger text",
            )

    def test_validator_rejects_frontmatter_control_characters(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            skill_file = self._skill_file(fixture)
            lines = skill_file.read_text().splitlines()
            lines[2] = "description: Use when a\x00change is requested"
            skill_file.write_text("\n".join(lines) + "\n")

            self._assert_rejected(
                fixture,
                "frontmatter must not contain unsupported control, line-separator, "
                "or noncharacter code points",
            )

    def test_validator_rejects_unsupported_frontmatter_codepoints(self):
        codepoints = (
            ("next-line", "\u0085"),
            ("line-separator", "\u2028"),
            ("paragraph-separator", "\u2029"),
            ("noncharacter-fffe", "\ufffe"),
            ("noncharacter-ffff", "\uffff"),
        )
        for name, character in codepoints:
            with (
                self.subTest(name=name),
                tempfile.TemporaryDirectory() as directory,
            ):
                fixture = self._copy_skills(directory)
                skill_file = self._skill_file(fixture)
                lines = skill_file.read_text().splitlines()
                lines[2] = f"description: Use when alpha{character}beta"
                skill_file.write_text("\n".join(lines) + "\n")

                self._assert_rejected(
                    fixture,
                    "frontmatter must not contain unsupported control, "
                    "line-separator, or noncharacter code points",
                )

    def test_validator_rejects_frontmatter_angle_brackets(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            skill_file = self._skill_file(fixture)
            lines = skill_file.read_text().splitlines()
            lines[2] = "description: Use when <foo> is requested"
            skill_file.write_text("\n".join(lines) + "\n")

            self._assert_rejected(
                fixture, "frontmatter description must not contain angle brackets"
            )

    def test_validator_rejects_overlong_frontmatter_description(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            skill_file = self._skill_file(fixture)
            description = "Use when " + "x" * 1016
            self.assertEqual(1025, len(description))
            lines = skill_file.read_text().splitlines()
            lines[2] = f"description: {description}"
            skill_file.write_text("\n".join(lines) + "\n")

            self._assert_rejected(
                fixture,
                "frontmatter description must be at most 1024 characters",
            )

    def test_validator_reports_malformed_frontmatter_and_missing_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            skill_file = fixture / "skills" / "codex-implement-change" / "SKILL.md"
            skill_file.write_text(
                "# Missing frontmatter\n\n[missing](references/does-not-exist.md)\n"
            )

            result = self._run_validator(fixture)

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual("", result.stderr)
            self.assertIn(
                "ERROR: skills/codex-implement-change/SKILL.md: "
                "frontmatter must be between the first two --- lines",
                result.stdout,
            )
            self.assertIn(
                "ERROR: skills/codex-implement-change/SKILL.md: "
                "local reference target references/does-not-exist.md must exist",
                result.stdout,
            )

    def test_validator_rejects_longer_default_prompt_skill_token(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            metadata_file = (
                fixture
                / "skills"
                / "codex-implement-change"
                / "agents"
                / "openai.yaml"
            )
            metadata_file.write_text(
                metadata_file.read_text().replace(
                    "$codex-implement-change", "$codex-implement-change-extra"
                )
            )

            result = self._run_validator(fixture)

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual("", result.stderr)
            self.assertIn(
                "ERROR: skills/codex-implement-change/agents/openai.yaml: "
                "interface.default_prompt must name $codex-implement-change",
                result.stdout,
            )

    def test_validator_rejects_orphan_and_tabbed_metadata_junk(self):
        cases = (
            (
                "orphan sequence",
                "\n- orphan-sequence-item\n",
                "metadata must contain only supported sections and exactly "
                "two-space scalar keys",
            ),
            (
                "tab indentation",
                "\n\torphan: value\n",
                "metadata must not contain tab characters",
            ),
        )
        for case, suffix, expected_rule in cases:
            with (
                self.subTest(case=case),
                tempfile.TemporaryDirectory() as directory,
            ):
                fixture = self._copy_skills(directory)
                metadata_file = self._metadata_file(fixture)
                metadata_file.write_text(metadata_file.read_text() + suffix)

                self._assert_rejected(fixture, expected_rule)

    def test_validator_rejects_metadata_control_characters(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            metadata_file = self._metadata_file(fixture)
            metadata_file.write_text(
                metadata_file.read_text() + "\n# invalid\x00comment\n"
            )

            self._assert_rejected(
                fixture,
                "metadata must not contain unsupported control, line-separator, "
                "or noncharacter code points",
            )

    def test_validator_rejects_unsupported_metadata_codepoints(self):
        codepoints = (
            ("next-line", "\u0085"),
            ("line-separator", "\u2028"),
            ("paragraph-separator", "\u2029"),
            ("noncharacter-fffe", "\ufffe"),
            ("noncharacter-ffff", "\uffff"),
        )
        for name, character in codepoints:
            with (
                self.subTest(name=name),
                tempfile.TemporaryDirectory() as directory,
            ):
                fixture = self._copy_skills(directory)
                metadata_file = self._metadata_file(fixture)
                metadata_file.write_text(
                    metadata_file.read_text().replace(
                        "Codex: Implement Change",
                        f"Codex: Implement{character}Change",
                        1,
                    )
                )

                self._assert_rejected(
                    fixture,
                    "metadata must not contain unsupported control, "
                    "line-separator, or noncharacter code points",
                )

    def test_validator_rejects_duplicate_metadata_section(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            metadata_file = self._metadata_file(fixture)
            metadata_file.write_text(
                metadata_file.read_text()
                + "\npolicy:\n  allow_implicit_invocation: false\n"
            )

            self._assert_rejected(
                fixture, "metadata section policy must not be duplicated"
            )

    def test_validator_rejects_duplicate_implicit_invocation_key(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            metadata_file = self._metadata_file(fixture)
            metadata_file.write_text(
                metadata_file.read_text().replace(
                    "  allow_implicit_invocation: true",
                    "  allow_implicit_invocation: true\n"
                    "  allow_implicit_invocation: false",
                    1,
                )
            )

            self._assert_rejected(
                fixture,
                "metadata key policy.allow_implicit_invocation must not be "
                "duplicated",
            )

    def test_validator_rejects_duplicate_default_prompt_key(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            metadata_file = self._metadata_file(fixture)
            metadata_file.write_text(
                metadata_file.read_text().replace(
                    "\n\npolicy:",
                    '\n  default_prompt: "Do something else."\n\npolicy:',
                    1,
                )
            )

            self._assert_rejected(
                fixture,
                "metadata key interface.default_prompt must not be duplicated",
            )

    def test_validator_rejects_unknown_metadata_sections_and_keys(self):
        cases = (
            (
                "section",
                "\nextra:\n  value: \"unsupported\"\n",
                "metadata section extra is unsupported",
            ),
            (
                "key",
                '\n  extra: "unsupported"',
                "metadata key interface.extra is unsupported",
            ),
        )
        for case, addition, expected_rule in cases:
            with (
                self.subTest(case=case),
                tempfile.TemporaryDirectory() as directory,
            ):
                fixture = self._copy_skills(directory)
                metadata_file = self._metadata_file(fixture)
                content = metadata_file.read_text()
                if case == "section":
                    content += addition
                else:
                    content = content.replace("\n\npolicy:", addition + "\n\npolicy:", 1)
                metadata_file.write_text(content)

                self._assert_rejected(fixture, expected_rule)

    def test_validator_rejects_metadata_backslash_escapes(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            metadata_file = self._metadata_file(fixture)
            metadata_file.write_text(
                metadata_file.read_text().replace(
                    "Use $codex-implement-change",
                    "Use \\q $codex-implement-change",
                    1,
                )
            )

            self._assert_rejected(
                fixture,
                "interface.default_prompt must be a non-empty double-quoted "
                "string without backslashes",
            )

    def test_validator_rejects_false_or_missing_implicit_invocation(self):
        replacements = {
            "false": "  allow_implicit_invocation: false",
            "missing": "",
        }
        for case, replacement in replacements.items():
            with (
                self.subTest(case=case),
                tempfile.TemporaryDirectory() as directory,
            ):
                fixture = self._copy_skills(directory)
                metadata_file = self._metadata_file(fixture)
                metadata_file.write_text(
                    metadata_file.read_text().replace(
                        "  allow_implicit_invocation: true", replacement, 1
                    )
                )

                self._assert_rejected(
                    fixture, "policy.allow_implicit_invocation must be true"
                )

    def test_validator_rejects_unfinished_markers(self):
        for marker in ("TODO", "TBD"):
            with (
                self.subTest(marker=marker),
                tempfile.TemporaryDirectory() as directory,
            ):
                fixture = self._copy_skills(directory)
                skill_file = self._skill_file(fixture)
                skill_file.write_text(skill_file.read_text() + f"\n{marker}\n")

                self._assert_rejected(
                    fixture,
                    "shipped skill content must not contain unfinished marker token(s): "
                    f"{marker}",
                )

    def test_validator_rejects_duplicate_descriptions(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            source_file = self._skill_file(fixture)
            duplicate_file = self._skill_file(fixture, "codex-readonly-review")
            source_description = source_file.read_text().splitlines()[2]
            duplicate_lines = duplicate_file.read_text().splitlines()
            duplicate_lines[2] = source_description
            duplicate_file.write_text("\n".join(duplicate_lines) + "\n")

            result = self._run_validator(fixture)

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual("", result.stderr)
            self.assertEqual(
                2,
                result.stdout.count(
                    "frontmatter description must be unique across skills"
                ),
                result.stdout,
            )

    def test_validator_reports_unreadable_required_file_once(self):
        with tempfile.TemporaryDirectory() as directory:
            fixture = self._copy_skills(directory)
            skill_file = fixture / "skills" / "codex-implement-change" / "SKILL.md"
            skill_file.write_bytes(b"\xff")

            result = self._run_validator(fixture)

            self.assertEqual(1, result.returncode, result.stdout + result.stderr)
            self.assertEqual("", result.stderr)
            readability_lines = [
                line
                for line in result.stdout.splitlines()
                if line.startswith(
                    "ERROR: skills/codex-implement-change/SKILL.md: "
                    "file must be readable UTF-8 text"
                )
            ]
            self.assertEqual(1, len(readability_lines), result.stdout)


if __name__ == "__main__":
    unittest.main()
