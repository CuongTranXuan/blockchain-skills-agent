from __future__ import annotations

from pathlib import Path


def load_skills(skills_dir: str = "skills") -> str:
    """Read all skill markdown files and concatenate into a single system prompt."""
    skills_path = Path(skills_dir)
    if not skills_path.exists():
        raise FileNotFoundError(f"Skills directory not found: {skills_path.resolve()}")

    files = sorted(
        skills_path.glob("*.md"),
        key=lambda f: (f.name != "SKILL-INDEX.md", f.name),
    )

    if not files:
        raise FileNotFoundError(f"No .md files found in {skills_path.resolve()}")

    parts: list[str] = []
    for f in files:
        parts.append(f"<!-- {f.name} -->\n{f.read_text()}")

    return "\n\n---\n\n".join(parts)
