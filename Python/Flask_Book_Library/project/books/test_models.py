import unittest
from project import app, db
from project.books.models import Book


class TestBookModel(unittest.TestCase):

    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Testy poprawnych danych
    def test_valid_book_creation(self):
        book = Book(name="Wiedźmin", author="Andrzej Sapkowski", year_published=1990, book_type="2days")
        db.session.add(book)
        db.session.commit()
        self.assertEqual(book.name, "Wiedźmin")
        self.assertEqual(book.author, "Andrzej Sapkowski")
        self.assertEqual(book.year_published, 1990)
        self.assertEqual(book.book_type, "2days")
        self.assertEqual(book.status, "available")

    def test_valid_book_repr(self):
        book = Book(name="Solaris", author="Stanisław Lem", year_published=1961, book_type="2days")
        self.assertIn("Solaris", repr(book))
        self.assertIn("Stanisław Lem", repr(book))

    # Testy niepoprawnych danych
    def test_invalid_empty_name(self):
        with self.assertRaises((ValueError, TypeError)):
            Book(name="", author="Autor", year_published=2020, book_type="2days")

    def test_invalid_none_values(self):
        with self.assertRaises((ValueError, TypeError)):
            Book(name=None, author=None, year_published=None, book_type=None)

    def test_invalid_year_type_string(self):
        with self.assertRaises((ValueError, TypeError)):
            Book(name="Książka", author="Autor", year_published="dwatysiące", book_type="2days")

    def test_invalid_negative_year(self):
        with self.assertRaises(ValueError):
            Book(name="Książka", author="Autor", year_published=-500, book_type="2days")

    def test_invalid_book_type(self):
        with self.assertRaises(ValueError):
            Book(name="Książka", author="Autor", year_published=2020, book_type="invalid_type")

    # SQL Injection i XSS
    def test_sql_injection_in_name(self):
        with self.assertRaises(ValueError):
            Book(name="'; DROP TABLE books; --", author="Autor", year_published=2020, book_type="2days")

    def test_xss_script_in_name(self):
        with self.assertRaises(ValueError):
            Book(name="<script>alert('XSS')</script>", author="Autor", year_published=2020, book_type="2days")

    def test_xss_img_in_author(self):
        with self.assertRaises(ValueError):
            Book(name="Książka", author="<img src=x onerror=alert(1)>", year_published=2020, book_type="2days")

    # Testy ekstremalne
    def test_extreme_long_name(self):
        with self.assertRaises(ValueError):
            Book(name="A" * 10000, author="Autor", year_published=2020, book_type="2days")

    def test_extreme_huge_year(self):
        with self.assertRaises((ValueError, OverflowError)):
            Book(name="Książka", author="Autor", year_published=10**20, book_type="2days")


if __name__ == "__main__":
    unittest.main()
