"""Rozszerzony scenariusz testow jednostkowych dla klasy project.books.models.Book.

Zakres testow (zgodnie z poleceniem):
  1. Testy poprawnych danych
  2. Testy niepoprawnych danych
  3. Testy prob wstrzykniecia kodu SQL i JavaScript
  4. Testy ekstremalne

UWAGA: Celem zadania jest przygotowanie zestawu testow, a NIE poprawianie
definicji klasy Book. Model Book nie waliduje danych, dlatego czesc testow
niepoprawnych/ekstremalnych/wstrzyknieciowych konczy sie niepowodzeniem
(obiekt powstaje mimo niepoprawnych danych). Zgodnie z poleceniem taki test
w tym wypadku MA sie nie udac - to jest oczekiwany wynik, ktory dokumentuje
brak walidacji w modelu.
"""

import datetime

import pytest

from project.books.models import Book

VALID_BOOK_TYPES = ("2days", "5days", "10days")


def _add(session, book):
    session.add(book)
    session.commit()
    return book


# ---------------------------------------------------------------------------
# 1. TESTY POPRAWNYCH DANYCH
# ---------------------------------------------------------------------------
class TestValidData:
    def test_attributes_set_on_construction(self):
        book = Book("The Hobbit", "J.R.R. Tolkien", 1937, "2days")
        assert book.name == "The Hobbit"
        assert book.author == "J.R.R. Tolkien"
        assert book.year_published == 1937
        assert book.book_type == "2days"

    def test_default_status_is_available(self):
        book = Book("Dune", "Frank Herbert", 1965, "5days")
        assert book.status == "available"

    def test_explicit_status_is_kept(self):
        book = Book("1984", "George Orwell", 1949, "10days", status="loaned")
        assert book.status == "loaned"

    def test_persisted_and_queried_back(self, session):
        _add(session, Book("Solaris", "Stanislaw Lem", 1961, "5days"))
        fetched = Book.query.filter_by(name="Solaris").first()
        assert fetched is not None
        assert fetched.id is not None
        assert fetched.author == "Stanislaw Lem"
        assert fetched.year_published == 1961
        assert fetched.book_type == "5days"

    def test_all_valid_book_types_accepted(self, session):
        for i, bt in enumerate(VALID_BOOK_TYPES):
            _add(session, Book(f"Book {i}", "Author", 2000 + i, bt))
        assert Book.query.count() == len(VALID_BOOK_TYPES)


# ---------------------------------------------------------------------------
# 2. TESTY NIEPOPRAWNYCH DANYCH
#    (asercje wymagaja poprawnego zachowania; model Book nie waliduje danych,
#     wiec te testy sa oczekiwanie czerwone)
# ---------------------------------------------------------------------------
class TestInvalidData:
    def test_name_longer_than_column_limit_is_rejected(self, session):
        # name = db.Column(db.String(64)) -> dlugosc > 64 powinna byc odrzucona
        long_name = "x" * 100
        with pytest.raises(Exception):
            _add(session, Book(long_name, "Author", 2000, "2days"))

    def test_name_cannot_be_none(self, session):
        # nazwa jest polem identyfikujacym ksiazke -> None powinien byc odrzucony
        with pytest.raises(Exception):
            _add(session, Book(None, "Author", 2000, "2days"))

    def test_year_published_must_be_integer(self, session):
        # year_published = db.Column(db.Integer) -> tekst powinien byc odrzucony
        with pytest.raises(Exception):
            _add(session, Book("Bad Year", "Author", "not-a-number", "2days"))

    def test_year_published_must_not_be_negative(self, session):
        book = _add(session, Book("Negative Year", "Author", -500, "2days"))
        assert book.year_published >= 0

    def test_book_type_must_be_a_valid_choice(self, session):
        # dozwolone sa tylko wartosci z formularza: 2days/5days/10days
        book = _add(session, Book("Weird Type", "Author", 2000, "forever"))
        assert book.book_type in VALID_BOOK_TYPES

    def test_duplicate_name_is_rejected(self, session):
        # name ma ograniczenie unique=True
        _add(session, Book("Unique Title", "Author", 2000, "2days"))
        with pytest.raises(Exception):
            _add(session, Book("Unique Title", "Other Author", 2001, "5days"))


# ---------------------------------------------------------------------------
# 3. TESTY WSTRZYKNIECIA KODU SQL I JAVASCRIPT
# ---------------------------------------------------------------------------
class TestSqlInjection:
    def test_sql_payload_in_name_is_stored_as_literal_data(self, session):
        payload = "Robert'); DROP TABLE books;--"
        _add(session, Book(payload, "Author", 2000, "2days"))
        # Tabela nadal istnieje i wartosc zostala zapisana doslownie
        fetched = Book.query.filter_by(name=payload).first()
        assert fetched is not None
        assert fetched.name == payload

    def test_table_survives_sql_payload(self, session):
        _add(session, Book("'; DROP TABLE books; --", "Author", 2000, "2days"))
        # Mozna nadal dodawac i odpytywac rekordy -> tabela nie zostala usunieta
        _add(session, Book("Still Here", "Author", 2001, "5days"))
        assert Book.query.count() == 2

    def test_filter_is_not_vulnerable_to_boolean_injection(self, session):
        _add(session, Book("Secret Book", "Author", 2000, "2days"))
        # Klasyczny ' OR '1'='1 nie moze zwrocic wszystkich rekordow
        injected = Book.query.filter_by(name="' OR '1'='1").all()
        assert injected == []


class TestJavaScriptInjection:
    def test_script_payload_is_not_stored_verbatim(self, session):
        # Oczekiwanie: model sanityzuje/odrzuca zawartosc <script>.
        # Model tego nie robi -> test oczekiwanie czerwony (brak sanityzacji).
        payload = "<script>alert('xss')</script>"
        book = _add(session, Book(payload, "Author", 2000, "2days"))
        assert "<script>" not in book.name

    def test_html_event_handler_payload_is_neutralised(self, session):
        payload = "<img src=x onerror=alert(1)>"
        book = _add(session, Book(payload, "Author", 2000, "2days"))
        assert "onerror=" not in book.name


# ---------------------------------------------------------------------------
# 4. TESTY EKSTREMALNE
# ---------------------------------------------------------------------------
class TestExtreme:
    def test_empty_name_is_rejected(self, session):
        book = _add(session, Book("", "Author", 2000, "2days"))
        assert book.name != ""

    def test_extremely_long_name(self, session):
        huge = "A" * 100_000
        with pytest.raises(Exception):
            _add(session, Book(huge, "Author", 2000, "2days"))

    def test_extremely_large_year(self, session):
        book = _add(session, Book("Future Book", "Author", 10**18, "2days"))
        current_year = datetime.date.today().year
        assert book.year_published <= current_year

    def test_extremely_negative_year(self, session):
        book = _add(session, Book("Ancient Book", "Author", -(10**9), "2days"))
        assert book.year_published >= 0

    def test_unicode_and_emoji_name_roundtrip(self, session):
        name = "Zażółć gęślą jaźń 📚🔥 日本語"
        _add(session, Book(name, "Author", 2000, "2days"))
        fetched = Book.query.filter_by(name=name).first()
        assert fetched is not None
        assert fetched.name == name
