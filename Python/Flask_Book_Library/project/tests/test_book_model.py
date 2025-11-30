import unittest
from project.books.models import Book
import datetime

class BookModelTestCase(unittest.TestCase):
    def test_create_valid_book(self):
        """Sprawdza czy można utworzyć obiekt książki z prawidłowymi danymi"""
        # Given
        name = "Wiedźmin: Ostatnie Życzenie"
        author = "Andrzej Sapkowski"
        year = 1993
        
        # When
        book = Book(
            name=name,
            author=author,
            year_published=year,
            book_type="Fantasy",
            status="available"
        )
        
        # Then
        self.assertEqual(book.name, name)
        self.assertEqual(book.author, author)
        self.assertEqual(book.year_published, year)

    def test_reject_book_author(self):
        """Test powinien rzucić wyjątek przy próbie utworzenia książki z niepoprawnymi znakami w nazwie autora"""
        # Given
        author_name = "Autor123!@#>?/.,"
        
        # When & Then
        with self.assertRaises(ValueError) as cm:
            Book(
                name="Książka z przyszłości",
                author=author_name,
                year_published=2000,
                book_type="Sci-Fi"
            )
        self.assertIn("Niepoprawne znaki w nazwie autora.", str(cm.exception))
    
    def test_reject_future_year(self):
        """Test powinien rzucić wyjątek przy próbie utworzenia książki z datą z przyszłości"""
        # Given
        future_year = datetime.datetime.now().year + 1
        
        # When & Then
        with self.assertRaises(ValueError) as cm:
            Book(
                name="Książka z przyszłości",
                author="Autor",
                year_published=future_year,
                book_type="Sci-Fi"
            )
        self.assertIn("Rok publikacji nie może być z przyszłości.", str(cm.exception))

    def test_sql_injection_sanitization(self):
        """Sprawdza czy konstruktor czyści nazwę z potencjalnego kodu SQL i niepoprawnych znaków"""
        # Given
        sql_payload = "Wiedźmin'; DROP TABLE books; --"
        
        # When
        book = Book(name=sql_payload, author="Hacker", year_published=2020, book_type="Hack")
        
        # Then
        self.assertNotIn(";", book.name, "Średnik powinien zostać usunięty.")
        self.assertNotIn("--", book.name, "Komentarz SQL powinien zostać usunięty.")
        self.assertEqual(book.name, "Wiedźmin' DROP TABLE books ")

    def test_xss_injection_in_author(self):
        """Sprawdza czy konstruktor czyści autora z kodu JavaScript"""
        # Given
        xss_payload = "<script>alert('XSS')</script>John Doe"
        
        # When
        book = Book(name="XSS Book", author=xss_payload, year_published=2020, book_type="Tech")
        
        # Then
        self.assertNotIn("<script>", book.author, "Tag <script> powinien zostać usunięty.")
        self.assertNotIn("alert('XSS')", book.author, "Kod JS powinien zostać usunięty lub zneutralizowany.")
        self.assertEqual(book.author, "alert('XSS')John Doe")

    def test_extreme_string_length(self):
        """Sprawdza czy konstruktor odrzuca zbyt długą nazwę"""
        # Given
        long_name = "A" * 10000
        
        # When
        with self.assertRaises(ValueError) as cm:
            Book(name=long_name, author="Author", year_published=2020, book_type="Type")
            
        # Then
        self.assertIn("Nazwa książki jest za długa!", str(cm.exception))