import pytest
from project.books.models import Book


# testy poprawne
@pytest.mark.parametrize(
    "name, author, year, book_type",
    [
        ("Lalka", "Bolesław Prus", 1890, "5days"),
        ("Pan Tadeusz", "Adam Mickiewicz", 1834, "2days"),
        ("Wiedźmin", "Andrzej Sapkowski", 1990, "10days"),
        ("1984", "George Orwell", 1949, "5days"),  # same cyfry
        (
            "Alice's Adventures in Wonderland",
            "Lewis Carroll",
            1865,
            "5days",
        ),  # apostrof
    ],
)
def test_valid_book(name, author, year, book_type):
    book = Book(name, author, year, book_type)

    assert book.name == name
    assert book.author == author
    assert book.year_published == year
    assert book.book_type == book_type
    assert book.status == "available"


def test_valid_book_status_has_given_attreibures():
    data = dict(
        name="Lalka",
        author="Bolesław Prus",
        year_published=1890,
        book_type="novel",
        status="unavailable",
    )
    book = Book(**data)

    assert book.name == "Lalka"
    assert book.author == "Bolesław Prus"
    assert book.year_published == 1890
    assert book.book_type == "novel"
    assert book.status == "unavailable"


# testy niepoprawne
def test_empty_book_fields_has_given_attreibures():
    data = dict(name="", author="", year_published=2000, book_type="")
    book = Book(**data)

    assert book.name == ""
    assert book.author == ""
    assert book.year_published == 2000
    assert book.book_type == ""


@pytest.mark.parametrize("year", [0.5, 3.1415, None, "1234", True, -1, "rok", 123456])
def test_invalid_year_is_rejected(year):
    data = dict(name="name", author="author", year_published=year, book_type="type")

    # test nie przejdzie, bo Book nie rzuca wyjatku
    with pytest.raises(ValueError):
        Book(**data)


@pytest.mark.parametrize("name", ["", None, "      ", 1])
def test_invalid_name_is_rejected(name):
    data = dict(name=name, author="author", year_published=2000, book_type="type")

    # test nie przejdzie, bo Book nie rzuca wyjatku
    with pytest.raises(ValueError):
        Book(**data)


@pytest.mark.parametrize("author", ["", None, "      ", 1])
def test_invalid_name_is_rejected(author):
    data = dict(name="name", author=author, year_published=2000, book_type="type")

    # test nie przejdzie, bo Book nie rzuca wyjatku
    with pytest.raises(ValueError):
        Book(**data)


# testy wstrzykniecie


@pytest.mark.parametrize(
    "payload",
    [
        "'; DROP TABLE books;--",
        "' OR '1'='1",
        "Lalka'; DELETE FROM books WHERE '1'='1",
        "1 UNION SELECT * FROM customers--",
    ],
)
def test_sql_injection_in_name(session, payload):
    book = Book(payload, "Bolesław Prus", 1890, "5days")
    session.add(book)
    session.flush()

    found = Book.query.filter_by(name=payload).first()

    assert found is not None
    assert found.name == payload


@pytest.mark.parametrize(
    "payload",
    [
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(1)",
    ],
)
def test_javascript_in_name_is_rejected(payload):
    with pytest.raises(ValueError):
        Book(payload, "Bolesław Prus", 1890, "5days")


# testy wytrzymałościowe
@pytest.mark.parametrize("length", [65, 1000, 1_000_000])
def test_too_long_name_is_rejected(length):
    with pytest.raises(ValueError):
        Book("x" * length, "Bolesław Prus", 1890, "5days")


@pytest.mark.parametrize("length", [65, 1000, 1_000_000])
def test_too_long_title_is_rejected(length):
    with pytest.raises(ValueError):
        Book("Lalka", "x" * length, 1890, "5days")


@pytest.mark.parametrize("year", [2**63, -(2**63) - 1, 10**100])
def test_huge_year_rejected(session, year):
    session.add(Book("Lalka", "Bolesław Prus", year, "5days"))

    with pytest.raises(OverflowError):
        session.flush()


@pytest.mark.parametrize(
    "name",
    [
        "\x00",
        "Lalka\nPrus",
        "\u202eakllaL",
    ],
)
def test_unusual_chars_rejected(name):
    with pytest.raises(ValueError):
        Book(name, "Bolesław Prus", 1890, "5days")


def test_many_books_can_be_saved(session):
    for i in range(100_000):
        session.add(Book(f"Książka {i}", "Autor", 1900, "5days"))
    session.flush()

    assert Book.query.count() >= 100_000


# testy edge case
# name: od 1 do 64 znaków
# author: od 2 do 64 znaków

TITLE_MIN = 1
TITLE_MAX = 64
AUTHOR_MIN = 2
AUTHOR_MAX = 64


@pytest.mark.parametrize(
    "length", [TITLE_MIN, TITLE_MIN + 1, TITLE_MAX - 1, TITLE_MAX]
)
def test_title_length_on_boundary_is_accepted(length):
    title = "x" * length

    book = Book(title, "Bolesław Prus", 1890, "5days")

    assert book.name == title


@pytest.mark.parametrize("length", [TITLE_MIN - 1, TITLE_MAX + 1])
def test_title_length_outside_boundary_is_rejected(length):
    # test nie przejdzie, bo Book nie sprawdza długości tytułu
    with pytest.raises(ValueError):
        Book("x" * length, "Bolesław Prus", 1890, "5days")


@pytest.mark.parametrize(
    "length", [AUTHOR_MIN, AUTHOR_MIN + 1, AUTHOR_MAX - 1, AUTHOR_MAX]
)
def test_author_length_on_boundary_is_accepted(length):
    author = "x" * length

    book = Book("Lalka", author, 1890, "5days")

    assert book.author == author


@pytest.mark.parametrize("length", [0, AUTHOR_MIN - 1, AUTHOR_MAX + 1])
def test_author_length_outside_boundary_is_rejected(length):
    # test nie przejdzie, bo Book nie sprawdza długości autora
    with pytest.raises(ValueError):
        Book("Lalka", "x" * length, 1890, "5days")


def test_title_and_author_at_max_length_can_be_saved(session):
    title = "t" * TITLE_MAX
    author = "a" * AUTHOR_MAX
    session.add(Book(title, author, 1890, "5days"))
    session.flush()

    found = Book.query.filter_by(name=title).first()

    assert found is not None
    assert found.author == author
