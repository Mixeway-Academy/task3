import unittest
from project import app, db
from project.books.models import Book


class BookTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
        self.app = app.test_client()
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()

    def test_create_book(self):
        book = Book(name='Book 1', author='Author 1', year_published=2022, book_type='Fiction')
        with app.app_context():
            db.session.add(book)
            db.session.commit()
            assert book.id is not None
            assert book.name == 'Book 1'
            assert book.author == 'Author 1'
            assert book.year_published == 2022
            assert book.book_type == 'Fiction'
            assert book.status == 'available'

    def test_repr(self):
        book = Book(name='Book 1', author='Author 1', year_published=2022, book_type='Fiction')
        with app.app_context():
            db.session.add(book)
            db.session.commit()
            expected_repr = "Book(ID: {}, Name: {}, Author: {}, Year Published: {}, Type: {}, Status: {})".format(
                book.id, book.name, book.author, book.year_published, book.book_type, book.status
            )
            assert repr(book) == expected_repr

    def test_xss_vulnerability(self):
        name = '<script>alert("XSS Attack!");</script>'
        author = 'Author 1'
        year_published = 2022
        book_type = 'Fiction'

        book = Book(name=name, author=author, year_published=year_published, book_type=book_type)
        with app.app_context():
            db.session.add(book)
            db.session.commit()
            self.assertRaises(AssertionError, self.assertEqual, book.name, '<script>alert("XSS Attack!");</script>')



if __name__ == '__main__':
    unittest.main()