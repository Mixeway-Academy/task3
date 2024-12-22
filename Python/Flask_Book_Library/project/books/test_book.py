import unittest
from project import db, app
from project.books.models import Book

class TestBookModel(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()
        self.app_context = app.app_context()
        self.app_context.push()
        db.create_all()
        

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    # Testy poprawnych danych
    def test_book_valid_data(self):
        book = Book(name="Jakas Ksiazka", author="Jakis autor", year_published=2024, book_type="Fiction")
        db.session.add(book)
        db.session.commit()
        tested_book = Book.query.filter_by(name="Jakas Ksiazka").first()
        self.assertIsNotNone(tested_book)
        self.assertEqual(tested_book.name, "Jakas Ksiazka")
        self.assertEqual(tested_book.author, "Jakis autor")
        self.assertEqual(tested_book.year_published, 2024)
        self.assertEqual(tested_book.book_type, "Fiction")
        self.assertEqual(tested_book.status, "available")

    def test_duplicate_book_name(self):
        # powinno zwrocic blad
        book1 = Book(name="Name", author="Jakis autor2", year_published=2000, book_type="Fiction")
        book2 = Book(name="Name", author="Jakis autor2", year_published=2000, book_type="Non-Fiction")
        db.session.add(book1)
        db.session.commit()
        db.session.add(book2)
        with self.assertRaises(Exception):
            db.session.commit()

    # Testy niepoprawnych danych
    def test_book_invalid_name(self):
        book = Book(name=None, author="Jakis autor", year_published=2001, book_type="Non-Fiction")
        with self.assertRaises(Exception):
            db.session.add(book)
            db.session.commit()

    def test_book_invalid_author(self):
        book = Book(name="Cos", author=1234, year_published=1920, book_type="Non-Fiction")
        with self.assertRaises(Exception):
            db.session.add(book)
            db.session.commit()

    def test_book_invalid_year(self):
        book = Book(name="Cos2", author="Autor 47", year_published="to nawet nie jest rok", book_type="Non-Fiction")
        with self.assertRaises(Exception):
            db.session.add(book)
            db.session.commit()
    
    def test_book_invalid_book_type(self):
        book = Book(name="Cos3", author="Autor kolejny", year_published=1920, book_type=None)
        with self.assertRaises(Exception):
            db.session.add(book)
            db.session.commit()


    # Testy związane z próbą wstrzyknięcia kodu 
    def test_book_sql_injection(self):
        book = Book(name="sth'; DROP TABLE books; --", author="sql injection test", year_published=2021, book_type="Horror")
        db.session.add(book)
        db.session.commit()
        self.assertIsNotNone(Book.query.filter_by(name="sth'); DROP TABLE books;--").first())
        self.assertEqual(book.name, "sth'; DROP TABLE books; --")
        
    def test_book_xss(self):
        xss_inputs = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert('XSS')>",
            "<body onload=alert('XSS')>",
            "<iframe src='javascript:alert(\"XSS\");'></iframe>",
            "<div style=\"width: expression(alert('XSS'));\">"
        ]

        for i, malicious_input in enumerate(xss_inputs):
            with self.subTest(i=i):
                book = Book(name=malicious_input, author="XSS test", year_published=2021, book_type="Drama")
                with self.assertRaises(Exception):
                    db.session.add(book)
                    db.session.commit()

    # Testy ekstremalne
    def test_book_extreme_year_published(self):
        book = Book(name="Przyszlosc", author="Autor przyszlosci", year_published=99999, book_type="Adventure")
        with self.assertRaises(Exception):
            db.session.add(book)
            db.session.commit()

    def test_book_extreme_year_published_old(self):
        book = Book(name="Bardzo stara ksiazka", author="Jakis autor 9", year_published=-5000, book_type="Adventure")
        with self.assertRaises(Exception):
            db.session.add(book)
            db.session.commit()

    def test_create_book_long_name(self):
        long_name = "A" * 200 
        book = Book(name=long_name, author="Jakis autor 10", year_published=2021, book_type="Adventure")
        with self.assertRaises(Exception):
            db.session.add(book)
            db.session.commit()

    def test_create_book_long_author(self):
        long_author = "B" * 200
        book = Book(name="Ksiazka z dlugim autorem", author=long_author, year_published=2021, book_type="Adventure")
        with self.assertRaises(Exception):
            db.session.add(book)
            db.session.commit()


if __name__ == '__main__':
    unittest.main()
