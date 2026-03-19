import tempfile
from pathlib import Path

import pytest

from agent.skills_loader import load_skills


def test_load_skills():
    skills = load_skills("skills")
    assert len(skills) > 1000
    assert "SKILL-INDEX" in skills
    assert "skill-validate" in skills
    assert "skill-adapt" in skills
    assert "skill-debug" in skills


def test_skill_index_loaded_first():
    skills = load_skills("skills")
    index_pos = skills.index("SKILL-INDEX")
    validate_pos = skills.index("skill-validate")
    assert index_pos < validate_pos


def test_load_skills_missing_dir():
    with pytest.raises(FileNotFoundError):
        load_skills("/nonexistent/path")


def test_load_skills_empty_dir():
    with tempfile.TemporaryDirectory() as td:
        with pytest.raises(FileNotFoundError):
            load_skills(td)
