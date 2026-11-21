import pytest

from project import app, db
from project.books.models import Book

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'


@pytest.fixture(autouse=True)
def setup_db():
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()

# pozytywne

def test_create_book():
    book = Book("Dune", "Frank Herbert", 1965, "Sci-Fi")
    assert book.name == "Dune"
    assert book.author == "Frank Herbert"
    assert book.year_published == 1965
    assert book.status == "available"


def test_save_book():
    db.session.add(Book("Dune", "Frank Herbert", 1965, "Sci-Fi"))
    db.session.commit()
    assert Book.query.filter_by(name="Dune").first().author == "Frank Herbert"

# negatywne

def test_empty_name():
    with pytest.raises(ValueError):
        Book("", "Frank Herbert", 1965, "Sci-Fi")


def test_name_none():
    with pytest.raises(ValueError):
        Book(None, "Frank Herbert", 1965, "Sci-Fi")


def test_year_is_text():
    with pytest.raises(ValueError):
        Book("Dune", "Frank Herbert", "abc", "Sci-Fi")


def test_negative_year():
    with pytest.raises(ValueError):
        Book("Dune", "Frank Herbert", -100, "Sci-Fi")

# wstrzyknięcie kodu

def test_sql_injection():
    with pytest.raises(ValueError):
        Book("'; DROP TABLE books; --", "Frank Herbert", 1965, "Sci-Fi")


def test_javascript_injection():
    with pytest.raises(ValueError):
        Book("<script>alert(1)</script>", "Frank Herbert", 1965, "Sci-Fi")

# przypadki ekstremalne

def test_very_long_name():
    with pytest.raises(ValueError):
        Book("a" * 10000, "Frank Herbert", 1965, "Sci-Fi")


def test_huge_year():
    with pytest.raises(ValueError):
        Book("Dune", "Frank Herbert", 10 ** 20, "Sci-Fi")
