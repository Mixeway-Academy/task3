import sys
import unittest
from project.books.models import Book


class TestBookModel(unittest.TestCase):

    def test_correct_input(self):
        valid_books = [
            {"name": "Wiedzmin", "author": "Andrzej Sapkowski", "year_published": 1993, "book_type": "5days"},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "10days", "status": "available"},
            {"name": "Lalka", "author": "Boleslaw Prus", "year_published": 1890, "book_type": "2days", "status": "loaned"},
            {"name": "X" * 64, "author": "A" * 64, "year_published": 2023, "book_type": "2days"},
        ]

        for data in valid_books:
            with self.subTest(data=data):
                try:
                    book = Book(**data)
                    self.assertEqual(book.name, data["name"])
                    self.assertEqual(book.author, data["author"])
                    self.assertEqual(book.year_published, data["year_published"])
                    self.assertEqual(book.book_type, data["book_type"])
                except Exception as exc:
                    self.fail(f"Unexpected exception raised: {exc}")

    def test_incorrect_input_name(self):
        inputs = [
            None,
            "null",
            "nil",
            "0",
            "",
            " ",
            "\t",
            "\n",
            "book\ntitle",
            "   Pan Tadeusz",
            "%20PanTadeusz",
            "Pan%20Tadeusz",
            "Pan..Tadeusz",
            "--",
            "=0@$*^%;<!->.:\\()&#\"",
            "@@£$∞§|[]≈±´•Ωé®†µüıœπ˙~ß∂¸√ç‹›‘’‚…",
        ]

        for value in inputs:
            with self.subTest(name=value):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(
                        name=value,
                        author="Adam Mickiewicz",
                        year_published=1834,
                        book_type="5days"
                    )

    def test_incorrect_input_author(self):
        inputs = [
            None,
            "null",
            "nil",
            "0",
            "",
            " ",
            "\t",
            "\n",
            "jan.kowalski\n",
            "   Jan Kowalski",
            "%20JanKowalski",
            "Jan..Kowalski",
            "--",
            "J a n   K o w a l s k i",
            "=0@$*^%;<!->.:\\()&#\"",
            "@@£$∞§|[]≈±´•Ωé®†µüıœπ˙~ß∂¸√ç‹›‘’‚…",
        ]

        for value in inputs:
            with self.subTest(author=value):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(
                        name="Pan Tadeusz",
                        author=value,
                        year_published=1834,
                        book_type="5days"
                    )

    def test_incorrect_input_year_and_type(self):
        invalid_cases = [
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": None, "book_type": "5days"},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": "nie_liczba", "book_type": "5days"},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": -100, "book_type": "5days"},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 0, "book_type": "5days"},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": None},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": ""},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "invalid_type"},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "5days", "status": ""},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "5days", "status": "unknown_status"},
        ]

        for case in invalid_cases:
            with self.subTest(case=case):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(**case)

    def test_incorrect_input_xss(self):
        inputs = [
            "\"-prompt(8)-\"",
            "'-prompt(8)-'",
            "<img/src/onerror=prompt(8)>",
            "<script\\x20type=\"text/javascript\">javascript:alert(1);</script>",
            "'`\"><\\x3Cscript>javascript:alert(1)</script>",
            "<script src=1 href=1 onerror=\"javascript:alert(1)\"></script>",
        ]

        for value in inputs:
            with self.subTest(field="name", payload=value):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name=value, author="Adam Mickiewicz", year_published=1834, book_type="5days")

            with self.subTest(field="author", payload=value):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name="Pan Tadeusz", author=value, year_published=1834, book_type="5days")

            with self.subTest(field="book_type", payload=value):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name="Pan Tadeusz", author="Adam Mickiewicz", year_published=1834, book_type=value)

            with self.subTest(field="status", payload=value):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name="Pan Tadeusz", author="Adam Mickiewicz", year_published=1834, book_type="5days", status=value)

    def test_incorrect_input_sqli(self):
        inputs = [
            "-- or # ",
            "\" OR 1 = 1 -- -",
            "'''''''''''''UNION SELECT '2",
            "1' ORDER BY 1--+",
            "' UNION SELECT sum(columnname ) from tablename --",
            ",(select * from (select(sleep(10)))a)",
        ]

        for value in inputs:
            with self.subTest(field="name", payload=value):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name=value, author="Adam Mickiewicz", year_published=1834, book_type="5days")

            with self.subTest(field="author", payload=value):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name="Pan Tadeusz", author=value, year_published=1834, book_type="5days")

            with self.subTest(field="book_type", payload=value):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name="Pan Tadeusz", author="Adam Mickiewicz", year_published=1834, book_type=value)

            with self.subTest(field="status", payload=value):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name="Pan Tadeusz", author="Adam Mickiewicz", year_published=1834, book_type="5days", status=value)

    def test_incorrect_input_boundary(self):
        boundary_cases = [
            {"name": "x" * 65, "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "5days"},
            {"name": "Pan Tadeusz", "author": "x" * 65, "year_published": 1834, "book_type": "5days"},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "x" * 21},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "5days", "status": "x" * 21},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "1days"},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "3days"},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "11days"},
            {"name": ".Pan Tadeusz", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "5days"},
            {"name": "Pan Tadeusz.", "author": "Adam Mickiewicz", "year_published": 1834, "book_type": "5days"},
            {"name": "Pan Tadeusz", "author": ".Adam Mickiewicz", "year_published": 1834, "book_type": "5days"},
            {"name": "Pan Tadeusz", "author": "Adam Mickiewicz.", "year_published": 1834, "book_type": "5days"},
        ]

        for case in boundary_cases:
            with self.subTest(case=case):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(**case)

    def test_extreme_input(self):
        inputs = [
            "X" * 10000,
            "X" * 100000,
            "X" * 1000000,
            "X" * 2000000,
            "X" * 4000000,
        ]

        for value in inputs:
            with self.subTest(field="name", length=len(value)):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name=value, author="Adam Mickiewicz", year_published=1834, book_type="5days")

            with self.subTest(field="author", length=len(value)):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name="Pan Tadeusz", author=value, year_published=1834, book_type="5days")

    def test_extreme_year_input(self):
        extreme_years = [
            -sys.maxsize,
            -1000000,
            1000000,
            sys.maxsize,
            10**100,
        ]

        for year in extreme_years:
            with self.subTest(year=year):
                with self.assertRaises((ValueError, TypeError, RuntimeError)):
                    Book(name="Pan Tadeusz", author="Adam Mickiewicz", year_published=year, book_type="5days")


if __name__ == "__main__":
    unittest.main()
