import unittest
from project.books.models import Book


class TestBookModel(unittest.TestCase):

    # poprawne dane
    def test_valid_book_creation(self):
        book = Book(
            name="Wiedźmin: Ostatnie życzenie",
            author="Andrzej Sapkowski",
            year_published=1993,
            book_type="5days",
            status="available"
        )
        self.assertEqual(book.name, "Wiedźmin: Ostatnie życzenie")
        self.assertEqual(book.author, "Andrzej Sapkowski")
        self.assertEqual(book.year_published, 1993)
        self.assertEqual(book.book_type, "5days")
        self.assertEqual(book.status, "available")

    def test_valid_book_default_status(self):
        book = Book("Lalka", "Bolesław Prus", 1890, "10days")
        self.assertEqual(book.status, "available")

    def test_valid_book_repr(self):
        book = Book("Solaris", "Stanisław Lem", 1961, "2days")
        expected = (
            "Book(ID: None, Name: Solaris, Author: Stanisław Lem, "
            "Year Published: 1961, Type: 2days, Status: available)"
        )
        self.assertEqual(repr(book), expected)

    # niepoprawne dane
    def test_invalid_empty_name_and_author(self):
        with self.assertRaises((ValueError, TypeError)):
            Book(name="", author="", year_published=2020, book_type="5days")

    def test_invalid_none_values(self):
        with self.assertRaises((ValueError, TypeError)):
            Book(name=None, author=None, year_published=None, book_type=None)

    def test_invalid_year_type_string(self):
        with self.assertRaises((ValueError, TypeError)):
            Book(name="Pan Tadeusz", author="Adam Mickiewicz", year_published="1800", book_type="5days")

    def test_invalid_negative_year(self):
        with self.assertRaises(ValueError):
            Book(name="Stara Księga", author="Nieznany", year_published=-500, book_type="5days")

    def test_invalid_future_year(self):
        with self.assertRaises(ValueError):
            Book(name="Książka z przyszłości", author="Jan Kowalski", year_published=3050, book_type="5days")

    def test_invalid_status_value(self):
        with self.assertRaises(ValueError):
            Book(name="Dziady", author="Adam Mickiewicz", year_published=1823, book_type="5days", status="_niepoprawny_status")

    def test_invalid_book_type_not_string(self):
        with self.assertRaises((ValueError, TypeError)):
            Book(name="Quo Vadis", author="Henryk Sienkiewicz", year_published=1896, book_type=12345)

    # SQL i XSS
    def test_sql_injection_in_name(self):
        with self.assertRaises(ValueError):
            Book(name="'; DROP TABLE books; --", author="Jan Kowalski", year_published=2021, book_type="5days")

    def test_sql_injection_in_author(self):
        with self.assertRaises(ValueError):
            Book(name="Normalny Tytuł", author="Admin' OR '1'='1", year_published=2021, book_type="5days")

    def test_xss_script_injection_in_name(self):
        with self.assertRaises(ValueError):
            Book(name="<script>alert('XSS');</script>", author="Jan Kowalski", year_published=2021, book_type="5days")

    def test_xss_img_injection_in_author(self):
        with self.assertRaises(ValueError):
            Book(name="Normalny Tytuł", author="<img src=x onerror=alert('XSS')>", year_published=2021, book_type="5days")

    def test_xss_injection_in_book_type(self):
        with self.assertRaises(ValueError):
            Book(name="Normalny Tytuł", author="Jan Kowalski", year_published=2021, book_type="<svg/onload=alert(1)>")

    # testy ekstremalne i brzegowe
    def test_extreme_long_name(self):
        with self.assertRaises(ValueError):
            Book(name="A" * 10000, author="Jan Kowalski", year_published=2020, book_type="5days")

    def test_extreme_long_author(self):
        with self.assertRaises(ValueError):
            Book(name="Krótki tytuł", author="B" * 10000, year_published=2020, book_type="5days")

    def test_extreme_huge_year(self):
        with self.assertRaises((ValueError, OverflowError)):
            Book(name="Test Roku", author="Jan Kowalski", year_published=10**20, book_type="5days")

    def test_extreme_null_bytes_and_control_chars(self):
        with self.assertRaises(ValueError):
            Book(name="Książka\x00\r\n\t", author="Autor\x00" * 20, year_published=2020, book_type="5days")

    def test_boundary_name_length(self):
        book = Book(name="A" * 64, author="Jan Kowalski", year_published=2020, book_type="5days")
        self.assertEqual(len(book.name), 64)
        with self.assertRaises(ValueError):
            Book(name="A" * 65, author="Jan Kowalski", year_published=2020, book_type="5days")

    def test_boundary_year_zero(self):
        with self.assertRaises(ValueError):
            Book(name="Książka", author="Jan Kowalski", year_published=0, book_type="5days")


if __name__ == "__main__":
    unittest.main()