"""Tests for academic API helpers and mocked CrossRef/OpenAlex clients."""

from __future__ import annotations

from typing import Any
from unittest.mock import patch

from sermon_insight.academic_api import (
    normalize_doi,
    search_crossref,
    validate_isbn,
    verify_doi,
)


def test_normalize_doi() -> None:
    assert normalize_doi("https://doi.org/10.1163/ej.9789004206519.i-338.") == (
        "10.1163/ej.9789004206519.i-338"
    )


def test_validate_isbn() -> None:
    assert validate_isbn("978-3-16-133502-0") is True
    assert validate_isbn("978-1-85075-238-7") is True
    assert validate_isbn("978-3-16-133502-9") is False


def test_search_crossref_mocked() -> None:
    fake_response: dict[str, Any] = {
        "message": {
            "items": [
                {
                    "title": ["Keeping His Appointment: Creation and Enthronement in Hebrews"],
                    "author": [{"given": "Kenneth L.", "family": "Schenck"}],
                    "published-print": {"date-parts": [[1997]]},
                    "container-title": ["Journal for the Study of the New Testament"],
                    "DOI": "10.1177/0142064X9701906606",
                }
            ]
        }
    }
    with patch("sermon_insight.academic_api._http_get_json", return_value=fake_response):
        results = search_crossref("Schenck Hebrews", rows=1)

    assert len(results) == 1
    assert results[0].doi == "10.1177/0142064X9701906606"
    assert results[0].year == 1997
    assert "Kenneth L. Schenck" in results[0].format_chicago()


def test_verify_doi_mocked() -> None:
    fake_response: dict[str, Any] = {
        "message": {
            "title": ["Atonement and the Logic of Resurrection in the Epistle to the Hebrews"],
            "author": [{"given": "David M.", "family": "Moffitt"}],
            "published-print": {"date-parts": [[2011]]},
            "publisher": "Brill",
        }
    }
    with patch("sermon_insight.academic_api._http_get_json", return_value=fake_response):
        res = verify_doi("10.1163/ej.9789004206519.i-338")

    assert res.valid is True
    assert res.publisher == "Brill"
    assert res.year == 2011
