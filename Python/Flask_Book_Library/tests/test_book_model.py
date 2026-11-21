import pytest
from project.books.models import Book

# @pytest.mark.parametrize


# Testy poprawnych danych
@pytest.mark.parametrize(
    "name, author, year_published, book_type, status",
    [
        ("Książka 1", "Autor 1", 2020, "Klasyka", "available"),
        ("Książka 2", "Autor 2", 2019, "Sci-Fi", "checked out"),
        ("Książka 3", "Autor 3", 2021, "Naukowa", "available"),
        ("A" * 64, "B" * 64, 2026, "C" * 20, "D" * 20),
        ("A", "B", 0, "C", "D"),
        ("A", "B", -100000, "C", "D"),
    ],
    ids=[
        "valid_data_1",
        "valid_data_2",
        "valid_data_3",
        "max_length_fields",
        "year_published_zero",
        "year_published_negative",
    ],
)
def test_book_model_valid_data(name, author, year_published, book_type, status):
    book = Book(
        name=name,
        author=author,
        year_published=year_published,
        book_type=book_type,
        status=status,
    )
    assert book.name == name
    assert book.author == author
    assert book.year_published == year_published
    assert book.book_type == book_type
    assert book.status == status


# Testy niepoprawnych danych
@pytest.mark.parametrize(
    "name, author, year_published, book_type, status",
    [
        ("", "Autor 1", 2020, "Klasyka", "available"),  # Pusta nazwa
        ("Książka 2", "", 2019, "Sci-Fi", "checked out"),  # Pusty autor
        (
            "Książka 3",
            "Autor 3",
            "2021",
            "Naukowa",
            "available",
        ),  # Rok jako ciąg znaków
        (
            "Książka 4",
            "Autor 4",
            2020.5,
            "Klasyka",
            "available",
        ),  # Rok jako liczba zmiennoprzecinkowa
        (
            "Książka 5",
            "Autor 5",
            2020 + 1j,
            "Klasyka",
            "available",
        ),  # Rok jako liczba zespolona
        ("Książka 6", "Autor 6", 2020, "", "available"),  # Pusty typ książki
        ("Książka 7", "Autor 7", 2020, "Klasyka", ""),  # Pusty status
        ("A" * 65, "B" * 64, 2026, "C" * 20, "D" * 20),  # Nazwa za długa
        ("A" * 64, "B" * 65, 2026, "C" * 20, "D" * 20),  # Autor za długi
        ("A" * 64, "B" * 64, 2026, "C" * 21, "D" * 20),  # Typ książki za długi
        ("A" * 64, "B" * 64, 2026, "C" * 20, "D" * 21),  # Status za długi
        (None, "B", 2026, "C", "D"),  # Brak nazwy
        ("A", None, 2026, "C", "D"),  # Brak autora
        ("A", "B", None, "C", "D"),  # Brak roku publikacji
        ("A", "B", 2026, None, "D"),  # Brak typu książki
        ("A", "B", 2026, "C", None),  # Brak statusu
    ],
    ids=[
        "empty_name",
        "empty_author",
        "string_year_published",
        "float_year_published",
        "complex_year_published",
        "empty_book_type",
        "empty_status",
        "name_too_long",
        "author_too_long",
        "book_type_too_long",
        "status_too_long",
        "missing_name",
        "missing_author",
        "missing_year_published",
        "missing_book_type",
        "missing_status",
    ],
)
def test_book_model_invalid_data(name, author, year_published, book_type, status):
    with pytest.raises(Exception):
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
            status=status,
        )


# Testy związane z próbą wstrzyknięcia kodu SQL i kodu JavaScript
@pytest.mark.parametrize(
    "field, payload",
    [
        ("name", "Książka 1; DROP TABLE books;"),
        ("author", "Autor 1; DROP TABLE books;"),
        ("book_type", "Klasyka; DROP TABLE books;"),
        ("status", "available; DROP TABLE books;"),
        ("name", "<script>alert('XSS');</script>"),
        ("author", "<script>alert('XSS');</script>"),
        ("book_type", "<script>alert('XSS');</script>"),
        ("status", "<script>alert('XSS');</script>"),
    ],
    ids=[
        "sql_injection_name",
        "sql_injection_author",
        "sql_injection_book_type",
        "sql_injection_status",
        "xss_injection_name",
        "xss_injection_author",
        "xss_injection_book_type",
        "xss_injection_status",
    ],
)
def test_book_model_injection_attacks(field, payload):
    kwargs = {
        "name": "Książka 1",
        "author": "Autor 1",
        "year_published": 2026,
        "book_type": "Klasyka",
        "status": "available",
    }
    kwargs[field] = payload

    with pytest.raises(Exception):
        book = Book(**kwargs)


# Testy ekstremalne
@pytest.mark.parametrize(
    "name, author, year_published, book_type, status",
    [
        ("A" * 1000, "B" * 1000, 2026, "C" * 1000, "D" * 1000),  # Długie pola
        (
            "A" * 1000000,
            "B" * 1000000,
            2026,
            "C" * 1000000,
            "D" * 1000000,
        ),  # Bardzo długie pola
        ("A", "B", 9999999999, "C", "D"),  # Bardzo duży rok publikacji
        ("A", "B", -9999999999, "C", "D"),  # Bardzo mały rok publikacji
        ("A", "B", 2026, "C" * 1000, "D" * 1000),  # Bardzo długi typ książki i status
    ],
    ids=[
        "long_fields",
        "very_long_fields",
        "very_large_year_published",
        "very_small_year_published",
        "very_long_book_type_and_status",
    ],
)
def test_book_model_extreme_cases(name, author, year_published, book_type, status):
    with pytest.raises(Exception):
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
            status=status,
        )
