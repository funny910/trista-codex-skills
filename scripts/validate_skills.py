"""Validate the shipped Codex skill structure without third-party packages."""

from pathlib import Path
import re
import sys
from typing import Optional


EXPECTED_SKILLS = {
    "codex-implement-change",
    "codex-readonly-review",
    "codex-verify-change",
}
REQUIRED_FILES = ("SKILL.md", "agents/openai.yaml")
REQUIRED_INTERFACE_KEYS = ("display_name", "short_description", "default_prompt")
SUPPORTED_FRONTMATTER_KEYS = {"name", "description"}
UNFINISHED_MARKERS = ("TODO", "TBD")


def _shown(path: Path, root: Path) -> str:
    try:
        return str(path.relative_to(root))
    except ValueError:
        return str(path)


def _read_text(path: Path, root: Path, findings: list[str]) -> Optional[str]:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        findings.append(
            f"{_shown(path, root)}: file must be readable UTF-8 text ({error})"
        )
        return None


def _frontmatter(
    content: str,
) -> tuple[Optional[dict[str, str]], list[str]]:
    lines = content.splitlines()
    if not lines or lines[0] != "---":
        return None, []
    try:
        closing = lines.index("---", 1)
    except ValueError:
        return None, []

    values: dict[str, str] = {}
    seen_keys: set[str] = set()
    rules: list[str] = []
    for line in lines[1:closing]:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue

        match = re.fullmatch(
            r"([A-Za-z_][A-Za-z0-9_-]*):[ \t]+([^\r\n]+)", line
        )
        if match is None:
            rules.append(
                "frontmatter must contain only top-level scalar mappings for "
                "name and description"
            )
            continue

        key, value = match.group(1), match.group(2).strip()
        if key in seen_keys:
            rules.append(f"frontmatter key {key} must not be duplicated")
            continue
        seen_keys.add(key)
        if key not in SUPPORTED_FRONTMATTER_KEYS:
            rules.append(
                f"frontmatter key {key} is unsupported; expected name or description"
            )
            continue
        values[key] = value

    return values, rules


def _section_value(content: str, section: str, key: str) -> Optional[str]:
    lines = content.splitlines()
    in_section = False
    for line in lines:
        if re.fullmatch(rf"{re.escape(section)}:\s*", line):
            in_section = True
            continue
        if in_section and line and not line[0].isspace():
            return None
        if in_section:
            match = re.fullmatch(
                rf"  {re.escape(key)}:\s*(.*?)\s*", line
            )
            if match:
                return match.group(1)
    return None


def _validate_frontmatter(
    skill_file: Path,
    skill_name: str,
    root: Path,
    findings: list[str],
    descriptions: dict[str, list[Path]],
) -> Optional[str]:
    content = _read_text(skill_file, root, findings)
    if content is None:
        return None

    for target in re.findall(r"\]\((references/[^)\s]+)", content):
        reference = skill_file.parent / target.split("#", 1)[0]
        if not reference.is_file():
            findings.append(
                f"{_shown(skill_file, root)}: local reference target {target} must exist"
            )

    values, frontmatter_rules = _frontmatter(content)
    if values is None:
        findings.append(
            f"{_shown(skill_file, root)}: frontmatter must be between the first two --- lines"
        )
        return content

    for rule in frontmatter_rules:
        findings.append(f"{_shown(skill_file, root)}: {rule}")

    if "name" not in values:
        findings.append(
            f"{_shown(skill_file, root)}: frontmatter name is required"
        )
    elif values["name"] != skill_name:
        findings.append(
            f"{_shown(skill_file, root)}: frontmatter name must exactly match {skill_name}"
        )

    description = values.get("description", "")
    if re.fullmatch(r"Use when\s+\S.*", description) is None:
        findings.append(
            f"{_shown(skill_file, root)}: frontmatter description must begin with Use when and include trigger text"
        )
    else:
        descriptions.setdefault(description, []).append(skill_file)

    return content


def _validate_agent_metadata(
    metadata_file: Path,
    skill_name: str,
    root: Path,
    findings: list[str],
) -> None:
    content = _read_text(metadata_file, root, findings)
    if content is None:
        return

    values: dict[str, str] = {}
    for key in REQUIRED_INTERFACE_KEYS:
        value = _section_value(content, "interface", key)
        if value is None:
            findings.append(
                f"{_shown(metadata_file, root)}: interface.{key} is required"
            )
            continue
        if not re.fullmatch(r'"[^"\n]+"', value):
            findings.append(
                f"{_shown(metadata_file, root)}: interface.{key} must be a non-empty quoted string"
            )
        values[key] = value

    default_prompt = values.get("default_prompt", "")
    skill_token = re.compile(rf"\${re.escape(skill_name)}(?![A-Za-z0-9_-])")
    if default_prompt and not skill_token.search(default_prompt):
        findings.append(
            f"{_shown(metadata_file, root)}: interface.default_prompt must name ${skill_name}"
        )

    implicit = _section_value(content, "policy", "allow_implicit_invocation")
    if implicit != "true":
        findings.append(
            f"{_shown(metadata_file, root)}: policy.allow_implicit_invocation must be true"
        )


def _scan_unfinished_markers(
    skill_dir: Path, root: Path, findings: list[str]
) -> None:
    try:
        files = sorted(path for path in skill_dir.rglob("*") if path.is_file())
    except OSError as error:
        findings.append(
            f"{_shown(skill_dir, root)}: shipped skill files must be readable ({error})"
        )
        return

    marker_pattern = re.compile(
        rf"\b(?:{'|'.join(map(re.escape, UNFINISHED_MARKERS))})\b"
    )
    for path in files:
        content = _read_text(path, root, findings)
        if content is None:
            continue
        markers = sorted(set(marker_pattern.findall(content)))
        if markers:
            findings.append(
                f"{_shown(path, root)}: shipped skill content must not contain unfinished marker token(s): {', '.join(markers)}"
            )


def validate_repo(root: Path) -> list[str]:
    """Return structural findings; an empty list means valid."""
    root = Path(root).resolve()
    findings: list[str] = []
    skills_dir = root / "skills"

    try:
        actual = {path.name for path in skills_dir.iterdir() if path.is_dir()}
    except OSError as error:
        actual = set()
        findings.append(
            f"{_shown(skills_dir, root)}: exact skill inventory must be readable ({error})"
        )

    missing = sorted(EXPECTED_SKILLS - actual)
    unexpected = sorted(actual - EXPECTED_SKILLS)
    if missing or unexpected:
        details = []
        if missing:
            details.append(f"missing {', '.join(missing)}")
        if unexpected:
            details.append(f"unexpected {', '.join(unexpected)}")
        findings.append(
            f"{_shown(skills_dir, root)}: exact skill inventory violated ({'; '.join(details)})"
        )

    descriptions: dict[str, list[Path]] = {}
    for skill_name in sorted(EXPECTED_SKILLS):
        skill_dir = skills_dir / skill_name
        skill_file = skill_dir / "SKILL.md"
        metadata_file = skill_dir / "agents" / "openai.yaml"

        for relative_path in REQUIRED_FILES:
            path = skill_dir / relative_path
            if not path.is_file():
                findings.append(
                    f"{_shown(path, root)}: required skill file must exist"
                )

        if skill_file.is_file():
            _validate_frontmatter(
                skill_file, skill_name, root, findings, descriptions
            )
        if metadata_file.is_file():
            _validate_agent_metadata(metadata_file, skill_name, root, findings)
        if skill_dir.is_dir():
            _scan_unfinished_markers(skill_dir, root, findings)

    for description, paths in sorted(descriptions.items()):
        if len(paths) > 1:
            for path in paths:
                findings.append(
                    f"{_shown(path, root)}: frontmatter description must be unique across skills"
                )

    return list(dict.fromkeys(findings))


def main(argv: list[str] | None = None) -> int:
    arguments = sys.argv[1:] if argv is None else argv
    if len(arguments) > 1:
        print("ERROR: usage: python scripts/validate_skills.py [repository-root]")
        return 1

    root = Path(arguments[0]) if arguments else Path(__file__).resolve().parents[1]
    findings = validate_repo(root)
    if findings:
        for finding in findings:
            print(f"ERROR: {finding}")
        return 1

    print(f"OK: {_shown(root.resolve(), root.resolve()) or '.'} skill structure is valid")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
