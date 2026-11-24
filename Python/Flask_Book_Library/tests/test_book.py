import unittest
from unittest.mock import patch

from flask_sqlalchemy import SQLAlchemy

# Import modeli uruchamia create_all. Testy konstruktora nie potrzebują bazy.
with patch.object(SQLAlchemy, "create_all"):
    from project.books.models import Book


class BookTests(unittest.TestCase):
    def create_book(self, **changes):
        data = {
            "name": "Lalka",
            "author": "Bolesław Prus",
            "year_published": 1890,
            "book_type": "5days",
        }
        data.update(changes)
        return Book(**data)

    def test_accepts_valid_data(self):
        book = self.create_book()

        self.assertEqual(book.name, "Lalka")
        self.assertEqual(book.author, "Bolesław Prus")
        self.assertEqual(book.year_published, 1890)
        self.assertEqual(book.book_type, "5days")
        self.assertEqual(book.status, "available")

    def test_accepts_all_supported_loan_periods(self):
        for period in ("2days", "5days", "10days"):
            with self.subTest(period=period):
                self.assertEqual(self.create_book(book_type=period).book_type, period)

    def test_accepts_titles_at_length_boundaries(self):
        for length in (1, 64):
            with self.subTest(length=length):
                title = "A" * length
                self.assertEqual(self.create_book(name=title).name, title)

    def test_rejects_missing_or_blank_title(self):
        for title in (None, "", "   "):
            with self.subTest(title=title):
                with self.assertRaises((TypeError, ValueError)):
                    self.create_book(name=title)

    def test_rejects_title_just_over_length_limit(self):
        with self.assertRaises(ValueError):
            self.create_book(name="A" * 65)

    def test_rejects_non_numeric_publication_year(self):
        with self.assertRaises((TypeError, ValueError)):
            self.create_book(year_published="nieznany")

    def test_rejects_unsupported_loan_period(self):
        with self.assertRaises(ValueError):
            self.create_book(book_type="30days")

    def test_rejects_incomplete_sql_fragment_as_title(self):
        # Niepełne wyrażenie SQL jest wyłącznie przykładem danych wejściowych.
        with self.assertRaises(ValueError):
            self.create_book(name="' OR (")

    def test_rejects_inert_javascript_markup_as_title(self):
        with self.assertRaises(ValueError):
            self.create_book(name='<script type="text/plain">void 0</script>')

    def test_rejects_extremely_long_title(self):
        with self.assertRaises(ValueError):
            self.create_book(name="A" * 10_000_000)
