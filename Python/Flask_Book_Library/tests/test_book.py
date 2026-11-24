"""Testy jednostkowe modelu Book (project/books/models.py).

Założenia:
* name           - wymagany, niepusty tekst, max 64 znaki, unikalny,
                   bez znaków sterujących oraz kodu SQL/JavaScript,
* author         - opcjonalny tekst, max 64 znaki, bez kodu SQL/JavaScript,
* year_published - liczba całkowita z zakresu 1..bieżący rok,
* book_type      - jedna z wartości: 2days, 5days, 10days,
* status         - domyślnie "available".

Dane uznajemy za odrzucone, jeśli model zgłosi wyjątek przy tworzeniu obiektu
albo baza danych odmówi zapisu. Model nie ma walidacji, więc część testów
celowo nie przechodzi.
"""
import datetime

import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from project.books.models import Book

CURRENT_YEAR = datetime.date.today().year
REJECTION_ERRORS = (ValueError, TypeError, SQLAlchemyError, OverflowError)


@pytest.fixture
def db_session():
    engine = create_engine("sqlite://")
    Book.__table__.create(engine)
    session = Session(engine)
    yield session
    session.close()
    engine.dispose()


def book_data(**overrides):
    data = {
        "name": "Pan Tadeusz",
        "author": "Adam Mickiewicz",
        "year_published": 1834,
        "book_type": "5days",
    }
    data.update(overrides)
    return data


def save_and_reload(session, book):
    session.add(book)
    session.commit()
    book_id = book.id
    session.expunge_all()
    return session.get(Book, book_id)


def assert_rejected(session, **overrides):
    try:
        session.add(Book(**book_data(**overrides)))
        session.flush()
    except REJECTION_ERRORS:
        session.rollback()
        return
    fields = ", ".join(f"{key}={value!r:.60}" for key, value in overrides.items())
    pytest.fail(f"Niepoprawne dane zostały przyjęte i zapisane: {fields}")


class TestValidData:
    def test_creates_book_with_given_data(self):
        book = Book(**book_data())

        assert book.name == "Dziady"
        assert book.author == "Adam Mickiewicz"
        assert book.year_published == 1834
        assert book.book_type == "5days"
        assert book.status == "available"

    def test_saved_book_is_read_back_unchanged(self, db_session):
        loaded = save_and_reload(db_session, Book(**book_data()))

        assert isinstance(loaded.id, int)
        assert (loaded.name, loaded.year_published) == ("Pan Tadeusz", 1834)

    def test_accepts_every_book_type(self, db_session):
        for number, book_type in enumerate(("2days", "5days", "10days")):
            book = Book(**book_data(name=f"Tom {number}", book_type=book_type))

            assert save_and_reload(db_session, book).book_type == book_type

    def test_accepts_apostrophes_and_polish_letters(self, db_session):
        loaded = save_and_reload(
            db_session, Book(**book_data(name="Pan Wołodyjowski", author="Arthur O'Brien"))
        )

        assert (loaded.name, loaded.author) == ("Pan Wołodyjowski", "Arthur O'Brien")

    def test_author_is_optional(self, db_session):
        assert save_and_reload(db_session, Book(**book_data(author=None))).author is None


class TestInvalidData:
    def test_rejects_missing_name(self, db_session):
        assert_rejected(db_session, name=None)

    def test_rejects_blank_name(self, db_session):
        assert_rejected(db_session, name="   ")

    def test_rejects_year_as_text(self, db_session):
        assert_rejected(db_session, year_published="abc")

    def test_rejects_unknown_book_type(self, db_session):
        assert_rejected(db_session, book_type="1day")

    def test_rejects_unknown_status(self, db_session):
        assert_rejected(db_session, status="stolen")

    def test_rejects_duplicate_name(self, db_session):
        db_session.add(Book(**book_data()))
        db_session.flush()
        db_session.add(Book(**book_data(author="Inny Autor")))

        with pytest.raises(IntegrityError):
            db_session.flush()

    def test_rejects_invalid_value_on_update(self, db_session):
        book = Book(**book_data())
        db_session.add(book)
        db_session.flush()

        with pytest.raises(REJECTION_ERRORS):
            book.year_published = "abc"
            db_session.flush()


class TestSqlInjection:
    def test_rejects_drop_table_in_name(self, db_session):
        assert_rejected(db_session, name="'; DROP TABLE books; --")

    def test_rejects_always_true_condition_in_author(self, db_session):
        assert_rejected(db_session, author="' OR '1'='1")

    def test_payload_in_query_is_treated_as_plain_text(self, db_session):
        db_session.add(Book(**book_data()))
        db_session.commit()

        found = db_session.query(Book).filter_by(name="' OR '1'='1").all()

        assert found == []
        assert inspect(db_session.connection()).has_table("books")


class TestJavaScriptInjection:
    def test_rejects_script_tag_in_name(self, db_session):
        assert_rejected(db_session, name="<script>alert('XSS')</script>")

    def test_rejects_event_handler_in_author(self, db_session):
        assert_rejected(db_session, author="<img src=x onerror=alert(1)>")

    def test_rejects_script_on_update(self, db_session):
        book = Book(**book_data())
        db_session.add(book)
        db_session.flush()

        with pytest.raises(REJECTION_ERRORS):
            book.name = "<svg onload=alert(document.cookie)>"
            db_session.flush()


class TestExtremeValues:
    def test_accepts_name_with_max_length(self, db_session):
        assert save_and_reload(db_session, Book(**book_data(name="x" * 64))).name == "x" * 64

    def test_rejects_name_one_char_too_long(self, db_session):
        assert_rejected(db_session, name="x" * 65)

    def test_rejects_huge_name(self, db_session):
        assert_rejected(db_session, name="x" * 1000000)

    def test_accepts_boundary_years(self, db_session):
        for number, year in enumerate((1, CURRENT_YEAR)):
            book = Book(**book_data(name=f"Tom {number}", year_published=year))

            assert save_and_reload(db_session, book).year_published == year

    def test_rejects_future_year(self, db_session):
        assert_rejected(db_session, year_published=CURRENT_YEAR + 1)

    def test_rejects_year_exceeding_64_bits(self, db_session):
        assert_rejected(db_session, year_published=2**63)

    def test_rejects_null_byte_in_name(self, db_session):
        assert_rejected(db_session, name="Pan\x00Tadeusz")
