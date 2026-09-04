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
