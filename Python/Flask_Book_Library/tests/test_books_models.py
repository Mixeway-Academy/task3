import os
import sys

import pytest

TESTS_DIR = os.path.dirname(__file__)
PROJECT_ROOT = os.path.abspath(os.path.join(TESTS_DIR, os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from project.books.models import Book  # noqa: E402


def test_correct_create_book():
    book = Book(name="Land", author="Grzegorz", year_published=2004, book_type="fiction")
    assert book.name == "Land"
    assert book.author == "Grzegorz"
    assert book.year_published == 2004
 
def test_empty_title_create_book():
    with pytest.raises(ValueError) as excinfo:
        Book(name="", author="Grzegorz", year_published=2004, book_type="fiction")

def test_sql_injection():
    payload = "Grzegorz'); DROP TABLE Books;--"
    book = Book(name=payload, author="Hacker", year_published=2020, book_type="fiction")
    assert book.name == payload

def test_xss_injection():
    payload = "<script>alert('XSS')</script>"
    book = Book(name=payload, author="Hacker", year_published=2020, book_type="fiction")
    assert book.name == payload

def test_too_long_title():
    long_title = "A" * 300
    with pytest.raises(ValueError) as excinfo:
        Book(name=long_title, author="Grzegorz", year_published=2004, book_type="fiction")