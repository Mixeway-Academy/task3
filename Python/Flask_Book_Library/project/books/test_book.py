from project.books.models import Book


# --- dane poprawne ---
def test_valid_book():
    b = Book("Wiedzmin", "Sapkowski", 1993, "Fantasy")
    assert b.name == "Wiedzmin"
    assert b.author == "Sapkowski"
    assert b.year_published == 1993
    assert b.book_type == "Fantasy"
    assert b.status == "available"

def test_valid_status():
    b = Book("Lalka", "Prus", 1890, "Classic", "borrowed")
    assert b.status == "borrowed"


# --- dane niepoprawne (test MA prawo nie przejsc) ---
def test_negative_year():
    b = Book("X", "Y", -100, "Z")
    assert b.year_published > 0

def test_year_not_a_number():
    b = Book("X", "Y", "tysiac", "Z")
    assert isinstance(b.year_published, int)

def test_empty_name():
    b = Book("", "Y", 2000, "Z")
    assert b.name != ""

def test_future_year():
    b = Book("X", "Y", 3000, "Z")
    assert b.year_published <= 2026


# --- wstrzykniecie SQL ---
def test_sql_injection():
    payload = "'; DROP TABLE books; --"
    b = Book(payload, "Y", 2000, "Z")
    assert b.name != payload


# --- wstrzykniecie JavaScript (XSS) ---
def test_xss_injection():
    payload = "<script>alert('x')</script>"
    b = Book(payload, "Y", 2000, "Z")
    assert "<script>" not in b.name


# --- przypadki ekstremalne ---
def test_name_too_long():
    b = Book("A" * 5000, "Y", 2000, "Z")
    assert len(b.name) <= 64

def test_type_too_long():
    b = Book("X", "Y", 2000, "T" * 500)
    assert len(b.book_type) <= 20

def test_huge_year():
    b = Book("X", "Y", 10 ** 50, "Z")
    assert b.year_published < 10000
