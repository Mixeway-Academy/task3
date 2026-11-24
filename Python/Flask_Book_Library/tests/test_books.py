import pytest
from project.books.models import Book


def create_book(
    name="The Hobbit",
    author="J.R.R. Tolkien",
    year_published=1937,
    book_type="Fantasy",
    status="available"
):
    return Book(name, author, year_published, book_type, status)


# =================== Testy poprawnych danych =================== #

def test_correct_input():
    book = create_book()

    assert book.name == "The Hobbit"
    assert book.author == "J.R.R. Tolkien"
    assert book.year_published == 1937
    assert book.book_type == "Fantasy"
    assert book.status == "available"


# =================== Testy niepoprawnych danych =================== #

# Niepoprawny tytuł książki
@pytest.mark.parametrize("value", [None, "", "   ", 123, []])
def test_invalid_name(value):
    with pytest.raises((ValueError, TypeError)):
        create_book(name=value)


# =================== Testy warunków brzegowych =================== #

# Poprawna długość tytułu
@pytest.mark.parametrize("length", [1, 63, 64])
def test_valid_name_length(length):
    book = create_book(name="A" * length)

    assert len(book.name) == length


# Niepoprawna długość tytułu
@pytest.mark.parametrize("length", [0, 65])
def test_invalid_name_length(length):
    with pytest.raises(ValueError):
        create_book(name="A" * length)


# =================== Testy ekstremalnych danych =================== #

@pytest.mark.parametrize("length", [
    10_000, 100_000, 1_000_000, 2_000_000, 4_000_000
])
def test_extreme_name(length):
    with pytest.raises(ValueError):
        create_book(name="A" * length)


# =================== Testy SQL Injection =================== #

@pytest.mark.parametrize("value", [
    "' OR '1'='1",
    "' OR 1=1 --",
    "'; DROP TABLE books; --",
    "UNION SELECT * FROM books"
])
def test_sql_injection_name(value):
    with pytest.raises(ValueError):
        create_book(name=value)


# =================== Testy JavaScript Injection (XSS) =================== #

@pytest.mark.parametrize("value", [
    "<script>alert('XSS')</script>",
    "<img src=x onerror=alert(1)>",
    "<svg onload=alert(1)>",
    "javascript:alert(1)"
])
def test_xss_injection_name(value):
    with pytest.raises(ValueError):
        create_book(name=value)
