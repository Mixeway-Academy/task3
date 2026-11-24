import pytest
from project.books.models import Book


def test_valid_book_sets_attributes():
    book = Book("Red Rising", "Pierce Brown", 2014, "5days")
    assert book.name == "Red Rising"
    assert book.author == "Pierce Brown"
    assert book.year_published == 2014
    assert book.book_type == "5days"


def test_valid_book_default_status():
    book = Book("Golden Son", "Pierce Brown", 2015, "10days")
    assert book.status == "available"


def test_valid_book_repr_contains_fields():
    book = Book("Morning Star", "Pierce Brown", 2016, "2days")
    repr_text = repr(book)
    assert "Morning Star" in repr_text
    assert "2016" in repr_text


def test_valid_book_persists_and_retrieves(session):
    book = Book("Iron Gold", "Pierce Brown", 2018, "5days")
    session.add(book)
    session.commit()
    fetched = Book.query.filter_by(name="Iron Gold").first()
    assert fetched is not None
    assert fetched.author == "Pierce Brown"
    assert fetched.year_published == 2018


def test_empty_name_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        Book("", "Author", 2020, "5days")


def test_none_year_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        Book("Title", "Author", None, "5days")


def test_non_numeric_year_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        Book("Title", "Author", "not a year", "5days")


def test_name_over_limit_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        Book("A" * 65, "Author", 2020, "5days")


def test_invalid_book_type_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        Book("Title", "Author", 2020, "not-a-type")


def test_sql_injection_name_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        Book("'; DROP TABLE books; --", "Author", 2020, "5days")


def test_xss_injection_name_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        Book("<script>alert('XSS')</script>", "Author", 2020, "5days")


def test_extreme_length_name_is_rejected():
    with pytest.raises((ValueError, TypeError)):
        Book("A" * 1_000_000, "Author", 2020, "5days")
