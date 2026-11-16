"""Stage 1 Quantitative Forensic Auditor for sermon insight projects."""

from __future__ import annotations

import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from sermon_insight.academic_api import VerificationResult, validate_isbn, verify_doi
from sermon_insight.linter import LintIssue, lint_path

_DOI_RE = re.compile(r"DOI:\s*([^\s|]+)", re.IGNORECASE)
_ISBN_RE = re.compile(r"ISBN:\s*([0-9Xx-]{10,17})", re.IGNORECASE)
_TIER_1_RE = re.compile(r"1등급")
_TIER_2_RE = re.compile(r"2등급")


@dataclass(frozen=True)
class BibliographyEntry:
    """A single row parsed from Section 2.1 of the academic analysis report."""

    index: str
    language: str
    author: str
    title: str
    container: str
    pub_info: str
    identifier: str
    tier: str


@dataclass(frozen=True)
class AuditSummary:
    """Result of running the Stage 1 Quantitative Forensic Audit."""

    project_dir: Path
    academic_report: Optional[Path]
    entries: tuple[BibliographyEntry, ...]
    en_count: int
    de_count: int
    tier1_count: int
    tier2_count: int
    stub_files: tuple[Path, ...]
    lint_issues: tuple[LintIssue, ...]
    verifications: tuple[VerificationResult, ...]
    passed: bool
    failure_reasons: tuple[str, ...]


def parse_registry_table(markdown_text: str) -> list[BibliographyEntry]:
    """Extract bibliographic rows from Section 2.1 Markdown table."""
    entries: list[BibliographyEntry] = []
    in_registry = False

    for line in markdown_text.splitlines():
        stripped = line.strip()
        if stripped.startswith("### 2.1"):
            in_registry = True
            continue
        if in_registry and stripped.startswith("### "):
            break
        if not in_registry or not stripped.startswith("|"):
            continue

        cells = [c.strip() for c in stripped.strip("|").split("|")]
        if len(cells) < 8:
            continue
        if cells[0] in ("번호", ":---") or cells[0].startswith("---"):
            continue

        entries.append(
            BibliographyEntry(
                index=cells[0],
                language=cells[1],
                author=cells[2],
                title=cells[3],
                container=cells[4],
                pub_info=cells[5],
                identifier=cells[6],
                tier=cells[7],
            )
        )

    return entries


def _verify_entry_identifier(entry: BibliographyEntry, offline: bool) -> VerificationResult:
    """Verify the DOI or ISBN in a bibliography entry."""
    doi_match = _DOI_RE.search(entry.identifier)
    if doi_match:
        doi = doi_match.group(1)
        if "placeholder" in doi.lower():
            return VerificationResult(
                identifier=doi,
                kind="DOI",
                valid=False,
                detail="Placeholder DOI detected",
            )
        if offline:
            valid_syntax = doi.startswith("10.") and "/" in doi
            return VerificationResult(
                identifier=doi,
                kind="DOI",
                valid=valid_syntax,
                detail="Offline DOI syntax check" if valid_syntax else "Invalid DOI syntax",
            )
        return verify_doi(doi)

    isbn_match = _ISBN_RE.search(entry.identifier)
    if isbn_match:
        isbn = isbn_match.group(1)
        valid = validate_isbn(isbn)
        return VerificationResult(
            identifier=isbn,
            kind="ISBN",
            valid=valid,
            detail="ISBN checksum valid" if valid else "Invalid ISBN checksum",
        )

    # Secondary identifiers like ATLA ID or JSTOR URL
    return VerificationResult(
        identifier=entry.identifier,
        kind="OTHER",
        valid=bool(entry.identifier and entry.identifier != "-"),
        detail="Non-DOI/ISBN catalog identifier present",
    )


def run_quantitative_audit(
    project_dir: Path,
    offline: bool = False,
    min_en: int = 5,
    min_de: int = 5,
) -> AuditSummary:
    """Execute Stage 1 Quantitative Forensic Audit on a sermon insight directory."""
    academic_files = sorted(project_dir.glob("*ACADEMIC_ANALYSIS_REPORT.md"))
    academic_report = academic_files[0] if academic_files else None

    entries: list[BibliographyEntry] = []
    if academic_report is not None:
        entries = parse_registry_table(academic_report.read_text(encoding="utf-8"))

    en_count = sum(1 for e in entries if "영어" in e.language or "english" in e.language.lower())
    de_count = sum(1 for e in entries if "독일어" in e.language or "german" in e.language.lower())
    tier1_count = sum(1 for e in entries if _TIER_1_RE.search(e.tier))
    tier2_count = sum(1 for e in entries if _TIER_2_RE.search(e.tier))

    stub_files = tuple(sorted(project_dir.rglob("*.txt")))
    lint_issues = tuple(lint_path(project_dir, fix=False))
    verifications = tuple(_verify_entry_identifier(e, offline=offline) for e in entries)

    failures: list[str] = []
    if academic_report is None:
        failures.append("Missing *_ACADEMIC_ANALYSIS_REPORT.md")
    if not entries:
        failures.append("No bibliographic entries found in Section 2.1 table")
    if en_count < min_en:
        failures.append(f"English literature quota unmet: {en_count} < {min_en}")
    if de_count < min_de:
        failures.append(f"German literature quota unmet: {de_count} < {min_de}")
    if stub_files:
        failures.append(f"Synthetic .txt stub files detected: {len(stub_files)}")
    if lint_issues:
        failures.append(f"Markdown lint issues detected: {len(lint_issues)}")
    invalid_ids = [v for v in verifications if not v.valid]
    if invalid_ids:
        failures.append(f"Invalid bibliographic identifiers: {len(invalid_ids)}")

    return AuditSummary(
        project_dir=project_dir,
        academic_report=academic_report,
        entries=tuple(entries),
        en_count=en_count,
        de_count=de_count,
        tier1_count=tier1_count,
        tier2_count=tier2_count,
        stub_files=stub_files,
        lint_issues=lint_issues,
        verifications=verifications,
        passed=len(failures) == 0,
        failure_reasons=tuple(failures),
    )


def render_audit_report(summary: AuditSummary) -> str:
    """Render a Stage 1 Quantitative Forensic Audit report from an ``AuditSummary``."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    verdict = "**최종 판정: 완전 적합**(CLEAN)" if summary.passed else "**최종 판정: 보완 필요**(REJECT)"

    rows: list[str] = []
    for entry, ver in zip(summary.entries, summary.verifications):
        status = "**일치**(PASS)" if ver.valid else f"**불일치**(FAIL: {ver.detail})"
        rows.append(
            f"| {entry.index} | {entry.language} | {entry.author} | {entry.title} | "
            f"{ver.kind}: {ver.identifier} | {status} |"
        )
    table_body = "\n".join(rows) if rows else "| - | - | - | - | - | 항목 없음 |"

    failures_section = ""
    if summary.failure_reasons:
        bullet_list = "\n".join(f"- {reason}" for reason in summary.failure_reasons)
        failures_section = f"\n### 미충족 항목\n{bullet_list}\n"

    return f"""# 1차 정량 검수 보고서 (Stage 1 Quantitative Forensic Audit)

* **검수 일시**: {now}
* **검수 대상 디렉터리**: `{summary.project_dir}`
* **자동 감사 도구**: `sermon-insight audit`

---

## 1. 종합 판정 결과 (Formal Verdict)

{verdict}
{failures_section}
---

## 2. 4대 정량 검증 영역별 실사 결과 요약

| 검증 영역 | 점검 항목 및 기준 | 실사 결과 | 판정 |
| :--- | :--- | :--- | :--- |
| **1. 서지 완전성 및 인용 진위** | 총 {len(summary.entries)}편 전수 식별자 검증 | 유효 {sum(1 for v in summary.verifications if v.valid)}/{len(summary.verifications)}편 | {"**PASS**" if all(v.valid for v in summary.verifications) and summary.verifications else "**FAIL**"} |
| **2. 사료 진위 3등급제 준수** | 1등급 / 2등급 구분 표기 | 1등급 {summary.tier1_count}편, 2등급 {summary.tier2_count}편, 스텁 {len(summary.stub_files)}건 | {"**PASS**" if not summary.stub_files else "**FAIL**"} |
| **3. 언어별 문헌 수 쿼터** | 영미권 / 독일어권 균형 | 영문 {summary.en_count}편, 독문 {summary.de_count}편 | {"**PASS**" if summary.en_count >= 5 and summary.de_count >= 5 else "**FAIL**"} |
| **4. 파일 실재성 및 린트** | 마크다운 5대 헌법 준수 | 린트 오류 {len(summary.lint_issues)}건 | {"**PASS**" if not summary.lint_issues else "**FAIL**"} |

---

## 3. 서지 완전성 및 인용 진위 포렌식 전수 실사 대조표

| 번호 | 언어권 | 저자 | 저작/논문 제목 | 식별자 | 실사 결과 |
| :--- | :--- | :--- | :--- | :--- | :--- |
{table_body}
"""
