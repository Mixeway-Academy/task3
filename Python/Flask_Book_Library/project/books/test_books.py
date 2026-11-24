import datetime
import pytest
from project.books.models import Book

CURRENT_YEAR = datetime.date.today().year

DEFAULTS = {
    "name": "The Hobbit",
    "author": "J.R.R. Tolkien",
    "year_published": 1937,
    "book_type": "Fantasy",
    "status": "available",
}


def make_book(**overrides):
    return Book(**{**DEFAULTS, **overrides})


# 1. Valid data 
@pytest.mark.parametrize(
    "overrides",
    [
        pytest.param({}, id="default_data"),
        pytest.param(
            {"name": "Pride and Prejudice", "author": "Jane Austen", "year_published": 1813,
             "book_type": "Novel", "status": "borrowed"},
            id="borrowed_status",
        ),
        pytest.param({"name": "N" * 64, "author": "A" * 64, "book_type": "T" * 20},
                     id="max_length_fields"),
        pytest.param({"name": "O'Reilly's Guide", "author": "Tim O'Reilly"},
                     id="apostrophes_in_names"),
        pytest.param({"name": "C++ (3rd ed.): basics!"}, id="punctuation_in_title"),
        pytest.param({"year_published": 1}, id="smallest_year"),
        pytest.param({"year_published": CURRENT_YEAR}, id="current_year"),
        pytest.param({"name": "Zażółć gęślą jaźń"}, id="polish_diacritics"),
    ],
)
def test_correct_data_is_stored_in_object(overrides):
    expected = {**DEFAULTS, **overrides}
    book = make_book(**overrides)
    for field, value in expected.items():
        assert getattr(book, field) == value


def test_default_status_is_available():
    book = Book("Moby Dick", "Herman Melville", 1851, "Novel")
    assert book.status == "available"


@pytest.mark.parametrize(
    "args",
    [
        pytest.param((), id="no_arguments"),
        pytest.param(("Title only",), id="name_only"),
    ],
)
def test_constructor_requires_mandatory_arguments(args):
    with pytest.raises(TypeError):
        Book(*args)


# 2. Invalid data 
@pytest.mark.parametrize(
    "field, value",
    [
        pytest.param("name", "", id="name_empty"),
        pytest.param("name", "   ", id="name_only_spaces"),
        pytest.param("name", None, id="name_none"),
        pytest.param("author", "", id="author_empty"),
        pytest.param("author", None, id="author_none"),
        pytest.param("book_type", None, id="book_type_none"),
        pytest.param("status", "", id="status_empty"),
        pytest.param("year_published", None, id="year_none"),
        pytest.param("year_published", "1999", id="year_as_string"),
        pytest.param("year_published", 1999.9, id="year_as_float"),
        pytest.param("year_published", -1, id="year_negative"),
        pytest.param("year_published", 0, id="year_zero"),
        pytest.param("year_published", CURRENT_YEAR + 1, id="year_in_future"),
        pytest.param("status", "destroyed", id="status_not_in_allowed_values"),
        pytest.param("name", "N" * 65, id="name_too_long"),
        pytest.param("author", "A" * 65, id="author_too_long"),
        pytest.param("book_type", "T" * 21, id="book_type_too_long"),
        pytest.param("name", 12345, id="name_as_int"),
    ],
)
def test_invalid_data_is_rejected(field, value):
    with pytest.raises((ValueError, TypeError)):
        make_book(**{field: value})


# 3. SQL injection 
@pytest.mark.parametrize(
    "field, payload",
    [
        pytest.param("name", "'; DROP TABLE books; --", id="drop_table_in_name"),
        pytest.param("author", "Robert'); DROP TABLE books;--", id="bobby_tables_in_author"),
        pytest.param("book_type", "' OR '1'='1", id="or_1_eq_1_in_book_type"),
        pytest.param("status", "admin'--", id="comment_bypass_in_status"),
        pytest.param("name", "' UNION SELECT NULL, sql, NULL FROM sqlite_master --",
                     id="union_select_in_name"),
        pytest.param("author", "'; UPDATE books SET status='stolen'; --",
                     id="update_set_in_author"),
    ],
)
def test_sql_payload_is_rejected(field, payload):
    with pytest.raises((ValueError, TypeError)):
        make_book(**{field: payload})


# 4. JavaScript injection / XSS 
@pytest.mark.parametrize(
    "field, payload",
    [
        pytest.param("name", "<script>alert('XSS')</script>", id="script_tag_in_name"),
        pytest.param("author", "<img src=x onerror=alert(1)>", id="img_onerror_in_author"),
        pytest.param("book_type", '"><svg/onload=alert(1)>', id="svg_onload_in_book_type"),
        pytest.param("status", '<iframe src="javascript:alert(1)"></iframe>',
                     id="iframe_javascript_in_status"),
        pytest.param("name", "javascript:alert(1)", id="javascript_scheme_in_name"),
        pytest.param("author", "<body onload=alert(document.cookie)>",
                     id="body_onload_in_author"),
    ],
)
def test_xss_payload_is_rejected_or_sanitized(field, payload):
    try:
        book = make_book(**{field: payload})
    except (ValueError, TypeError):
        return
    stored = getattr(book, field).lower()
    assert "<" not in stored and ">" not in stored
    assert "javascript:" not in stored
    assert "onerror" not in stored and "onload" not in stored


# 5. Extreme cases
@pytest.mark.parametrize(
    "field, size",
    [
        pytest.param("name", 1_000_000, id="name_1m_chars"),
        pytest.param("author", 1_000_000, id="author_1m_chars"),
        pytest.param("book_type", 100_000, id="book_type_100k_chars"),
    ],
)
def test_extremely_long_texts_are_rejected(field, size):
    with pytest.raises((ValueError, TypeError)):
        make_book(**{field: "X" * size})


@pytest.mark.parametrize(
    "year",
    [
        pytest.param(10**10, id="ten_billion"),
        pytest.param(-(10**10), id="minus_ten_billion"),
        pytest.param(2**63, id="int64_max_plus_1"),
        pytest.param(float("inf"), id="infinity"),
        pytest.param(float("nan"), id="nan"),
    ],
)
def test_extreme_year_values_are_rejected(year):
    with pytest.raises((ValueError, TypeError)):
        make_book(year_published=year)


def test_mass_object_creation():
    books = [Book(f"Title {i}", "Author", 1900 + i % 100, "Novel") for i in range(10_000)]
    assert len(books) == 10_000
    assert books[-1].name == "Title 9999"