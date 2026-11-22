
import pytest

from project.books.models import Book


# ==================================================
# 1. POPRAWNE DANE
# ==================================================

def test_valid_book():
    book = Book(
        name="Harry Potter",
        author="J.K. Rowling",
        year_published=1997,
        book_type="Fantasy"
    )

    assert book.name == "Harry Potter"
    assert book.author == "J.K. Rowling"
    assert book.year_published == 1997
    assert book.status == "available"


# ==================================================
# 2. NIEPOPRAWNE DANE
# ==================================================

@pytest.mark.parametrize("name, author, year, book_type", [
    ("", "John Smith", 2000, "Novel"),
    ("Book", "", 2000, "Novel"),
    ("Book", "John Smith", -100, "Novel"),
    ("Book", "John Smith", "abc", "Novel"),
    ("Book", "John Smith", 2000, ""),
])
def test_invalid_book_data(name, author, year, book_type):
    with pytest.raises((ValueError, TypeError)):
        Book(name, author, year, book_type)


# ==================================================
# 3. SQL INJECTION
# ==================================================

@pytest.mark.parametrize("payload", [
    "' OR 1=1 --",
    "'; DROP TABLE books; --",
])
def test_sql_injection(payload):
    with pytest.raises(ValueError):
        Book(payload, "John Smith", 2000, "Novel")


# ==================================================
# 4. JAVASCRIPT INJECTION
# ==================================================

@pytest.mark.parametrize("payload", [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
])
def test_javascript_injection(payload):
    with pytest.raises(ValueError):
        Book(payload, "John Smith", 2000, "Novel")


# ==================================================
# 5. WARUNKI BRZEGOWE
# ==================================================

def test_maximum_book_name_length():
    book = Book("A" * 64, "John Smith", 2000, "Novel")

    assert len(book.name) == 64


def test_exceeding_book_name_length():
    with pytest.raises(ValueError):
        Book("A" * 65, "John Smith", 2000, "Novel")


# ==================================================
# 6. DANE EKSTREMALNE
# ==================================================

def test_extremely_long_book_name():
    with pytest.raises(ValueError):
        Book("A" * 10_000_000, "John Smith", 2000, "Novel")
