import pytest
from project.books.models import Book

# ========== 1. POPRAWNE DANE ==========
def test_valid_book():
    book = Book("Pan Tadeusz", "Mickiewicz", 1834, "paper")
    assert book.name == "Pan Tadeusz"
    assert book.author == "Mickiewicz"
    assert book.year_published == 1834
    assert book.book_type == "paper"
    assert book.status == "available"  # wartość domyślna


def test_valid_book_custom_status():
    book = Book("Lalka", "Prus", 1890, "ebook", status="borrowed")
    assert book.status == "borrowed"


# ========== 2. NIEPOPRAWNE DANE ==========
@pytest.mark.xfail(reason="Model nie waliduje typu roku")
def test_year_as_text():
    book = Book("Zła data", "Autor", "tysiąc osiemset", "paper")
    assert isinstance(book.year_published, int)


@pytest.mark.xfail(reason="Model dopuszcza pustą nazwę")
def test_empty_name():
    book = Book("", "Autor", 2000, "paper")
    assert book.name != ""


@pytest.mark.xfail(reason="Model dopuszcza ujemny rok")
def test_negative_year():
    book = Book("Przyszłość", "Autor", -500, "paper")
    assert book.year_published > 0


# ========== 3. WSTRZYKNIĘCIE SQL / JavaScript ==========
def test_sql_injection_passes_through():
    payload = "'; DROP TABLE books; --"
    book = Book(payload, "Autor", 2000, "paper")
    # Model nie sanityzuje — ładunek jest przechowywany dosłownie (potencjalna podatność)
    assert book.name == payload


@pytest.mark.xfail(reason="Model nie sanityzuje danych — brak ochrony przed XSS")
def test_js_injection_sanitized():
    payload = "<script>alert('xss')</script>"
    book = Book(payload, "Autor", 2000, "paper")
    assert "<script>" not in book.name


# ========== 4. WARUNKI BRZEGOWE ==========
def test_name_exactly_64_chars():
    name = "A" * 64  # dokładnie limit kolumny String(64)
    book = Book(name, "Autor", 2000, "paper")
    assert len(book.name) == 64


@pytest.mark.xfail(reason="Brak walidacji długości — nazwa > 64 znaki przechodzi")
def test_name_65_chars_over_limit():
    book = Book("A" * 65, "Autor", 2000, "paper")
    assert len(book.name) <= 64


def test_year_current():
    book = Book("Nowość", "Autor", 2026, "paper")
    assert book.year_published == 2026


def test_status_exactly_20_chars():
    book = Book("Status test", "Autor", 2000, "paper", status="A" * 20)
    assert len(book.status) == 20


# ========== 5. DANE EKSTREMALNE ==========
@pytest.mark.xfail(reason="Brak walidacji długości — nazwa 10000 znaków przechodzi")
def test_very_long_name():
    book = Book("A" * 10000, "Autor", 2000, "paper")
    assert len(book.name) <= 64


@pytest.mark.xfail(reason="Brak walidacji zakresu roku")
def test_year_huge_number():
    book = Book("Daleka przyszłość", "Autor", 10 ** 9, "paper")
    assert book.year_published < 3000


def test_unicode_and_emoji():
    book = Book("Книга 📚 日本語", "Autor", 2000, "paper")
    assert book.name == "Книга 📚 日本語"

