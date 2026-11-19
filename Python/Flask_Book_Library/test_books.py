import pytest
from project import app, db
from project.books.models import Book
from sqlalchemy.exc import IntegrityError, DataError


@pytest.fixture
def client():
    """Konfiguracja środowiska testowego"""
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'

    with app.app_context():
        db.create_all()

        yield app.test_client()

        db.session.remove()
        db.drop_all()


# ==============================================================================
# 1. TESTY POPRAWNYCH DANYCH (VALID DATA TESTS)
# ==============================================================================

def test_create_book_success(client):
    """Poprawne utworzenie książki przez endpoint API /books/create."""
    data = {
        'name': 'Harry Potter',
        'author': 'J.K. Rowling',
        'year_published': 1997,
        'book_type': 'Fantasy'
    }

    response = client.post('/books/create', json=data)

    assert response.status_code == 302

    book = Book.query.filter_by(name='Harry Potter').first()
    assert book is not None
    assert book.name == 'Harry Potter'
    assert book.author == 'J.K. Rowling'
    assert book.year_published == 1997
    assert book.book_type == 'Fantasy'
    assert book.status == 'available'


def test_book_model_init_direct(client):
    """Bezpośrednie utworzenie obiektu klasy Book i weryfikacja jego atrybutów."""
    book = Book(
        name="Władca Pierścieni",
        author="J.R.R. Tolkien",
        year_published=1954,
        book_type="10days",
        status="available"
    )

    assert book.name == "Władca Pierścieni"
    assert book.author == "J.R.R. Tolkien"
    assert book.year_published == 1954
    assert book.book_type == "10days"
    assert book.status == "available"


def test_book_model_default_status(client):
    """Sprawdzenie domyślnej wartości atrybutu status ('available')."""
    book = Book(
        name="Hobbit",
        author="J.R.R. Tolkien",
        year_published=1937,
        book_type="5days"
    )
    assert book.status == "available"


def test_book_model_repr(client):
    """Weryfikacja tekstowej reprezentacji obiektu Book (__repr__)."""
    book = Book(
        name="Solaris",
        author="Stanisław Lem",
        year_published=1961,
        book_type="2days",
        status="available"
    )
    expected_repr = (
        f"Book(ID: {book.id}, Name: {book.name}, Author: {book.author}, "
        f"Year Published: {book.year_published}, Type: {book.book_type}, Status: {book.status})"
    )
    assert repr(book) == expected_repr


# ==============================================================================
# 2. TESTY NIEPOPRAWNYCH DANYCH (INVALID DATA TESTS)
# ==============================================================================

def test_create_book_missing_field_book_type(client):
    """Brak wymaganego pola 'book_type' powinien skutkować kodem 400 Bad Request."""
    data = {
        'name': 'Harry Potter',
        'author': 'J.K. Rowling',
        'year_published': 1997
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400
    assert 'error' in response.json


def test_create_book_missing_field_name(client):
    """Brak wymaganego pola 'name' powinien skutkować błędem 400 i brakiem zapisu w bazie."""
    data = {
        'author': 'J.K. Rowling',
        'year_published': 1997,
        'book_type': 'Fantasy'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400
    assert 'error' in response.json


def test_create_book_missing_field_year(client):
    """Brak wymaganego pola 'year_published' powinien zwrócić błąd 400."""
    data = {
        'name': 'Test Book Without Year',
        'author': 'Test Author',
        'book_type': '5days'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400
    assert 'error' in response.json


def test_create_book_empty_strings(client):
    """Próba utworzenia książki z pustym tytułem lub pustym autorem."""
    data = {
        'name': '',
        'author': '',
        'year_published': 2020,
        'book_type': '2days'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400
    assert Book.query.filter_by(name='').first() is None


def test_create_book_invalid_year_type_string(client):
    """Niepoprawny typ danych dla roku wydania (tekst zamiast liczby całkowitej)."""
    data = {
        'name': 'Książka z Błędnym Rokiem',
        'author': 'Anonim',
        'year_published': 'dwa tysiące dwudziesty',
        'book_type': '2days'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400
    assert Book.query.filter_by(name='Książka z Błędnym Rokiem').first() is None


def test_create_book_invalid_book_type_choice(client):
    """Typ książki spoza dozwolonej puli wyborów ('2days', '5days', '10days')."""
    data = {
        'name': 'Nieprawidłowy Typ Książki',
        'author': 'Autor',
        'year_published': 2022,
        'book_type': 'niedozwolony_typ_100_dni'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400
    assert Book.query.filter_by(name='Nieprawidłowy Typ Książki').first() is None


def test_create_book_duplicate_name(client):
    """Próba utworzenia książki o istniejącym tytule (unikalność kolumny 'name')."""
    data1 = {
        'name': 'Unikalny Tytuł',
        'author': 'Autor Pierwszy',
        'year_published': 2010,
        'book_type': '2days'
    }
    resp1 = client.post('/books/create', json=data1)
    assert resp1.status_code == 302

    # Próba dodania drugiej książki o tej samej nazwie
    data2 = {
        'name': 'Unikalny Tytuł',
        'author': 'Autor Drugi',
        'year_published': 2020,
        'book_type': '5days'
    }
    resp2 = client.post('/books/create', json=data2)
    # Powinno zwrócić błąd (kod 400 lub 409 Conflict lub 500) i nie dopuścić do duplikatu
    assert resp2.status_code in [400, 409, 500]
    assert Book.query.filter_by(name='Unikalny Tytuł').count() == 1


def test_create_book_invalid_status(client):
    """Próba utworzenia książki z nieobsługiwanym statusem (np. 'destroyed')."""
    data = {
        'name': 'Zniszczona Książka',
        'author': 'Autor',
        'year_published': 2015,
        'book_type': '2days',
        'status': 'destroyed'
    }
    response = client.post('/books/create', json=data)
    # Jeśli walidacja statusu jest zaimplementowana, powinna odrzucić
    assert response.status_code == 400


# ==============================================================================
# 3. TESTY WSTRZYKIWANIA KODU SQL I JAVASCRIPT (SQL & JS INJECTION TESTS)
# ==============================================================================

def test_create_book_xss_in_name(client):
    """Próba wstrzyknięcia skryptu JavaScript (<script>) w tytule książki."""
    data = {
        'name': '<script>alert("XSS")</script>',
        'author': 'Attacker',
        'year_published': 2024,
        'book_type': 'Fantasy'
    }

    response = client.post('/books/create', json=data)

    assert response.status_code == 400
    assert response.json.get('error') == 'Invalid input detected in field: name'
    book = Book.query.filter_by(name='<script>alert("XSS")</script>').first()
    assert book is None


def test_create_book_xss_svg_payload(client):
    """Próba ataku XSS z użyciem wektora SVG w polu book_type."""
    data = {
        'name': 'Książka SVG XSS',
        'author': 'Tester Bezpieczeństwa',
        'year_published': 2022,
        'book_type': '<svg onload=alert(1)>'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400
    assert Book.query.filter_by(name='Książka SVG XSS').first() is None


def test_create_book_sql_injection_tautology(client):
    """Próba wstrzyknięcia SQL (' OR '1'='1) w tytule."""
    sqli_payload = "Book' OR '1'='1"
    data = {
        'name': sqli_payload,
        'author': 'SQL Injector',
        'year_published': 2020,
        'book_type': '2days'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400 or response.status_code == 302
    # Sprawdzenie czy baza nadal funkcjonuje poprawnie
    assert Book.query.count() >= 0


def test_create_book_sql_injection_drop_table(client):
    """Próba zniszczenia tabeli za pomocą wstrzyknięcia polecenia DROP TABLE."""
    sqli_payload = "Clean Code'; DROP TABLE books; --"
    data = {
        'name': sqli_payload,
        'author': 'Destructive Attacker',
        'year_published': 2008,
        'book_type': '10days'
    }
    response = client.post('/books/create', json=data)
    # Sprawdzenie czy tabela books nadal istnieje i nie została usunięta
    books_still_exist = db.session.query(Book).count()
    assert books_still_exist >= 0


def test_create_book_sql_injection_in_year(client):
    """Próba wstrzyknięcia kodu SQL w numerycznym polu year_published."""
    data = {
        'name': 'Książka z SQL w Roku',
        'author': 'Tester SQL',
        'year_published': '2020; SELECT * FROM customers;',
        'book_type': '2days'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400


# ==============================================================================
# 4. TESTY EKSTREMALNE (EXTREME / BOUNDARY TESTS)
# ==============================================================================

def test_extreme_long_name_exceeding_column_limit(client):
    """Próba utworzenia książki z nazwą przekraczającą limit kolumny db.String(64)."""
    # Kolumna name ma limit String(64). Przekazujemy ciąg 1000 znaków.
    extreme_name = "A" * 1000
    data = {
        'name': extreme_name,
        'author': 'Autor',
        'year_published': 2020,
        'book_type': '2days'
    }
    response = client.post('/books/create', json=data)
    # Aplikacja powinna odrzucić zbyt długą nazwę kodem 400
    assert response.status_code == 400
    assert Book.query.filter_by(name=extreme_name).first() is None


def test_extreme_long_author(client):
    """Próba utworzenia książki z polem autor o długości 1000 znaków (limit String(64))."""
    extreme_author = "B" * 1000
    data = {
        'name': 'Książka z Długim Autorem',
        'author': extreme_author,
        'year_published': 2021,
        'book_type': '5days'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400
    assert Book.query.filter_by(author=extreme_author).first() is None


def test_extreme_long_book_type(client):
    """Próba przekazania book_type o długości 500 znaków (limit String(20))."""
    extreme_type = "T" * 500
    data = {
        'name': 'Książka z Długim Typem',
        'author': 'Autor',
        'year_published': 2022,
        'book_type': extreme_type
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400


def test_extreme_large_year_integer(client):
    """Przekazanie ekstremalnej liczby całkowitej jako rok wydania (przekroczenie int32 / nierealna wartość)."""
    extreme_year = 10**18  # 1 trylion
    data = {
        'name': 'Książka z Ekstremalnym Rokiem',
        'author': 'Podróżnik w Czasie',
        'year_published': extreme_year,
        'book_type': '2days'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400
    assert Book.query.filter_by(name='Książka z Ekstremalnym Rokiem').first() is None


def test_extreme_whitespace_only_name(client):
    """Tytuł książki składający się wyłącznie z 1000 spacji i białych znaków."""
    whitespace_name = " " * 1000
    data = {
        'name': whitespace_name,
        'author': 'Autor',
        'year_published': 2020,
        'book_type': '2days'
    }
    response = client.post('/books/create', json=data)
    assert response.status_code == 400
    assert Book.query.filter_by(name=whitespace_name).first() is None


def test_extreme_bulk_create_performance(client):
    """Test wydajnościowy: seryjne dodanie 50 książek i weryfikacja integralności bazy."""
    created_count = 0
    for i in range(50):
        data = {
            'name': f'Bulk Book {i}',
            'author': f'Bulk Author {i}',
            'year_published': 2000 + (i % 25),
            'book_type': '2days'
        }
        resp = client.post('/books/create', json=data)
        if resp.status_code == 302:
            created_count += 1

    assert created_count == 50
    assert Book.query.count() >= 50
