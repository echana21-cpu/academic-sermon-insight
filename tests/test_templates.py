"""Tests for project scaffolding templates."""

from __future__ import annotations

from pathlib import Path

import pytest

from sermon_insight.books import parse_passage
from sermon_insight.linter import lint_path
from sermon_insight.templates import scaffold_project


def test_scaffold_project_creates_five_clean_files(tmp_path: Path) -> None:
    passage = parse_passage("로마서 8장")
    created = scaffold_project(passage, tmp_path)

    assert len(created) == 5
    project_dir = tmp_path / "romans8_sermon_insight"
    assert project_dir.is_dir()
    assert (project_dir / "DASHBOARD.md").is_file()
    assert (project_dir / "ROMANS8_ACADEMIC_ANALYSIS_REPORT.md").is_file()
    assert (project_dir / "ROMANS8_QUANTITATIVE_AUDIT_REPORT.md").is_file()
    assert (project_dir / "ROMANS8_QUALITATIVE_REVIEW_REPORT.md").is_file()
    assert (project_dir / "ROMANS8_SERMON_OUTLINE.md").is_file()

    # Generated templates themselves must pass the 5-rule linter with 0 issues
    issues = lint_path(project_dir)
    assert issues == []


def test_scaffold_project_refuses_overwrite_without_force(tmp_path: Path) -> None:
    passage = parse_passage("John 15")
    scaffold_project(passage, tmp_path)
    with pytest.raises(FileExistsError):
        scaffold_project(passage, tmp_path, overwrite=False)
