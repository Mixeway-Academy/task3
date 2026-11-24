from project.books.models import Book
import pytest

@pytest.mark.parametrize(
    "book_name, author, year_published, book_type",
    [
        ("Book 1", "Author 1", 2020, "Fiction"),
        ("-- Interesting book --", "ONEWORDAUTHOR", 2019, "Non-Fiction"),
        ("Book 3", "Author 3", 2021, "Science Fiction"),
        ("Book 4", "Author 4", 2022, "Mystery"),
        ("!!!!!", "Polish ĄŁTÓR", 2023, "1231455551134"),
        ("Book 5", "Author 5", 1555, "Romance"),
    ],
)
def test_books_creation_correct(book_name, author, year_published, book_type):
    book = Book(name=book_name, author=author, year_published=year_published, book_type=book_type)
    assert book.name == book_name
    assert book.author == author
    assert book.year_published == year_published
    assert book.book_type == book_type

@pytest.mark.parametrize(
    "book_name, author, year_published, book_type",
    [
        ("", "Author 1", 2020, "Fiction"),
        ("Book 1", "", 2020, "Fiction"),
        ("Book 1", "Author 1", "", "Fiction"),
        ("Book 1", "Author 1", 2020, ""),
        (2424, "Author 1", 2020, "Fiction"),
        ("Book 1", 2424, 2020, "Fiction"),
        ("Book 1", "Author 1", "2020", "Fiction"),
        ("Book 1", "Author 1", 2020, 2424),
        (None, "Author 1", 2020, "Fiction"),
        ("Book 1", None, 2020, "Fiction"),
        ("Book 1", "Author 1", None, "Fiction"),
        ("Book 1", "Author 1", 2020, None),
    ],
)
def test_books_creation_incorrect(book_name, author, year_published, book_type):
    with pytest.raises(ValueError):
        Book(name=book_name, author=author, year_published=year_published, book_type=book_type)

def test_books_sql_injection():
    injection_string = "'; DROP TABLE books; --"
    with pytest.raises(Exception):
        Book(name=injection_string, author="Author 1", year_published=2020, book_type="Fiction")
        Book(name="Book 1", author=injection_string, year_published=2020, book_type="Fiction")
        Book(name="Book 1", author="Author 1", year_published=injection_string, book_type="Fiction")
        Book(name="Book 1", author="Author 1", year_published=2020, book_type=injection_string)

def test_books_xss():
    injection_string = "<script>alert('XSS');</script>"
    with pytest.raises(Exception):
        Book(name=injection_string, author="Author 1", year_published=2020, book_type="Fiction")
        Book(name="Book 1", author=injection_string, year_published=2020, book_type="Fiction")
        Book(name="Book 1", author="Author 1", year_published=injection_string, book_type="Fiction")
        Book(name="Book 1", author="Author 1", year_published=2020, book_type=injection_string)

@pytest.mark.parametrize("book_name, author, year_published, book_type", [
    ("AAA"*500, "Author 1", 2020, "Fiction"),
    ("Book 1", "Author 1"*500, 2020, "Fiction"),
    ("Book 1", "Author 1", 2020*500, "Fiction"),
    ("Book 1", "Author 1", 2020, "Fiction"*500),
])
def test_books_extreme(book_name, author, year_published, book_type):
    with pytest.raises(ValueError):
        Book(name=book_name, author=author, year_published=year_published, book_type=book_type)