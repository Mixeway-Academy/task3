import os
import sys

# Use an isolated in-memory database so tests never touch project/data.sqlite.
# Must be set before `project` is imported.
os.environ["DATABASE_URL"] = "sqlite:///:memory:"
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest

from project import app as flask_app, db
from project.books.models import Book


@pytest.fixture()
def session():
    """Fresh schema for every test, inside an application context."""
    flask_app.config["TESTING"] = True
    with flask_app.app_context():
        db.drop_all()
        db.create_all()
        yield db.session
        db.session.rollback()
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def make_book(session):
    """Create a Book with valid defaults, override any field, persist it and reload it from the DB."""

    def _make(**overrides):
        data = {
            "name": "The Pragmatic Programmer",
            "author": "Andrew Hunt",
            "year_published": 1999,
            "book_type": "5days",
        }
        data.update(overrides)
        book = Book(**data)
        session.add(book)
        session.commit()
        book_id = book.id
        session.expire_all()
        return session.get(Book, book_id)

    return _make
