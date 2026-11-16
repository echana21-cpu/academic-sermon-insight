"""Bible book catalog and passage reference parser."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class BibleBook:
    """Represents a canonical Bible book with Korean and English names."""

    slug: str
    en: str
    ko: str
    aliases: tuple[str, ...] = ()


BIBLE_BOOKS: tuple[BibleBook, ...] = (
    # Old Testament
    BibleBook("genesis", "Genesis", "창세기", ("창", "gen")),
    BibleBook("exodus", "Exodus", "출애굽기", ("출", "exod", "ex")),
    BibleBook("leviticus", "Leviticus", "레위기", ("레", "lev")),
    BibleBook("numbers", "Numbers", "민수기", ("민", "num")),
    BibleBook("deuteronomy", "Deuteronomy", "신명기", ("신", "deut", "dt")),
    BibleBook("joshua", "Joshua", "여호수아", ("수", "josh")),
    BibleBook("judges", "Judges", "사사기", ("삿", "judg")),
    BibleBook("ruth", "Ruth", "룻기", ("룻",)),
    BibleBook("1samuel", "1 Samuel", "사무엘상", ("삼상", "1sam", "1 sam")),
    BibleBook("2samuel", "2 Samuel", "사무엘하", ("삼하", "2sam", "2 sam")),
    BibleBook("1kings", "1 Kings", "열왕기상", ("왕상", "1kgs", "1 kgs")),
    BibleBook("2kings", "2 Kings", "열왕기하", ("왕하", "2kgs", "2 kgs")),
    BibleBook("1chronicles", "1 Chronicles", "역대상", ("대상", "1chr", "1 chr")),
    BibleBook("2chronicles", "2 Chronicles", "역대하", ("대하", "2chr", "2 chr")),
    BibleBook("ezra", "Ezra", "에스라", ("스", "ezr")),
    BibleBook("nehemiah", "Nehemiah", "느헤미야", ("느", "neh")),
    BibleBook("esther", "Esther", "에스더", ("에", "esth")),
    BibleBook("job", "Job", "욥기", ("욥",)),
    BibleBook("psalms", "Psalms", "시편", ("시", "ps", "psalm")),
    BibleBook("proverbs", "Proverbs", "잠언", ("잠", "prov")),
    BibleBook("ecclesiastes", "Ecclesiastes", "전도서", ("전", "eccl")),
    BibleBook("songofsolomon", "Song of Solomon", "아가", ("아", "song", "canticles")),
    BibleBook("isaiah", "Isaiah", "이사야", ("사", "isa")),
    BibleBook("jeremiah", "Jeremiah", "예레미야", ("렘", "jer")),
    BibleBook("lamentations", "Lamentations", "예레미야애가", ("애", "lam")),
    BibleBook("ezekiel", "Ezekiel", "에스겔", ("겔", "ezek")),
    BibleBook("daniel", "Daniel", "다니엘", ("단", "dan")),
    BibleBook("hosea", "Hosea", "호세아", ("호", "hos")),
    BibleBook("joel", "Joel", "요엘", ("욜",)),
    BibleBook("amos", "Amos", "아모스", ("암",)),
    BibleBook("obadiah", "Obadiah", "오바댜", ("옵", "obad")),
    BibleBook("jonah", "Jonah", "요나", ("욘",)),
    BibleBook("micah", "Micah", "미가", ("미", "mic")),
    BibleBook("nahum", "Nahum", "나훔", ("나", "nah")),
    BibleBook("habakkuk", "Habakkuk", "하박국", ("합", "hab")),
    BibleBook("zephaniah", "Zephaniah", "스바냐", ("습", "zeph")),
    BibleBook("haggai", "Haggai", "학개", ("학", "hag")),
    BibleBook("zechariah", "Zechariah", "스가랴", ("슥", "zech")),
    BibleBook("malachi", "Malachi", "말라기", ("말", "mal")),
    # New Testament
    BibleBook("matthew", "Matthew", "마태복음", ("마", "matt", "mt")),
    BibleBook("mark", "Mark", "마가복음", ("막", "mk")),
    BibleBook("luke", "Luke", "누가복음", ("눅", "lk")),
    BibleBook("john", "John", "요한복음", ("요", "jn")),
    BibleBook("acts", "Acts", "사도행전", ("행",)),
    BibleBook("romans", "Romans", "로마서", ("롬", "rom")),
    BibleBook("1corinthians", "1 Corinthians", "고린도전서", ("고전", "1cor", "1 cor")),
    BibleBook("2corinthians", "2 Corinthians", "고린도후서", ("고후", "2cor", "2 cor")),
    BibleBook("galatians", "Galatians", "갈라디아서", ("갈", "gal")),
    BibleBook("ephesians", "Ephesians", "에베소서", ("엡", "eph")),
    BibleBook("philippians", "Philippians", "빌립보서", ("빌", "phil")),
    BibleBook("colossians", "Colossians", "골로새서", ("골", "col")),
    BibleBook("1thessalonians", "1 Thessalonians", "데살로니가전서", ("살전", "1thess", "1 thess")),
    BibleBook("2thessalonians", "2 Thessalonians", "데살로니가후서", ("살후", "2thess", "2 thess")),
    BibleBook("1timothy", "1 Timothy", "디모데전서", ("딤전", "1tim", "1 tim")),
    BibleBook("2timothy", "2 Timothy", "디모데후서", ("딤후", "2tim", "2 tim")),
    BibleBook("titus", "Titus", "디도서", ("딛", "tit")),
    BibleBook("philemon", "Philemon", "빌레몬서", ("몬", "phlm")),
    BibleBook("hebrews", "Hebrews", "히브리서", ("히", "heb")),
    BibleBook("james", "James", "야고보서", ("약", "jas")),
    BibleBook("1peter", "1 Peter", "베드로전서", ("벧전", "1pet", "1 pet")),
    BibleBook("2peter", "2 Peter", "베드로후서", ("벧후", "2pet", "2 pet")),
    BibleBook("1john", "1 John", "요한일서", ("요일", "1jn", "1 jn")),
    BibleBook("2john", "2 John", "요한이서", ("요이", "2jn", "2 jn")),
    BibleBook("3john", "3 John", "요한삼서", ("요삼", "3jn", "3 jn")),
    BibleBook("jude", "Jude", "유다서", ("유",)),
    BibleBook("revelation", "Revelation", "요한계시록", ("계", "rev")),
)


def _build_lookup() -> dict[str, BibleBook]:
    """Build normalized name -> BibleBook lookup dictionary."""
    lookup: dict[str, BibleBook] = {}
    for book in BIBLE_BOOKS:
        keys = [book.slug, book.en.lower(), book.ko, *book.aliases]
        for key in keys:
            normalized = re.sub(r"\s+", "", key.lower())
            lookup[normalized] = book
    return lookup


_BOOK_LOOKUP: dict[str, BibleBook] = _build_lookup()


@dataclass(frozen=True)
class PassageRef:
    """Parsed biblical passage reference."""

    book: BibleBook
    chapter: int
    verses: Optional[str] = None

    @property
    def folder_name(self) -> str:
        """Return standard folder name, e.g. ``hebrews8_sermon_insight``."""
        return f"{self.book.slug}{self.chapter}_sermon_insight"

    @property
    def prefix_upper(self) -> str:
        """Return uppercase file prefix, e.g. ``HEBREWS8``."""
        return f"{self.book.slug.upper()}{self.chapter}"

    @property
    def title_ko(self) -> str:
        """Return Korean passage title, e.g. ``히브리서 8장`` or ``히브리서 8장 1-13절``."""
        if self.verses:
            return f"{self.book.ko} {self.chapter}장 {self.verses}절"
        return f"{self.book.ko} {self.chapter}장"

    @property
    def title_en(self) -> str:
        """Return English passage title, e.g. ``Hebrews 8`` or ``Hebrews 8:1-13``."""
        if self.verses:
            return f"{self.book.en} {self.chapter}:{self.verses}"
        return f"{self.book.en} {self.chapter}"


_PASSAGE_RE = re.compile(
    r"^\s*([1-3]?\s*[A-Za-z가-힣]+?)\s*(\d+)\s*(?:장|:)?\s*(?:(\d+(?:\s*[-–~]\s*\d+)?)\s*절?)?\s*$"
)


def find_book(name: str) -> Optional[BibleBook]:
    """Find a BibleBook by English name, Korean name, slug, or alias."""
    normalized = re.sub(r"\s+", "", name.strip().lower())
    return _BOOK_LOOKUP.get(normalized)


def parse_passage(raw: str) -> PassageRef:
    """Parse a Korean or English passage string into a ``PassageRef``.

    Examples:
        - ``"로마서 8장"``
        - ``"히브리서 8장 1-13절"``
        - ``"Romans 8"``
        - ``"Hebrews 8:1-13"``
    """
    match = _PASSAGE_RE.match(raw)
    if not match:
        raise ValueError(f"Could not parse passage reference: {raw!r}")

    book_raw, chapter_str, verses_raw = match.groups()
    book = find_book(book_raw)
    if book is None:
        raise ValueError(f"Unknown Bible book: {book_raw!r}")

    chapter = int(chapter_str)
    if chapter <= 0:
        raise ValueError(f"Chapter must be positive, got {chapter}")

    verses: Optional[str] = None
    if verses_raw:
        verses = re.sub(r"\s*[–~]\s*", "-", verses_raw.strip())

    return PassageRef(book=book, chapter=chapter, verses=verses)
