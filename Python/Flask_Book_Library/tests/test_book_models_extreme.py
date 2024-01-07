import pytest
from random import randint, choice
from string import ascii_letters
from datetime import date

from project.books.models import Book


class Test_Book_Models_Extreme:
    def test_large_strings(self):
        payload = "x" * 100_000_000
        with pytest.raises(ValueError):
            Book(
                name=payload,
                author=payload,
                year_published=2010,
                book_type=payload,
                status=payload
            )

    def test_large_ints(self):
        payload = 100_000 ** 20
        with pytest.raises(ValueError):
            Book(
                name="asd",
                author="asd",
                year_published=payload,
                book_type="asd",
            )


if __name__ == "__main__":
    raise NotImplementedError("Use run_tests.bash")