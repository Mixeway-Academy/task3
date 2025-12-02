import pytest
from ..books.models import Book

# ---------------------------
# TESTY POPRAWNYCH DANYCH
# ---------------------------

def test_create_book_valid():
    book = Book(
        name="Clean Code",
        author="Robert C. Martin",
        year_published=2008,
        book_type="IT",
        status="available"
    )
    assert book.name == "Clean Code"
    assert book.author == "Robert C. Martin"
    assert book.year_published == 2008
    assert book.book_type == "IT"
    assert book.status == "available"

# ---------------------------
# TESTY NIEPOPRAWNYCH DANYCH
# ---------------------------

def test_book_invalid_year_string():
    """rok publikacji jako string – powinno byc int"""
    book = Book(
        name="Some Book",
        author="Author X",
        year_published="2000",  # niepoprawne
        book_type="Drama"
    )
    # Spodziewany fail: Book nie waliduje typow
    assert isinstance(book.year_published, int), "year_published powinien byc int"


def test_book_missing_name():
    """brak nazwy ksiazki"""
    with pytest.raises(TypeError):
        Book(author="A", year_published=1999, book_type="Drama")


def test_book_invalid_status_type():
    """status powinien byc stringiem a tutaj podstawiamy liste"""
    book = Book(
        name="X",
        author="Y",
        year_published=2020,
        book_type="SciFi",
        status=["not", "a", "string"]
    )
    assert isinstance(book.status, str), "status powinien byc stringiem"

# ---------------------------
# TESTY SQL INJECTION
# ---------------------------

def test_sql_injection_in_name():
    payload = "'; DROP TABLE books; --"
    book = Book(
        name=payload,
        author="Attacker",
        year_published=2024,
        book_type="Malicious"
    )
    assert "'" not in book.name or ";" not in book.name, \
        "Pole name powinno odrzucac proby SQL injection"

def test_sql_injection_in_author():
    payload = "\" OR \"1\"=\"1"
    book = Book(
        name="Normal Book",
        author=payload,
        year_published=2024,
        book_type="Malicious"
    )
    assert "OR" not in book.author, \
        "Pole author powinno odrzucac proby SQL injection"

# ---------------------------
# TESTY PROB XSS/JS INJECTION
# ---------------------------

def test_xss_in_name():
    payload = "<script>alert('XSS');</script>"
    book = Book(
        name=payload,
        author="Normal",
        year_published=2024,
        book_type="Drama"
    )
    assert "<script>" not in book.name, \
        "Pole name powinno blokowac kod JavaScript (XSS)."

def test_xss_in_author():
    payload = "<img src=x onerror=alert(1)>"
    book = Book(
        name="Book",
        author=payload,
        year_published=2024,
        book_type="Drama"
    )
    assert "onerror" not in book.author, \
        "Pole author powinno blokowac XSS w atrybutach HTML"

# ---------------------------
# Pozostale testy
# ---------------------------

def test_extreme_long_name():
    long_name = "A" * 10000
    book = Book(
        name=long_name,
        author="Test",
        year_published=2020,
        book_type="Drama"
    )
    assert len(book.name) <= 64, \
        "Pole name nie powinno przyjmowac ekstremalnie dlugich wartosci"


def test_extreme_negative_year():
    book = Book(
        name="Test Book",
        author="Tester",
        year_published=-5000,
        book_type="History"
    )
    assert book.year_published >= 0, \
        "Rok publikacji nie powinien byc ujemny."


def test_extreme_book_type_length():
    long_type = "T" * 500
    book = Book(
        name="Test Book 2",
        author="Tester",
        year_published=2020,
        book_type=long_type
    )
    assert len(book.book_type) <= 20, \
        "Pole book_type powinno miec maksymalnie 20 znakow"
