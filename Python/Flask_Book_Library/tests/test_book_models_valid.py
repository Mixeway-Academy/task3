import pytest

from project.books.models import Book

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

    x = ["1", "2", "3"]

    @pytest.fixture(params=x)
    def get_random_string(self, request):
        yield request.param

    def test_example_valid_data(self, example_valid_data):
        x = Book(**example_valid_data)
        assert x.author == "John Doe"

    def test_name(self, example_valid_data, get_random_string):
        _, author, year_published, book_type, status = example_valid_data.values()
        for _ in range(0, 5):
            x = Book(
                name='ok',
                author=author,
                year_published=year_published,
                book_type=book_type,
                status=status
            )
            assert isinstance(get_random_string, str)

if __name__ == "__main__":
    raise NotImplementedError("Use run_tests.bash")