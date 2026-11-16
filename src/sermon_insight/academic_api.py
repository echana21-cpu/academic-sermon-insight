"""Academic reservoir search and bibliographic verification clients."""

from __future__ import annotations

import json
import re
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any, Optional

USER_AGENT = "academic-sermon-insight/0.1.0 (mailto:echana21@gmail.com)"
DEFAULT_TIMEOUT = 15


@dataclass(frozen=True)
class WorkRecord:
    """Normalized academic work metadata from CrossRef or OpenAlex."""

    title: str
    authors: tuple[str, ...]
    year: Optional[int]
    container: str
    doi: Optional[str]
    source: str
    url: Optional[str] = None

    def format_chicago(self) -> str:
        """Render a concise Chicago-style bibliographic entry."""
        author_str = ", ".join(self.authors) if self.authors else "Unknown Author"
        year_str = f"({self.year})" if self.year else "(n.d.)"
        doi_str = f" https://doi.org/{self.doi}" if self.doi else ""
        container_part = f" {self.container}." if self.container else ""
        return f"{author_str} {year_str}. {self.title}.{container_part}{doi_str}".strip()


@dataclass(frozen=True)
class VerificationResult:
    """Result of verifying a DOI or ISBN against an authoritative registry."""

    identifier: str
    kind: str  # "DOI" or "ISBN"
    valid: bool
    title: Optional[str] = None
    authors: tuple[str, ...] = ()
    publisher: Optional[str] = None
    year: Optional[int] = None
    detail: str = ""


def _http_get_json(url: str, timeout: int = DEFAULT_TIMEOUT) -> dict[str, Any]:
    """Fetch JSON from an HTTP endpoint with standard User-Agent."""
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        },
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8")
    data: dict[str, Any] = json.loads(raw)
    return data


def normalize_doi(raw: str) -> str:
    """Extract and normalize a bare DOI string."""
    cleaned = raw.strip()
    cleaned = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", cleaned, flags=re.IGNORECASE)
    cleaned = cleaned.rstrip(".,;)")
    return cleaned


def search_crossref(
    query: str,
    rows: int = 10,
    timeout: int = DEFAULT_TIMEOUT,
) -> list[WorkRecord]:
    """Search CrossRef Works API for academic literature."""
    params = urllib.parse.urlencode({"query": query, "rows": str(rows)})
    url = f"https://api.crossref.org/works?{params}"
    payload = _http_get_json(url, timeout=timeout)
    items = payload.get("message", {}).get("items", [])

    results: list[WorkRecord] = []
    for item in items:
        titles = item.get("title") or []
        title = str(titles[0]) if titles else "Untitled"

        authors_raw = item.get("author") or []
        authors: list[str] = []
        for author in authors_raw:
            given = str(author.get("given", "")).strip()
            family = str(author.get("family", "")).strip()
            full = f"{given} {family}".strip()
            if full:
                authors.append(full)

        year: Optional[int] = None
        for date_key in ("published-print", "published-online", "issued"):
            parts = (item.get(date_key) or {}).get("date-parts") or []
            if parts and parts[0]:
                year = int(parts[0][0])
                break

        containers = item.get("container-title") or []
        container = str(containers[0]) if containers else str(item.get("publisher", ""))
        doi = item.get("DOI")
        work_url = item.get("URL")

        results.append(
            WorkRecord(
                title=title,
                authors=tuple(authors),
                year=year,
                container=container,
                doi=str(doi) if doi else None,
                source="CrossRef",
                url=str(work_url) if work_url else None,
            )
        )
    return results


def search_openalex(
    query: str,
    rows: int = 10,
    timeout: int = DEFAULT_TIMEOUT,
) -> list[WorkRecord]:
    """Search OpenAlex Works API for academic literature."""
    params = urllib.parse.urlencode({"search": query, "per-page": str(rows)})
    url = f"https://api.openalex.org/works?{params}"
    payload = _http_get_json(url, timeout=timeout)
    items = payload.get("results", [])

    results: list[WorkRecord] = []
    for item in items:
        title = str(item.get("title") or "Untitled")
        authorships = item.get("authorships") or []
        authors = tuple(
            str((a.get("author") or {}).get("display_name", "")).strip()
            for a in authorships
            if (a.get("author") or {}).get("display_name")
        )
        year_raw = item.get("publication_year")
        year = int(year_raw) if year_raw is not None else None
        primary_loc = item.get("primary_location") or {}
        source_obj = primary_loc.get("source") or {}
        container = str(source_obj.get("display_name") or "")
        doi_raw = item.get("doi")
        doi = normalize_doi(str(doi_raw)) if doi_raw else None

        results.append(
            WorkRecord(
                title=title,
                authors=authors,
                year=year,
                container=container,
                doi=doi,
                source="OpenAlex",
                url=str(item.get("id")) if item.get("id") else None,
            )
        )
    return results


def verify_doi(doi: str, timeout: int = DEFAULT_TIMEOUT) -> VerificationResult:
    """Verify a DOI against the CrossRef REST API."""
    norm = normalize_doi(doi)
    encoded = urllib.parse.quote(norm, safe="")
    url = f"https://api.crossref.org/works/{encoded}"
    try:
        payload = _http_get_json(url, timeout=timeout)
    except urllib.error.HTTPError as exc:
        return VerificationResult(
            identifier=norm,
            kind="DOI",
            valid=False,
            detail=f"HTTP {exc.code}: {exc.reason}",
        )
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(
            identifier=norm,
            kind="DOI",
            valid=False,
            detail=f"Lookup failed: {exc}",
        )

    msg = payload.get("message", {})
    titles = msg.get("title") or []
    title = str(titles[0]) if titles else None
    authors = tuple(
        f"{a.get('given', '')} {a.get('family', '')}".strip()
        for a in (msg.get("author") or [])
        if a.get("family") or a.get("given")
    )
    year: Optional[int] = None
    for date_key in ("published-print", "published-online", "issued"):
        parts = (msg.get(date_key) or {}).get("date-parts") or []
        if parts and parts[0]:
            year = int(parts[0][0])
            break

    publisher = str(msg.get("publisher") or "") or None
    return VerificationResult(
        identifier=norm,
        kind="DOI",
        valid=True,
        title=title,
        authors=authors,
        publisher=publisher,
        year=year,
        detail="Verified via CrossRef REST API",
    )


def validate_isbn(isbn: str) -> bool:
    """Validate an ISBN-10 or ISBN-13 checksum offline."""
    digits = re.sub(r"[^0-9Xx]", "", isbn)
    if len(digits) == 10:
        total = 0
        for idx, ch in enumerate(digits):
            val = 10 if (idx == 9 and ch in ("X", "x")) else (int(ch) if ch.isdigit() else -1)
            if val < 0:
                return False
            total += (10 - idx) * val
        return total % 11 == 0

    if len(digits) == 13 and digits.isdigit():
        total = sum((1 if idx % 2 == 0 else 3) * int(ch) for idx, ch in enumerate(digits[:12]))
        check = (10 - (total % 10)) % 10
        return check == int(digits[12])

    return False


def verify_isbn_openlibrary(isbn: str, timeout: int = DEFAULT_TIMEOUT) -> VerificationResult:
    """Verify an ISBN checksum and optionally query OpenLibrary metadata."""
    cleaned = re.sub(r"[^0-9Xx-]", "", isbn.strip())
    if not validate_isbn(cleaned):
        return VerificationResult(
            identifier=cleaned,
            kind="ISBN",
            valid=False,
            detail="Invalid ISBN-10/ISBN-13 checksum",
        )

    bare = re.sub(r"[^0-9Xx]", "", cleaned)
    url = f"https://openlibrary.org/isbn/{bare}.json"
    try:
        payload = _http_get_json(url, timeout=timeout)
        title = str(payload.get("title") or "") or None
        publishers = payload.get("publishers") or []
        publisher = str(publishers[0]) if publishers else None
        return VerificationResult(
            identifier=cleaned,
            kind="ISBN",
            valid=True,
            title=title,
            publisher=publisher,
            detail="Checksum valid & found in OpenLibrary",
        )
    except urllib.error.HTTPError:
        return VerificationResult(
            identifier=cleaned,
            kind="ISBN",
            valid=True,
            detail="Checksum valid (not indexed in OpenLibrary)",
        )
    except Exception as exc:  # noqa: BLE001
        return VerificationResult(
            identifier=cleaned,
            kind="ISBN",
            valid=True,
            detail=f"Checksum valid (OpenLibrary lookup skipped: {exc})",
        )
