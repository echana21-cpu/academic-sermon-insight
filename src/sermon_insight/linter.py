"""5-Rule Markdown Constitution linter and auto-fixer."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

_INLINE_CODE_RE = re.compile(r"`[^`\n]+`")
_BOLD_RE = re.compile(r"\*\*[^\n*]+?\*\*")
_URL_RE = re.compile(r"https?://\S+")

# Rule 1: italics (*text* or _text_) outside bold, bullets, URLs, and identifiers
_ASTERISK_ITALIC_RE = re.compile(r"(?<!\*)\*(?!\*)([^*\n]+?)(?<!\*)\*(?!\*)")
_UNDERSCORE_ITALIC_RE = re.compile(r"(?<![A-Za-z0-9_])_([^_\n]+?)_(?![A-Za-z0-9_])")

# Balanced bold span: **content**
_BOLD_SPAN_RE = re.compile(r"\*\*([^\n*]+?)\*\*")
_PAREN_TAIL_RE = re.compile(r"^(.+?)\s*(\([^)\n]+\))$")

# Rule 4: em-dash (—)
_EM_DASH = "\u2014"

REQUIRED_SECTIONS: dict[str, tuple[str, ...]] = {
    "ACADEMIC_ANALYSIS_REPORT": (
        "## 1.",
        "## 2.",
        "## 3.",
        "## 4.",
        "## 5.",
        "## 6.",
    ),
    "SERMON_OUTLINE": (
        "## 1.",
        "## 2.",
        "## 3.",
        "### 제1대지",
        "### 제2대지",
        "### 제3대지",
        "## 4.",
        "## 5.",
    ),
    "QUANTITATIVE_AUDIT_REPORT": (
        "## 1.",
        "## 2.",
        "## 3.",
    ),
    "QUALITATIVE_REVIEW_REPORT": (
        "## 1.",
        "## 2.",
        "## 3.",
    ),
}


@dataclass(frozen=True)
class LintIssue:
    """A single Markdown Constitution violation."""

    file_path: Path
    line: int
    rule: str
    message: str
    snippet: str = ""


def _strip_ignored_spans(line: str) -> str:
    """Mask inline code, URLs, and bold spans so italic regexes do not misfire."""
    cleaned = _INLINE_CODE_RE.sub(lambda m: " " * len(m.group(0)), line)
    cleaned = _URL_RE.sub(lambda m: " " * len(m.group(0)), cleaned)
    return cleaned


def _detect_doc_type(path: Path) -> str | None:
    """Infer document type from standard filename suffixes."""
    upper = path.name.upper()
    for doc_type in REQUIRED_SECTIONS:
        if doc_type in upper:
            return doc_type
    return None


def lint_markdown(text: str, file_path: Path) -> list[LintIssue]:
    """Check a Markdown string against the 5-Rule Markdown Constitution."""
    issues: list[LintIssue] = []
    lines = text.splitlines()
    in_code_fence = False

    for idx, line in enumerate(lines, start=1):
        stripped = line.lstrip()
        if stripped.startswith("```"):
            in_code_fence = not in_code_fence
            continue
        if in_code_fence:
            continue

        line_no_code = _INLINE_CODE_RE.sub("", line)

        # Rule 4: Em-dash check (outside inline code)
        if _EM_DASH in line_no_code:
            issues.append(
                LintIssue(
                    file_path=file_path,
                    line=idx,
                    rule="NO_EM_DASH",
                    message="Em-dash (—) is forbidden; use hyphen (-).",
                    snippet=line.strip()[:80],
                )
            )

        # Rules 2 & 3: inspect balanced **...** spans
        for m in _BOLD_SPAN_RE.finditer(line_no_code):
            inner = m.group(1)
            if inner != inner.strip():
                issues.append(
                    LintIssue(
                        file_path=file_path,
                        line=idx,
                        rule="NO_BOLD_INTERNAL_SPACE",
                        message="Remove leading/trailing whitespace inside **...**.",
                        snippet=m.group(0),
                    )
                )
            if _PAREN_TAIL_RE.match(inner.strip()):
                issues.append(
                    LintIssue(
                        file_path=file_path,
                        line=idx,
                        rule="BOLD_PAREN_SEPARATION",
                        message="Keep parentheses outside bold: **term**(explanation).",
                        snippet=m.group(0),
                    )
                )

        # Rule 1: Italics check
        masked = _strip_ignored_spans(line)
        # Remove leading list bullet `* ` before checking `*italic*`
        bullet_masked = re.sub(r"^(\s*)\*(\s+)", r"\1 \2", masked)
        bullet_masked = _BOLD_RE.sub(lambda m: " " * len(m.group(0)), bullet_masked)

        for m in _ASTERISK_ITALIC_RE.finditer(bullet_masked):
            issues.append(
                LintIssue(
                    file_path=file_path,
                    line=idx,
                    rule="NO_ITALICS",
                    message="Asterisk italics (*...*) are forbidden; use '...' or **...**.",
                    snippet=m.group(0),
                )
            )
        for m in _UNDERSCORE_ITALIC_RE.finditer(bullet_masked):
            issues.append(
                LintIssue(
                    file_path=file_path,
                    line=idx,
                    rule="NO_ITALICS",
                    message="Underscore italics (_..._) are forbidden; use '...' or **...**.",
                    snippet=m.group(0),
                )
            )

    # Rule 5: Required structural sections
    doc_type = _detect_doc_type(file_path)
    if doc_type:
        for heading in REQUIRED_SECTIONS[doc_type]:
            if heading not in text:
                issues.append(
                    LintIssue(
                        file_path=file_path,
                        line=1,
                        rule="STRUCTURE_MISSING",
                        message=f"Missing required section heading: {heading}",
                        snippet=heading,
                    )
                )

    return issues


def _fix_bold_match(match: re.Match[str]) -> str:
    """Trim internal whitespace and move trailing parentheses outside bold."""
    inner = match.group(1).strip()
    paren_match = _PAREN_TAIL_RE.match(inner)
    if paren_match:
        return f"**{paren_match.group(1).strip()}**{paren_match.group(2)}"
    return f"**{inner}**"


def fix_markdown(text: str) -> str:
    """Auto-fix safe formatting violations (em-dash, bold whitespace, bold-paren)."""
    fixed_lines: list[str] = []
    in_code_fence = False

    for line in text.splitlines(keepends=True):
        if line.lstrip().startswith("```"):
            in_code_fence = not in_code_fence
            fixed_lines.append(line)
            continue
        if in_code_fence:
            fixed_lines.append(line)
            continue

        updated = line.replace(_EM_DASH, "-")
        updated = _BOLD_SPAN_RE.sub(_fix_bold_match, updated)
        fixed_lines.append(updated)

    return "".join(fixed_lines)


def lint_path(target: Path, fix: bool = False) -> list[LintIssue]:
    """Lint a single Markdown file or all ``.md`` files in a directory."""
    files = sorted(target.glob("*.md")) if target.is_dir() else [target]
    all_issues: list[LintIssue] = []

    for md_file in files:
        content = md_file.read_text(encoding="utf-8")
        if fix:
            fixed = fix_markdown(content)
            if fixed != content:
                md_file.write_text(fixed, encoding="utf-8")
                content = fixed
        all_issues.extend(lint_markdown(content, md_file))

    return all_issues
