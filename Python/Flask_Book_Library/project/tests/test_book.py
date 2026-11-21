import pytest
from project.books.models import Book


@pytest.mark.parametrize(
    "name, author, year_published, book_type, status",
    [
        ("Clean Code", "Robert C. Martin", 2008, "tech", "available"),
        ("Design Patterns", "Gamma et al.", 1994, "tech", None),
        ("A" * 64, "Autor", 2020, "fiction", "borrowed"), 
        ("B", "J", 0, "other", "available"),
    ],
)
def test_book_valid_data(name, author, year_published, book_type, status):
    if status is None:
        book = Book(name=name, author=author, year_published=year_published, book_type=book_type)
        assert book.status == "available"
    else:
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
            status=status,
        )
        assert book.status == status

    assert book.name == name
    assert book.author == author
    assert book.year_published == year_published
    assert book.book_type == book_type


@pytest.mark.parametrize(
    "name, author, year_published, book_type",
    [
        (None, "Autor", 2020, "fiction"),
        ("", "Autor", 2020, "fiction"),
        ("   \n\t  ", "Autor", 2020, "fiction"),
        ("Tytuł", None, 2020, "fiction"),
        ("Tytuł", "Autor", -1, "fiction"),
        ("Tytuł", "Autor", "nie_rok", "fiction"),
        ("Tytuł", "Autor", 2020, None),
    ],
)
def test_book_invalid_data(name, author, year_published, book_type):
    with pytest.raises((ValueError, TypeError)):
        Book(name=name, author=author, year_published=year_published, book_type=book_type)


@pytest.mark.parametrize(
    "payload",
    [
        # SQL Injection (bezpieczne stringi testowe)
        "' OR '1'='1",
        "-- or #",
        "1' UNION SELECT '2",
        "1' ORDER BY 1--+",
        '" OR 1=1 --',
        # XSS / JavaScript
        "<script>alert(1)</script>",
        '<img src=x onerror="alert(1)">',
        '"><script>javascript:alert(1)</script>',
        "javascript:alert(document.cookie)",
    ],
)
def test_book_sqli_and_xss_payloads_rejected(payload):
    with pytest.raises((ValueError, TypeError)):
        Book(name=payload, author="Autor", year_published=2022, book_type="tech")

    with pytest.raises((ValueError, TypeError)):
        Book(name="Poprawny tytuł", author=payload, year_published=2022, book_type="tech")


@pytest.mark.parametrize(
    "extreme_text",
    [
        "X" * 10_000,
        "X" * 100_000,
        "X" * 1_000_000,
        "X" * 4_000_000,
    ],
    ids=["len_10k", "len_100k", "len_1M", "len_4M"],
)
def test_book_extreme_input_lengths(extreme_text):
    with pytest.raises((ValueError, TypeError, OverflowError)):
        Book(name=extreme_text, author="Autor", year_published=2022, book_type="tech")