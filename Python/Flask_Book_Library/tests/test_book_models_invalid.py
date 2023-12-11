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

    @pytest.fixture
    def example_invalid_data(self):
        pass

    @pytest.fixture(params=[random_valid_string_length])
    def get_random_string(self, request):
        random_string = lambda length: ''.join(choice(ascii_letters) for i in range(length))
        yield random_string(request.param)

    def test_name_incorrect_type(self, example_valid_data):
        _, author, year_published, book_type, status = example_valid_data.values()
        invalid_name = 2
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
        )

    def test_name_out_of_bounds_value(self, example_valid_data):
        pass

    def test_author_incorrect_type(self, example_valid_data):
        pass

    def test_author_out_of_bounds_value(self, example_valid_data):
        pass

    def test_year_published_incorrect_type(self, example_valid_data):
        pass

    def test_year_published_out_of_bounds_value(self, example_valid_data):
        pass

    def test_book_type_incorrect_type(self, example_valid_data):
        pass

    def test_book_type_out_of_bounds_value(self, example_valid_data):
        pass

    def test_status_incorrect_type(self, example_valid_data):
        pass

    def test_status_out_of_bounds_value(self, example_valid_data):
        pass


if __name__ == "__main__":
    raise NotImplementedError("Use run_tests.bash")