"""Command-line interface for the Academic Sermon Insight pipeline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from sermon_insight import __version__
from sermon_insight.academic_api import (
    search_crossref,
    search_openalex,
    verify_doi,
    verify_isbn_openlibrary,
)
from sermon_insight.auditor import render_audit_report, run_quantitative_audit
from sermon_insight.books import parse_passage
from sermon_insight.linter import lint_path
from sermon_insight.templates import scaffold_project


def _cmd_init(args: argparse.Namespace) -> int:
    passage = parse_passage(args.passage)
    out_dir = Path(args.out).expanduser().resolve()
    created = scaffold_project(passage, out_dir, overwrite=args.force)
    print(f"Created {len(created)} files in {out_dir / passage.folder_name}:")
    for path in created:
        print(f"  - {path.name}")
    return 0


def _cmd_search(args: argparse.Namespace) -> int:
    if args.source == "openalex":
        records = search_openalex(args.query, rows=args.rows)
    else:
        records = search_crossref(args.query, rows=args.rows)

    if args.json:
        payload = [
            {
                "title": r.title,
                "authors": list(r.authors),
                "year": r.year,
                "container": r.container,
                "doi": r.doi,
                "source": r.source,
                "chicago": r.format_chicago(),
            }
            for r in records
        ]
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        return 0

    for idx, rec in enumerate(records, start=1):
        print(f"[{idx}] {rec.format_chicago()}")
    return 0


def _cmd_verify_doi(args: argparse.Namespace) -> int:
    res = verify_doi(args.doi)
    if args.json:
        print(
            json.dumps(
                {
                    "identifier": res.identifier,
                    "kind": res.kind,
                    "valid": res.valid,
                    "title": res.title,
                    "authors": list(res.authors),
                    "publisher": res.publisher,
                    "year": res.year,
                    "detail": res.detail,
                },
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        status = "VALID" if res.valid else "INVALID"
        print(f"[{status}] {res.identifier} - {res.detail}")
        if res.title:
            print(f"  Title: {res.title}")
        if res.authors:
            print(f"  Authors: {', '.join(res.authors)}")
        if res.year or res.publisher:
            print(f"  Published: {res.publisher or ''} ({res.year or 'n.d.'})")
    return 0 if res.valid else 1


def _cmd_verify_isbn(args: argparse.Namespace) -> int:
    res = verify_isbn_openlibrary(args.isbn)
    status = "VALID" if res.valid else "INVALID"
    print(f"[{status}] {res.identifier} - {res.detail}")
    if res.title:
        print(f"  Title: {res.title}")
    return 0 if res.valid else 1


def _cmd_lint(args: argparse.Namespace) -> int:
    target = Path(args.target).expanduser().resolve()
    issues = lint_path(target, fix=args.fix)
    if not issues:
        print(f"CLEAN: 0 lint issues in {target}")
        return 0

    for issue in issues:
        print(f"{issue.file_path.name}:{issue.line} [{issue.rule}] {issue.message} ({issue.snippet})")
    print(f"Found {len(issues)} lint issue(s).")
    return 1


def _cmd_audit(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).expanduser().resolve()
    summary = run_quantitative_audit(
        project_dir=project_dir,
        offline=args.offline,
        min_en=args.min_en,
        min_de=args.min_de,
    )

    if args.write_report:
        existing = sorted(project_dir.glob("*QUANTITATIVE_AUDIT_REPORT.md"))
        report_path = (
            existing[0]
            if existing
            else project_dir / "QUANTITATIVE_AUDIT_REPORT.md"
        )
        report_path.write_text(render_audit_report(summary), encoding="utf-8")
        print(f"Wrote audit report: {report_path}")

    verdict = "CLEAN" if summary.passed else "REJECT"
    print(
        f"[{verdict}] entries={len(summary.entries)} "
        f"(EN={summary.en_count}, DE={summary.de_count}), "
        f"tier1={summary.tier1_count}, tier2={summary.tier2_count}, "
        f"stubs={len(summary.stub_files)}, lint_issues={len(summary.lint_issues)}"
    )
    for reason in summary.failure_reasons:
        print(f"  - {reason}")
    return 0 if summary.passed else 1


def _cmd_status(args: argparse.Namespace) -> int:
    project_dir = Path(args.project_dir).expanduser().resolve()
    if not project_dir.is_dir():
        print(f"Directory not found: {project_dir}", file=sys.stderr)
        return 1
    md_files = sorted(project_dir.glob("*.md"))
    print(f"Project: {project_dir.name} ({len(md_files)} markdown files)")
    for md in md_files:
        size_kb = md.stat().st_size / 1024
        print(f"  - {md.name} ({size_kb:.1f} KB)")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Construct the CLI argument parser."""
    parser = argparse.ArgumentParser(
        prog="sermon-insight",
        description="Academic Sermon Insight Pipeline CLI",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)

    p_init = sub.add_parser("init", help="Scaffold a new sermon insight project")
    p_init.add_argument("passage", help='Bible passage, e.g. "로마서 8장" or "Hebrews 8:1-13"')
    p_init.add_argument("--out", default=".", help="Parent directory for project folder")
    p_init.add_argument("--force", action="store_true", help="Overwrite existing files")
    p_init.set_defaults(func=_cmd_init)

    p_search = sub.add_parser("search", help="Search CrossRef or OpenAlex for literature")
    p_search.add_argument("query", help="Search query string")
    p_search.add_argument("--rows", type=int, default=10, help="Number of results")
    p_search.add_argument("--source", choices=("crossref", "openalex"), default="crossref")
    p_search.add_argument("--json", action="store_true", help="Output JSON")
    p_search.set_defaults(func=_cmd_search)

    p_doi = sub.add_parser("verify-doi", help="Verify a DOI via CrossRef REST API")
    p_doi.add_argument("doi", help="DOI string or doi.org URL")
    p_doi.add_argument("--json", action="store_true", help="Output JSON")
    p_doi.set_defaults(func=_cmd_verify_doi)

    p_isbn = sub.add_parser("verify-isbn", help="Validate ISBN checksum and query OpenLibrary")
    p_isbn.add_argument("isbn", help="ISBN-10 or ISBN-13")
    p_isbn.set_defaults(func=_cmd_verify_isbn)

    p_lint = sub.add_parser("lint", help="Lint Markdown files against the 5-rule constitution")
    p_lint.add_argument("target", help="Markdown file or project directory")
    p_lint.add_argument("--fix", action="store_true", help="Auto-fix safe formatting issues")
    p_lint.set_defaults(func=_cmd_lint)

    p_audit = sub.add_parser("audit", help="Run Stage 1 Quantitative Forensic Audit")
    p_audit.add_argument("project_dir", help="Path to *_sermon_insight directory")
    p_audit.add_argument("--offline", action="store_true", help="Skip network DOI lookups")
    p_audit.add_argument("--min-en", type=int, default=5, help="Minimum English works")
    p_audit.add_argument("--min-de", type=int, default=5, help="Minimum German works")
    p_audit.add_argument("--write-report", action="store_true", help="Write audit report markdown")
    p_audit.set_defaults(func=_cmd_audit)

    p_status = sub.add_parser("status", help="Show project files and sizes")
    p_status.add_argument("project_dir", help="Path to *_sermon_insight directory")
    p_status.set_defaults(func=_cmd_status)

    return parser


def main(argv: Optional[list[str]] = None) -> int:
    """CLI entry point."""
    parser = build_parser()
    args = parser.parse_args(argv)
    return int(args.func(args))
