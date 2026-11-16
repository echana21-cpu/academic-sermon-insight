"""Tests for Bible book catalog and passage parser."""

from __future__ import annotations

import pytest

from sermon_insight.books import find_book, parse_passage


def test_find_book_korean_english_and_aliases() -> None:
    heb = find_book("히브리서")
    assert heb is not None
    assert heb.slug == "hebrews"

    rom = find_book("Romans")
    assert rom is not None
    assert rom.ko == "로마서"

    cor1 = find_book("고전")
    assert cor1 is not None
    assert cor1.slug == "1corinthians"


def test_parse_passage_korean() -> None:
    ref = parse_passage("히브리서 8장 1-13절")
    assert ref.book.slug == "hebrews"
    assert ref.chapter == 8
    assert ref.verses == "1-13"
    assert ref.folder_name == "hebrews8_sermon_insight"
    assert ref.prefix_upper == "HEBREWS8"


def test_parse_passage_english() -> None:
    ref = parse_passage("Romans 8")
    assert ref.book.slug == "romans"
    assert ref.chapter == 8
    assert ref.verses is None
    assert ref.title_ko == "로마서 8장"
    assert ref.title_en == "Romans 8"


def test_parse_passage_invalid_raises() -> None:
    with pytest.raises(ValueError):
        parse_passage("UnknownBook 1")
    with pytest.raises(ValueError):
        parse_passage("Romans 0")
