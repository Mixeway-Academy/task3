
import unittest
import datetime

from project.books.models import Book


CURRENT_YEAR = datetime.date.today().year


class BookTests(unittest.TestCase):

    def create_book(self, **kwargs):
        """Tworzy obiekt Book z domyślnymi danymi."""
        data = {
            "name": "W pustyni i w puszczy",
            "author": "Henryk Sienkiewicz",
            "year_published": 1911,
            "book_type": "2days",
            "status": "available"
        }

        data.update(kwargs)
        return Book(**data)

    def test_create_book_with_valid_data(self):
        book = self.create_book()

        self.assertEqual(book.name, "W pustyni i w puszczy")
        self.assertEqual(book.author, "Henryk Sienkiewicz")
        self.assertEqual(book.year_published, 1911)
        self.assertEqual(book.book_type, "2days")
        self.assertEqual(book.status, "available")

    def test_create_book_with_different_data(self):
        book = self.create_book(
            name="Hobbit",
            author="J.R.R. Tolkien",
            year_published=1937,
            book_type="5days",
            status="loaned"
        )

        self.assertEqual(book.name, "Hobbit")
        self.assertEqual(book.author, "J.R.R. Tolkien")
        self.assertEqual(book.year_published, 1937)

    def test_default_status(self):
        book = Book(
            "Lalka",
            "Bolesław Prus",
            1890,
            "10days"
        )

        self.assertEqual(book.status, "available")

    def test_short_name(self):
        book = self.create_book(name="A")
        self.assertEqual(book.name, "A")

    def test_maximum_name_length(self):
        name = "B" * 64
        book = self.create_book(name=name)

        self.assertEqual(len(book.name), 64)

    def test_polish_characters(self):
        book = self.create_book(
            name="Zażółć gęślą jaźń",
            author="Łukasz Żółkiewski"
        )

        self.assertEqual(book.name, "Zażółć gęślą jaźń")
        self.assertEqual(book.author, "Łukasz Żółkiewski")

    def test_book_representation(self):
        book = self.create_book()
        representation = repr(book)

        self.assertIn("W pustyni i w puszczy", representation)
        self.assertIn("Henryk Sienkiewicz", representation)

    def test_invalid_names(self):
        invalid_values = [
            None,
            "",
            " ",
            "\t",
            "\n",
            123,
            45.67,
            [],
            {},
            True,
            "N" * 65
        ]

        for value in invalid_values:
            with self.subTest(name=value):
                with self.assertRaises(Exception):
                    self.create_book(name=value)

    def test_invalid_authors(self):
        invalid_values = [
            None,
            "",
            " ",
            123,
            10.5,
            [],
            {},
            False,
            "A" * 65
        ]

        for value in invalid_values:
            with self.subTest(author=value):
                with self.assertRaises(Exception):
                    self.create_book(author=value)

    def test_invalid_publication_year(self):
        invalid_values = [
            None,
            "abc",
            "2000",
            -1,
            0,
            CURRENT_YEAR + 1,
            999999,
            2000.5,
            float("inf"),
            float("nan"),
            [],
            {}
        ]

        for value in invalid_values:
            with self.subTest(year=value):
                with self.assertRaises(Exception):
                    self.create_book(year_published=value)

    def test_invalid_book_types(self):
        invalid_values = [
            None,
            "",
            " ",
            "1day",
            "20days",
            "2DAYS",
            "unknown",
            123,
            [],
            "X" * 21
        ]

        for value in invalid_values:
            with self.subTest(book_type=value):
                with self.assertRaises(Exception):
                    self.create_book(book_type=value)

    def test_invalid_statuses(self):
        invalid_values = [
            None,
            "",
            " ",
            "unknown",
            "deleted",
            "AVAILABLE",
            123,
            [],
            "X" * 21
        ]

        for value in invalid_values:
            with self.subTest(status=value):
                with self.assertRaises(Exception):
                    self.create_book(status=value)

    def test_sql_injection_in_name(self):
        attacks = [
            "' OR '1'='1",
            "'; DROP TABLE books; --",
            "admin'--",
            "1' UNION SELECT * FROM users --",
            "' OR 1=1; DELETE FROM books; --",
            "1' ORDER BY 1--",
            "'; UPDATE books SET status='deleted'; --"
        ]

        for attack in attacks:
            with self.subTest(payload=attack):
                with self.assertRaises(Exception):
                    self.create_book(name=attack)

    def test_sql_injection_in_author(self):
        payloads = [
            "' OR 1=1 --",
            "'; DROP TABLE users; --",
            "admin' OR 'x'='x",
            "UNION SELECT password FROM users"
        ]

        for payload in payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(Exception):
                    self.create_book(author=payload)

    def test_sql_injection_in_book_type(self):
        payload = "'; DROP TABLE books; --"

        with self.assertRaises(Exception):
            self.create_book(book_type=payload)

    def test_xss_in_name(self):
        payloads = [
            "<script>alert(1)</script>",
            "<img src=x onerror=alert(1)>",
            "<svg onload=alert(1)>",
            "javascript:alert(document.cookie)",
            "<iframe src='javascript:alert(1)'></iframe>"
        ]

        for payload in payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(Exception):
                    self.create_book(name=payload)

    def test_xss_in_author(self):
        payloads = [
            "<script>document.cookie</script>",
            "<body onload=alert(1)>",
            "<a href='javascript:alert(1)'>Click</a>",
            "<div onclick=alert(1)>test</div>"
        ]

        for payload in payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(Exception):
                    self.create_book(author=payload)

    def test_xss_in_book_type(self):
        with self.assertRaises(Exception):
            self.create_book(
                book_type="<script>alert('XSS')</script>"
            )

    def test_extremely_long_book_name(self):
        name = "A" * 100000

        with self.assertRaises(Exception):
            self.create_book(name=name)

    def test_extremely_long_author(self):
        author = "B" * 100000

        with self.assertRaises(Exception):
            self.create_book(author=author)

    def test_extremely_long_book_type(self):
        book_type = "C" * 100000

        with self.assertRaises(Exception):
            self.create_book(book_type=book_type)

    def test_extreme_publication_year(self):
        extreme_values = [
            10**100,
            -(10**100),
            2**63,
            -(2**63),
        ]

        for value in extreme_values:
            with self.subTest(year=value):
                with self.assertRaises(Exception):
                    self.create_book(year_published=value)

    def test_empty_and_whitespace_extremes(self):
        values = [
            "\n" * 1000,
            "\t" * 1000,
            " " * 10000
        ]

        for value in values:
            with self.subTest(length=len(value)):
                with self.assertRaises(Exception):
                    self.create_book(name=value)


if __name__ == "__main__":
    unittest.main(verbosity=2)
