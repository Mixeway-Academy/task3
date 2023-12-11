import pytest
from random import randint, choice
from string import ascii_letters
from datetime import date

from project.books.models import Book

# constants
MAX_NAME_LENGTH = 64
MAX_AUTHOR_LENGTH = 64
MAX_BOOK_TYPE_LENGTH = 20
MAX_STATUS_LENGTH = 20
MAX_YEAR_PUBLISHED = date.today().year
ITERATIONS_PER_TEST = 10

random_valid_string_length = randint(1, 20)
random_valid_year_published = randint(1439, MAX_YEAR_PUBLISHED) # Since Gutenberg invention

class Test_Book_Models_Extreme: 
    @pytest.fixture
    def example_valid_data(self):
        return {
            "name": "The Great Book",
            "author": "John Doe",
            "year_published": 1998,
            "book_type": "poem",
            "status": "not available"
        }

    @pytest.fixture(params=[random_valid_string_length])
    def get_random_string(self, request):
        random_string = lambda length: ''.join(choice(ascii_letters) for i in range(length))
        yield random_string(request.param)

    def test_example_valid_data(self, example_valid_data):
        book = Book(**example_valid_data)
        assert book.author == "John Doe"

    def test_name_random_str(self, example_valid_data, get_random_string):
        _, author, year_published, book_type, status = example_valid_data.values()
        name = get_random_string
        for _ in range(0, ITERATIONS_PER_TEST):
            book = Book(
                name=name,
                author=author,
                year_published=year_published,
                book_type=book_type,
                status=status
            )
            assert isinstance(book.name, str)
            assert book.name == name
            assert len(book.name) <= MAX_NAME_LENGTH and len(book.name) > 0

    def test_name_max_length(self, example_valid_data):
        _, author, year_published, book_type, status = example_valid_data.values()
        name = "x" * MAX_NAME_LENGTH
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
            status=status
        )
        assert isinstance(book.name, str)
        assert book.name == name
        assert len(book.name) == MAX_NAME_LENGTH

    def test_name_min_length(self, example_valid_data):
        _, author, year_published, book_type, status = example_valid_data.values()
        name = "x"
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
            status=status
        )
        assert isinstance(book.name, str)
        assert book.name == name
        assert len(book.name) > 0

    def test_author_random_str(self, example_valid_data, get_random_string):
        name, _, year_published, book_type, status = example_valid_data.values()
        author = get_random_string
        for _ in range(0, ITERATIONS_PER_TEST):
            book = Book(
                name=name,
                author=author,
                year_published=year_published,
                book_type=book_type,
                status=status
            )
            assert isinstance(book.author, str)
            assert book.author == author
            assert len(book.author) <= MAX_AUTHOR_LENGTH and len(book.author) > 0

    def test_author_max_length(self, example_valid_data):
        name, _, year_published, book_type, status = example_valid_data.values()
        author = "x" * MAX_AUTHOR_LENGTH
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
            status=status
        )
        assert isinstance(book.author, str)
        assert book.author == author
        assert len(book.author) == MAX_AUTHOR_LENGTH

    def test_author_min_length(self, example_valid_data):
        name, _, year_published, book_type, status = example_valid_data.values()
        author = "x"
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
            status=status
        )
        assert isinstance(book.author, str)
        assert book.author == author
        assert len(book.author) > 0

    def test_year_published(self, example_valid_data):
        name, author, _, book_type, status = example_valid_data.values()
        year_published = random_valid_year_published
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
            status=status
        )
        assert isinstance(book.year_published, int)
        assert book.year_published == year_published
        assert book.year_published <= MAX_YEAR_PUBLISHED

    def test_book_type_random_str(self, example_valid_data, get_random_string):
        name, author, year_published, _, status = example_valid_data.values()
        book_type = get_random_string
        for _ in range(0, ITERATIONS_PER_TEST):
            book = Book(
                name=name,
                author=author,
                year_published=year_published,
                book_type=book_type,
                status=status
            )
            assert isinstance(book.book_type, str)
            assert book.book_type == book_type
            assert len(book.book_type) <= MAX_BOOK_TYPE_LENGTH and len(book.book_type) > 0

    def test_book_type_max_length(self, example_valid_data):
        name, author, year_published, _, status = example_valid_data.values()
        book_type = "x" * MAX_BOOK_TYPE_LENGTH
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
            status=status
        )
        assert isinstance(book.book_type, str)
        assert book.book_type == book_type
        assert len(book.book_type) == MAX_BOOK_TYPE_LENGTH

    def test_book_type_min_length(self, example_valid_data):
        name, author, year_published, _, status = example_valid_data.values()
        book_type = "x" * MAX_BOOK_TYPE_LENGTH
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
            status=status
        )
        assert isinstance(book.book_type, str)
        assert book.book_type == book_type
        assert len(book.book_type) > 0

    def test_status_random_str(self, example_valid_data, get_random_string):
        name, author, year_published, book_type, _ = example_valid_data.values()
        status = get_random_string
        for _ in range(0, ITERATIONS_PER_TEST):
            book = Book(
                name=name,
                author=author,
                year_published=year_published,
                book_type=book_type,
                status=status
            )
            assert isinstance(book.status, str)
            assert book.status == status
            assert len(book.status) <= MAX_STATUS_LENGTH and len(book.status) > 0

    def test_no_status_provided(self, example_valid_data):
        name, author, year_published, book_type, _ = example_valid_data.values()
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
        )
        assert book.status == "available" 
    
    

if __name__ == "__main__":
    raise NotImplementedError("Use run_tests.bash")