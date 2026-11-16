"""Tests for the 5-Rule Markdown Constitution linter."""

from __future__ import annotations

from pathlib import Path

from sermon_insight.linter import fix_markdown, lint_markdown


def test_lint_detects_all_four_inline_rules() -> None:
    sample = (
        "이것은 *이탤릭* 입니다.\n"
        "이것은 _언더스코어_ 입니다.\n"
        "**단어(설명)** 은 분리해야 합니다.\n"
        "** 공백 ** 은 금지됩니다.\n"
        "엠대시 — 는 하이픈으로 바꿉니다.\n"
    )
    issues = lint_markdown(sample, Path("notes.md"))
    rules = {i.rule for i in issues}
    assert "NO_ITALICS" in rules
    assert "BOLD_PAREN_SEPARATION" in rules
    assert "NO_BOLD_INTERNAL_SPACE" in rules
    assert "NO_EM_DASH" in rules


def test_lint_ignores_bullets_inline_code_and_identifiers() -> None:
    sample = (
        "* **항목**(설명): `auditor_quantitative_m3` 및 https://example.com/a_b_c\n"
        "- 정상적인 하이픈 - 사용\n"
    )
    issues = lint_markdown(sample, Path("notes.md"))
    assert issues == []


def test_fix_markdown_resolves_safe_formatting() -> None:
    dirty = "**단어(설명)** 과 ** 공백 ** 그리고 — 테스트\n"
    fixed = fix_markdown(dirty)
    assert fixed == "**단어**(설명) 과 **공백** 그리고 - 테스트\n"
