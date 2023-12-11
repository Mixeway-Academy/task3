import unittest
from project.books.models import Book


class TestBook(unittest.TestCase):

    def __init__(self, methodName: str = "runTest") -> None:
        super().__init__(methodName)
        self.valid_data = {
            "name": "Matematyka wśród nas",
            "author": "Jan Kowalski",
            "year_published": 2020,
            "book_type": "podręcznik",
            "status": None,
        }

    def test_valid_data(self):
        Book(
            name=self.valid_data["name"],
            author=self.valid_data["author"],
            year_published=self.valid_data["year_published"],
            book_type=self.valid_data["book_type"],
            status=self.valid_data["status"],
        )

    def test_invalid_data_type(self):
        with self.assertRaises(ValueError):
            Book(
                name=self.valid_data["name"],
                author=self.valid_data["author"],
                year_published="2020",
                book_type=self.valid_data["book_type"],
                status=self.valid_data["status"],
            )

    def test_invalid_data_length(self):
        with self.assertRaises(ValueError):
            Book(
                name=self.valid_data["name"],
                author=self.valid_data["author"],
                year_published=self.valid_data["year_published"],
                book_type= 25 * "X",
                status=self.valid_data["status"],
            )

    def test_sql_injections(self):
        payloads = ["' OR 1=1; --", "' OR '1", '" or "" "']
        for payload in payloads:
            with self.assertRaises(ValueError):
                Book(
                    name=payload,
                    author=self.valid_data["author"],
                    year_published=self.valid_data["year_published"],
                    book_type=self.valid_data["book_type"],
                    status=self.valid_data["status"],
                )

    def test_xss_injections(self):
        payloads = [
            "<image/src/onerror=prompt(8)>",
            "<script>javascript:alert(1)</script\x0D",
            "‘; alert(1);",
        ]
        for payload in payloads:
            with self.assertRaises(ValueError):
                Book(
                    name=payload,
                    author=self.valid_data["author"],
                    year_published=self.valid_data["year_published"],
                    book_type=self.valid_data["book_type"],
                    status=self.valid_data["status"],
                )

    def test_extreme_data_string(self):
        payloads = [
            100 * "X",
            10000 * "X",
            1000000 * "X",
            100000000 * "X",
            1000000000000 * "X",
        ]
        for payload in payloads:
            with self.assertRaises(ValueError):
                Book(
                    name=payload,
                    author=self.valid_data["author"],
                    year_published=self.valid_data["year_published"],
                    book_type=self.valid_data["book_type"],
                    status=self.valid_data["status"],
                )

    def test_extreme_data_int(self):
        payloads = [
            0,
            10000,
            -10000,
            100000000,
            -100000000,
            1000000000000,
            -1000000000000,
        ]
        for payload in payloads:
            with self.assertRaises(ValueError):
                Book(
                    name=self.valid_data["name"],
                    author=self.valid_data["author"],
                    year_published=self.valid_data["year_published"],
                    book_type=payload,
                    status=self.valid_data["status"],
                )


if __name__ == "__main__":
    unittest.main()
