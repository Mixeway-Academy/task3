import pytest
from project import app, db
from project.books.models import Book


@pytest.fixture
def app_context():
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


def test_correct_input_book(app_context):
    book = Book(
        name="Clean Code",
        author="Robert C. Martin",
        year_published=2008,
        book_type="10days",
    )
    assert book.name == "Clean Code"
    assert book.author == "Robert C. Martin"
    assert book.year_published == 2008
    assert book.book_type == "10days"
    assert book.status == "available"


@pytest.mark.parametrize(
    "name,author,year_published,book_type",
    [
        (None, "Author", 2020, "5days"),
        ("", "Author", 2020, "5days"),
        ("   \t\n  ", "Author", 2020, "5days"),
        ("Book Name", None, 2020, "5days"),
        ("Book Name", "", 2020, "5days"),
        ("Book Name", "Author", "nie_liczba", "5days"),
        ("Book Name", "Author", -500, "5days"),
        ("Book Name", "Author", 9999, "5days"),
        ("Book Name", "Author", 2020, "invalid_type"),
    ],
)
def test_incorrect_input_book(app_context, name, author, year_published, book_type):
    # Zgodnie z treścią zadania: jeśli model nie odrzuca niepoprawnych danych,
    # asercja odrzucenia błędu zakończy test niepowodzeniem.
    with pytest.raises((ValueError, TypeError)):
        Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
        )


@pytest.mark.parametrize(
    "payload",
    [
        "' OR 1=1 --",
        "\" OR 1=1",
        "1' ORDER BY 1--+",
        "UNION SELECT sum(columnname) from tablename",
        "', (select * from (select(sleep(10)))a)",
    ],
)
def test_sqli_input_book(app_context, payload):
    with pytest.raises((ValueError, TypeError)):
        Book(
            name=payload,
            author=payload,
            year_published=2022,
            book_type="5days",
        )


@pytest.mark.parametrize(
    "payload",
    [
        "<script>alert(1)</script>",
        "<img/src/onerror=prompt(8)>",
        "\"-prompt(8)-\"",
        "<script src=1 href=1 onerror=\"javascript:alert(1)\"></script>",
    ],
)
def test_xss_input_book(app_context, payload):
    with pytest.raises((ValueError, TypeError)):
        Book(
            name=payload,
            author=payload,
            year_published=2022,
            book_type="5days",
        )


@pytest.mark.parametrize("length", [65, 256, 10_000, 100_000, 1_000_000])
def test_extreme_and_boundary_input_book(app_context, length):
    extreme_text = "A" * length
    with pytest.raises((ValueError, TypeError)):
        Book(
            name=extreme_text,
            author=extreme_text,
            year_published=2022,
            book_type=extreme_text[:25],
        )