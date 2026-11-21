import pytest
from project.books.models import Book


# Valid data tests

def test_book_initialization():
    book = Book("The Hobbit", "J.R.R. Tolkien", 1937, "Fantasy")

    assert book.name == "The Hobbit"
    assert book.author == "J.R.R. Tolkien"
    assert book.year_published == 1937
    assert book.book_type == "Fantasy"
    assert book.status == "available"


def test_book_custom_status():
    book = Book("The Hobbit", "J.R.R. Tolkien", 1937, "Fantasy", "borrowed")

    assert book.status == "borrowed"


def test_book_repr():
    book = Book("The Hobbit", "J.R.R. Tolkien", 1937, "Fantasy")

    representation = repr(book)

    assert "The Hobbit" in representation
    assert "J.R.R. Tolkien" in representation
    assert "1937" in representation
    assert "Fantasy" in representation
    assert "available" in representation


# Invalid data tests

@pytest.mark.parametrize("name", [
    "",
    None,
    " ",
    "\n",
    "\t"
])
def test_invalid_book_name(name):
    with pytest.raises(ValueError):
        Book(name, "Author", 2020, "Fantasy")


@pytest.mark.parametrize("author", [
    "",
    None,
    " ",
    "\n",
    "\t"
])
def test_invalid_author(author):
    with pytest.raises(ValueError):
        Book("Book", author, 2020, "Fantasy")


@pytest.mark.parametrize("year", [
    -1,
    0,
    999999,
    "not a year",
    None
])
def test_invalid_year(year):
    with pytest.raises(ValueError):
        Book("Book", "Author", year, "Fantasy")


@pytest.mark.parametrize("book_type", [
    "",
    None,
    " ",
    "Unknown"
])
def test_invalid_book_type(book_type):
    with pytest.raises(ValueError):
        Book("Book", "Author", 2020, book_type)


@pytest.mark.parametrize("status", [
    "",
    None,
    "unknown",
    "invalid_status"
])
def test_invalid_status(status):
    with pytest.raises(ValueError):
        Book("Book", "Author", 2020, "Fantasy", status)


# SQL Injection tests

@pytest.mark.parametrize("malicious_input", [
    "' OR '1'='1",
    "'; DROP TABLE books; --",
    "admin'--",
    "' UNION SELECT * FROM users --",
    "1; DELETE FROM books"
])
def test_sql_injection_in_name(malicious_input):
    with pytest.raises(ValueError):
        Book(malicious_input, "Author", 2020, "Fantasy")


@pytest.mark.parametrize("malicious_input", [
    "' OR '1'='1",
    "'; DROP TABLE books; --",
    "admin'--"
])
def test_sql_injection_in_author(malicious_input):
    with pytest.raises(ValueError):
        Book("Book", malicious_input, 2020, "Fantasy")


# JavaScript Injection tests

@pytest.mark.parametrize("malicious_input", [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "javascript:alert('XSS')",
    "<iframe src='javascript:alert(1)'></iframe>"
])
def test_javascript_injection_in_name(malicious_input):
    with pytest.raises(ValueError):
        Book(malicious_input, "Author", 2020, "Fantasy")


@pytest.mark.parametrize("malicious_input", [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>"
])
def test_javascript_injection_in_author(malicious_input):
    with pytest.raises(ValueError):
        Book("Book", malicious_input, 2020, "Fantasy")


# Extreme input tests

@pytest.mark.parametrize("length", [
    10000,
    100000,
    1000000,
    2000000,
    4000000
])
def test_very_long_book_name(length):
    long_name = "A" * length

    with pytest.raises(ValueError):
        Book(long_name, "Author", 2020, "Fantasy")


@pytest.mark.parametrize("length", [
    10000,
    100000,
    1000000,
    2000000,
    4000000
])
def test_very_long_author_name(length):
    long_author = "A" * length

    with pytest.raises(ValueError):
        Book("Book", long_author, 2020, "Fantasy")


@pytest.mark.parametrize("length", [
    10000,
    100000,
    1000000,
    2000000,
    4000000
])
def test_extremely_long_book_type(length):
    long_type = "A" * length

    with pytest.raises(ValueError):
        Book("Book", "Author", 2020, long_type)


@pytest.mark.parametrize("length", [
    10000,
    100000,
    1000000,
    2000000,
    4000000
])
def test_extremely_long_status(length):
    long_status = "A" * length

    with pytest.raises(ValueError):
        Book("Book", "Author", 2020, "Fantasy", long_status)


def test_unicode_characters():
    book = Book("Książka 日本語 📚", "Autor Żółć", 2020, "Fantastyka")

    assert book.name == "Książka 日本語 📚"
    assert book.author == "Autor Żółć"


def test_large_year_value():
    with pytest.raises(ValueError):
        Book("Future Book", "Author", 2147483647, "Fantasy")


def test_negative_year_value():
    with pytest.raises(ValueError):
        Book("Old Book", "Author", -2147483648, "History")
