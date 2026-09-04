from pathlib import Path
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
        for skill_name in EXPECTED_SKILLS:
            skill_dir = ROOT / "skills" / skill_name
            self.assertTrue(skill_dir.is_dir(), f"missing skill directory {skill_name}")
            for relative_path in REQUIRED_FILES:
                self.assertTrue(
                    (skill_dir / relative_path).is_file(),
                    f"missing {skill_name}/{relative_path}",
                )

    def test_frontmatter_name_matches_directory(self):
        for skill_name in EXPECTED_SKILLS:
            skill_file = ROOT / "skills" / skill_name / "SKILL.md"
            self.assertTrue(skill_file.is_file(), f"missing {skill_name}/SKILL.md")
            content = skill_file.read_text()
            self.assertTrue(content.startswith("---\n"))
            frontmatter = content.split("---\n", 2)[1]
            self.assertIn(f"name: {skill_name}", frontmatter)
            self.assertIn("description: Use when", frontmatter)


if __name__ == "__main__":
    unittest.main()
