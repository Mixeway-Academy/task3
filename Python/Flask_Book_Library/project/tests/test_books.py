import pytest
from project.books.models import Book


def test_create_book():
    book = Book(
        name="Test Book",
        author="Tester",
        year_published=2020,
        book_type="fantasy",
        status="available"
    )

    assert book.name == "Test Book"
    assert book.author == "Tester"
    assert book.year_published == 2020
    assert book.book_type == "fantasy"
    assert book.status == "available"


def test_book_repr():
    book = Book("A", "B", 1999, "thriller")
    rep = repr(book)
    assert "Book(" in rep
    assert "Name: A" in rep


def test_change_status():
    book = Book("Book1", "Author1", 2010, "sci-fi")
    # zakładamy, że domyślnie status to "available"
    assert book.status == "available"
    book.status = "borrowed"
    assert book.status == "borrowed"


def test_create_book2():
	book = Book("Test Book", "Tester", 2020, "fantasy")
	assert book.name == "Test Book"
	assert book.author == "Tester"
	assert book.year_published == 2020
	assert book.book_type == "fantasy"
	assert book.status == "available"


def test_change_status2():
	book = Book("Book1", "Author1", 2010, "sci-fi")
	assert book.status == "available"
	book.status = "borrowed"
	assert book.status == "borrowed"


def test_book_repr2():
	book = Book("A", "B", 1999, "thriller")
	rep = repr(book)
	assert "Book(" in rep
	assert "Name: A" in rep


def test_change_book_type():
	book = Book("BookZ", "AuthorZ", 2015, "horror")
	assert book.book_type == "horror"
	book.book_type = "mystery"
	assert book.book_type == "mystery"


def test_default_status():
	book = Book("BookDefault", "AuthorDefault", 2021, "science")
	assert book.status == "available"


def test_books_equality():
	book1 = Book("SameBook", "SameAuthor", 2022, "romance")
	book2 = Book("SameBook", "SameAuthor", 2022, "romance")
	assert book1 != book2  
