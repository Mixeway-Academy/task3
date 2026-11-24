import unittest
from datetime import date
from unittest.mock import patch

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
from sqlalchemy.exc import IntegrityError


original_init_app = SQLAlchemy.init_app


def use_memory_database(self, flask_app):
    flask_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    original_init_app(self, flask_app)


with patch.object(SQLAlchemy, 'init_app', use_memory_database):
    from project import app, db
    from project.books.models import Book


class BookTests(unittest.TestCase):
    def setUp(self):
        self.context = app.app_context()
        self.context.push()
        db.drop_all()
        db.create_all()

    def tearDown(self):
        db.session.rollback()
        db.session.remove()
        db.drop_all()
        self.context.pop()

    def make_book(self, **changes):
        fields = dict(name='Solaris', author='Stanisław Lem',
                      year_published=1961, book_type='5days')
        fields.update(changes)
        return Book(**fields)

    def save(self, book):
        db.session.add(book)
        db.session.commit()
        db.session.expire_all()

    def test_valid_book_and_default_status(self):
        book = self.make_book()
        self.save(book)
        stored = db.session.get(Book, book.id)
        self.assertEqual(stored.name, 'Solaris')
        self.assertEqual(stored.author, 'Stanisław Lem')
        self.assertEqual(stored.year_published, 1961)
        self.assertEqual(stored.book_type, '5days')
        self.assertEqual(stored.status, 'available')
        self.assertIn('Solaris', repr(stored))

    def test_valid_types_and_custom_status(self):
        for book_type in ('2days', '5days', '10days'):
            with self.subTest(book_type=book_type):
                book = self.make_book(name=book_type, book_type=book_type,
                                      status='unavailable')
                self.save(book)
                self.assertEqual(db.session.get(Book, book.id).status,
                                 'unavailable')

    def test_unicode_title_and_current_year(self):
        book = self.make_book(name='Żółw i światło: część II',
                              author='Łucja Nowak',
                              year_published=date.today().year)
        self.save(book)
        stored = db.session.get(Book, book.id)
        self.assertEqual(stored.name, 'Żółw i światło: część II')
        self.assertEqual(stored.author, 'Łucja Nowak')
        self.assertEqual(stored.year_published, date.today().year)

    def test_missing_name_is_rejected(self):
        for name in ('', None, '   '):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.make_book(name=name)

    def test_invalid_year_is_rejected(self):
        for year in (-1, 0, 'nieznany', None):
            with self.subTest(year=year), self.assertRaises((TypeError, ValueError)):
                self.make_book(year_published=year)

    def test_unknown_book_type_is_rejected(self):
        for book_type in ('30days', '', None):
            with self.subTest(book_type=book_type), self.assertRaises(ValueError):
                self.make_book(book_type=book_type)

    def test_wrong_field_types_are_rejected(self):
        for field, value in (('name', 123), ('name', ['Solaris']),
                             ('author', 42), ('author', ['Lem'])):
            with self.subTest(field=field, value=value), self.assertRaises((TypeError, ValueError)):
                self.make_book(**{field: value})

    def test_control_characters_in_name_are_rejected(self):
        for name in ('Tytuł\x00dopisek', 'Tytuł\nDruga linia'):
            with self.subTest(name=repr(name)), self.assertRaises(ValueError):
                self.make_book(name=name)

    def test_duplicate_name_is_rejected_by_database(self):
        self.save(self.make_book())
        with self.assertRaises(IntegrityError):
            self.save(self.make_book(author='Inny autor'))

    def test_renaming_to_an_existing_name_is_rejected(self):
        self.save(self.make_book())
        second = self.make_book(name='Dzienniki gwiazdowe')
        self.save(second)
        stored = db.session.get(Book, second.id)
        stored.name = 'Solaris'
        with self.assertRaises(IntegrityError):
            db.session.commit()

    def test_sql_payloads_do_not_execute(self):
        payloads = ("'; DROP TABLE books; --", "' OR '1'='1",
                    "'; DELETE FROM books; --")
        for number, payload in enumerate(payloads):
            with self.subTest(payload=payload):
                book = self.make_book(name=payload, author=payload)
                self.save(book)
                self.assertEqual(db.session.get(Book, book.id).author, payload)
                count = db.session.execute(text('SELECT count(*) FROM books')).scalar_one()
                self.assertEqual(count, number + 1)

    def test_sql_condition_does_not_match_other_books(self):
        self.save(self.make_book())
        self.save(self.make_book(name='Lalka', author='Bolesław Prus'))
        self.assertIsNone(Book.query.filter_by(name="' OR '1'='1").first())
        self.assertEqual(Book.query.count(), 2)

    def test_script_in_name_is_not_rendered_as_html(self):
        payload = '<script>alert(1)</script>'
        self.save(self.make_book(name=payload))
        response = app.test_client().get('/books/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(payload.encode() in response.data)
        self.assertIn(b'&lt;script&gt;', response.data)

    def test_script_in_author_is_not_rendered_as_html(self):
        payload = '<img src=x onerror=alert(1)>'
        self.save(self.make_book(author=payload))
        response = app.test_client().get('/books/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(payload.encode() in response.data)
        self.assertIn(b'&lt;img', response.data)

    def test_svg_in_name_is_not_rendered_as_html(self):
        payload = '<svg onload=alert(1)>'
        self.save(self.make_book(name=payload))
        response = app.test_client().get('/books/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(payload.encode() in response.data)
        self.assertIn(b'&lt;svg', response.data)

    def test_html_attribute_in_author_is_not_rendered_as_html(self):
        payload = '<a href="javascript:alert(1)">Autor</a>'
        self.save(self.make_book(author=payload))
        response = app.test_client().get('/books/')
        self.assertEqual(response.status_code, 200)
        self.assertFalse(payload.encode() in response.data)
        self.assertIn(b'&lt;a', response.data)

    def test_overlong_name_is_rejected(self):
        for length in (65, 10000):
            with self.subTest(length=length), self.assertRaises(ValueError):
                self.make_book(name='A' * length)

    def test_overlong_author_is_rejected(self):
        for length in (65, 10000):
            with self.subTest(length=length), self.assertRaises(ValueError):
                self.make_book(author='A' * length)

    def test_maximum_field_lengths_are_accepted(self):
        book = self.make_book(name='A' * 64, author='B' * 64)
        self.save(book)
        stored = db.session.get(Book, book.id)
        self.assertEqual(len(stored.name), 64)
        self.assertEqual(len(stored.author), 64)

    def test_integer_overflow_is_rejected_by_database(self):
        for year in (2 ** 80, -(2 ** 80)):
            with self.subTest(year=year), self.assertRaises(OverflowError):
                self.save(self.make_book(year_published=year))
            db.session.rollback()


if __name__ == '__main__':
    unittest.main()
