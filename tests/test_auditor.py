"""Tests for Stage 1 Quantitative Forensic Auditor."""

from __future__ import annotations

from pathlib import Path
import shutil

from sermon_insight.auditor import render_audit_report, run_quantitative_audit
from sermon_insight.linter import lint_path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_DIR = REPO_ROOT / "examples" / "hebrews8_sermon_insight"


def test_audit_example_hebrews8_offline_passes(tmp_path: Path) -> None:
    assert EXAMPLE_DIR.is_dir()
    work_dir = tmp_path / "hebrews8_sermon_insight"
    shutil.copytree(EXAMPLE_DIR, work_dir)

    # Fix any legacy bold-paren formatting in the copied sample, then audit
    remaining = lint_path(work_dir, fix=True)
    assert remaining == []

    summary = run_quantitative_audit(work_dir, offline=True)
    assert len(summary.entries) == 11
    assert summary.en_count == 5
    assert summary.de_count == 6
    assert summary.tier1_count == 5
    assert summary.tier2_count == 6
    assert summary.stub_files == ()
    assert summary.lint_issues == ()
    assert summary.passed is True

    report_md = render_audit_report(summary)
    assert "CLEAN" in report_md


def test_audit_detects_stub_file_and_missing_quota(tmp_path: Path) -> None:
    (tmp_path / "stub.txt").write_text("fake stub", encoding="utf-8")
    summary = run_quantitative_audit(tmp_path, offline=True)
    assert summary.passed is False
    assert any("Missing *_ACADEMIC_ANALYSIS_REPORT.md" in r for r in summary.failure_reasons)
    assert any("Synthetic .txt stub" in r for r in summary.failure_reasons)
