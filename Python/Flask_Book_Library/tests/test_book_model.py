import unittest
from datetime import date

from project.books.models import Book


class BookModelTests(unittest.TestCase):
    def make_book(self, **changes):
        values = {
            'name': 'Clean Code',
            'author': 'Robert C. Martin',
            'year_published': 2008,
            'book_type': '5days',
            'status': 'available',
        }
        values.update(changes)
        return Book(**values)

    def assert_rejected(self, **changes):
        with self.assertRaises((TypeError, ValueError)):
            self.make_book(**changes)

    # Valid data
    def test_valid_book(self):
        book = self.make_book()
        self.assertEqual(book.name, 'Clean Code')
        self.assertEqual(book.author, 'Robert C. Martin')
        self.assertEqual(book.year_published, 2008)
        self.assertEqual(book.book_type, '5days')

    def test_default_status(self):
        book = Book('Clean Code', 'Robert C. Martin', 2008, '5days')
        self.assertEqual(book.status, 'available')

    def test_valid_boundary_values(self):
        book = self.make_book(name='N' * 64, author='A' * 64,
                              year_published=date.today().year,
                              book_type='10days')
        self.assertEqual(len(book.name), 64)
        self.assertEqual(len(book.author), 64)
        self.assertEqual(book.book_type, '10days')

    def test_unicode_text(self):
        book = self.make_book(name='Żółw i spółka', author='Łukasz Żak')
        self.assertEqual(book.name, 'Żółw i spółka')
        self.assertEqual(book.author, 'Łukasz Żak')

    # Invalid data
    def test_empty_name(self):
        self.assert_rejected(name='')

    def test_missing_name(self):
        self.assert_rejected(name=None)

    def test_whitespace_name(self):
        self.assert_rejected(name='   ')

    def test_non_numeric_year(self):
        self.assert_rejected(year_published='yesterday')

    def test_negative_year(self):
        self.assert_rejected(year_published=-1)

    def test_future_year(self):
        self.assert_rejected(year_published=date.today().year + 1)

    def test_invalid_book_type(self):
        self.assert_rejected(book_type='forever')

    def test_invalid_status(self):
        self.assert_rejected(status='unknown')

    # SQL and JavaScript payloads
    def test_sql_payload_in_name(self):
        self.assert_rejected(name="' OR 1=1 --")

    def test_sql_payload_in_author(self):
        self.assert_rejected(author="Robert'); DROP TABLE books; --")

    def test_script_payload_in_name(self):
        self.assert_rejected(name='<script>alert(1)</script>')

    def test_event_payload_in_author(self):
        self.assert_rejected(author='<img src=x onerror=alert(1)>')

    # Extreme values
    def test_name_above_column_limit(self):
        self.assert_rejected(name='N' * 65)

    def test_very_long_name(self):
        self.assert_rejected(name='N' * 10000)

    def test_author_above_column_limit(self):
        self.assert_rejected(author='A' * 65)

    def test_huge_year(self):
        self.assert_rejected(year_published=10 ** 100)


if __name__ == '__main__':
    unittest.main()
