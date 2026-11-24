"""Minimal unit tests for the Book model (project/books/models.py).

Covers the scope required by task 1: valid data, invalid data,
SQL injection, JavaScript (XSS) injection and extreme values.
"""

import pytest
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError

from project import app, db
from project.books.models import Book

VALID = {"name": "Wiedzmin", "author": "Andrzej Sapkowski", "year_published": 1990, "book_type": "10days"}


@pytest.fixture(autouse=True)
def fresh_db():
    with app.app_context():
        db.drop_all()
        db.create_all()
    yield
    with app.app_context():
        db.session.remove()


def make_book(**overrides):
    return Book(**{**VALID, **overrides})


# valid data
def test_valid_book_is_saved_with_default_status():
    with app.app_context():
        book = make_book()
        db.session.add(book)
        db.session.commit()
        stored = Book.query.one()
        assert book.id is not None
        assert stored.name == "Wiedzmin"
        assert stored.author == "Andrzej Sapkowski"
        assert stored.year_published == 1990
        assert stored.book_type == "10days"
        assert stored.status == "available"


# invalid data
def test_missing_arguments_are_rejected():
    with pytest.raises(TypeError):
        Book(name="Only name")


def test_duplicate_name_is_rejected():
    with app.app_context():
        db.session.add(make_book())
        db.session.commit()
        db.session.add(make_book(author="Someone else"))
        with pytest.raises(IntegrityError):
            db.session.commit()
        db.session.rollback()
        assert Book.query.count() == 1


# SQL injection
def test_sql_injection_payload_is_stored_as_text():
    payload = "'; DROP TABLE books; --"
    with app.app_context():
        db.session.add(make_book(name=payload))
        db.session.commit()
        assert Book.query.one().name == payload
        assert db.session.execute(text("SELECT COUNT(*) FROM books")).scalar() == 1


# JavaScript (XSS) injection
def test_xss_payload_is_returned_as_data():
    payload = "<script>alert('XSS')</script>"
    with app.app_context():
        db.session.add(make_book(name=payload))
        db.session.commit()
        response = app.test_client().get("/books/json")
        assert response.status_code == 200
        assert payload in response.get_data(as_text=True)


# extreme values
def test_extreme_values_are_handled():
    with app.app_context():
        db.session.add(make_book(name="A" * 10_000, year_published=2**63 - 1))
        db.session.commit()
        stored = Book.query.one()
        assert stored.name == "A" * 10_000
        assert stored.year_published == 2**63 - 1
