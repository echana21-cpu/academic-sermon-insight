"""CLI integration tests."""

from __future__ import annotations

from pathlib import Path
import shutil

from sermon_insight.cli import main

REPO_ROOT = Path(__file__).resolve().parent.parent
EXAMPLE_DIR = REPO_ROOT / "examples" / "hebrews8_sermon_insight"


def test_cli_init_lint_status(tmp_path: Path) -> None:
    rc_init = main(["init", "에베소서 1장", "--out", str(tmp_path)])
    assert rc_init == 0

    project_dir = tmp_path / "ephesians1_sermon_insight"
    assert main(["lint", str(project_dir)]) == 0
    assert main(["status", str(project_dir)]) == 0


def test_cli_example_hebrews8_audit_offline(tmp_path: Path) -> None:
    work_dir = tmp_path / "hebrews8_sermon_insight"
    shutil.copytree(EXAMPLE_DIR, work_dir)
    assert main(["lint", str(work_dir), "--fix"]) == 0
    assert main(["audit", str(work_dir), "--offline"]) == 0
