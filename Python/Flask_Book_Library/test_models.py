import unittest
from project.books.models import Book


class TestBookModel(unittest.TestCase):

    # 1. Testy poprawnych danych
    def test_valid_data(self):
        book = Book(name="Czysty Kod", author="Robert C. Martin", year_published=2008, book_type="IT",
                    status="available")
        self.assertEqual(book.name, "Czysty Kod")
        self.assertEqual(book.author, "Robert C. Martin")
        self.assertEqual(book.year_published, 2008)
        self.assertEqual(book.book_type, "IT")
        self.assertEqual(book.status, "available")

    # 2. Testy niepoprawnych danych
    def test_invalid_data(self):
        # Próba utworzenia książki z pustym tytułem, brakiem autora i błędnym rokiem
        book = Book(name="", author=None, year_published="Dwa Tysiące", book_type=None)

        # Oczekujemy, że klasa wymusi poprawne typy i odrzuci puste wartości
        self.assertIsInstance(book.year_published, int)
        self.assertIsNotNone(book.author)
        self.assertGreater(len(book.name), 0)

    # 3. Testy związane z próbą wstrzyknięcia kodu SQL i JavaScript
    def test_sql_and_js_injection(self):
        sql_payload = "Książka'; DROP TABLE books;--"
        js_payload = "<script>alert('xss')</script>"

        book_sql = Book(name=sql_payload, author="Hacker", year_published=2023, book_type="IT")
        book_js = Book(name="Bezpieczna", author=js_payload, year_published=2023, book_type="IT")

        # Oczekujemy, że klasa odrzuca złośliwe znaki
        self.assertNotEqual(book_sql.name, sql_payload)
        self.assertNotEqual(book_js.author, js_payload)

    # 4. Testy ekstremalne
    def test_extreme_data(self):
        extreme_long_name = "A" * 1000
        extreme_future_year = 999999

        book = Book(name=extreme_long_name, author="Autor", year_published=extreme_future_year, book_type="IT")

        # Oczekujemy, że system rzuci błąd przy przypisywaniu lub że wartości zostaną obcięte do limitów
        self.assertLessEqual(len(book.name), 64)
        self.assertLess(book.year_published, 2100)


if __name__ == '__main__':
    unittest.main()