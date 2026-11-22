import pytest
from project.books.models import Book

VALID_TYPES = ["2days", "5days", "10days"]
VALID_STATUSES = ["available", "unavailable"]

BOOK_DATA = {
    "name": "Pan Tadeusz",
    "author": "Adam Mickiewicz",
    "year_published": 1834,
    "book_type": "2days",
    "status": "available"
}


class TestValidData:
    @pytest.mark.parametrize(
        "name,author,year_published,book_type",
        [
            ("Pan Tadeusz", "Adam Mickiewicz", 1834, "2days"),
            ("1984", "George Orwell", 1949, "5days"),
            ("Lalka (tom 1)", "Bolesław Prus", 1890, "10days"),
        ],
    )
    def test_book_valid_data(self, name, author, year_published, book_type):
        book = Book(
            name=name,
            author=author,
            year_published=year_published,
            book_type=book_type,
        )
        assert book.name == name
        assert book.author == author
        assert book.year_published == year_published
        assert book.book_type == book_type
        assert book.book_type in VALID_TYPES
        assert book.status == "available"


class TestInvalidData:
    @pytest.mark.parametrize("bad_name", ["", "   ", None, 12345])
    def test_book_invalid_name(self, bad_name):
        invalid_data = BOOK_DATA
        invalid_data["name"] = bad_name
        with pytest.raises(ValueError):
            Book(**invalid_data)

    @pytest.mark.parametrize("bad_author", ["", "   ", None, 12345])
    def test_book_invalid_author(self, bad_author):
        invalid_data = BOOK_DATA
        invalid_data["author"] = bad_author
        with pytest.raises(ValueError):
            Book(**invalid_data)

    @pytest.mark.parametrize("bad_year", [-500, 0, 9999, "not_year", None])
    def test_book_invalid_year(self, bad_year):
        invalid_data = BOOK_DATA
        invalid_data["year_published"] = bad_year
        with pytest.raises(ValueError):
            Book(**invalid_data)

    @pytest.mark.parametrize("bad_type", ["", "    ", "not_type", None])
    def test_book_invalid_type(self, bad_type):
        invalid_data = BOOK_DATA
        invalid_data["book_type"] = bad_type
        with pytest.raises(ValueError):
            Book(**invalid_data)

    @pytest.mark.parametrize("bad_status", ["", "    ", "not_status", None])
    def test_book_invalid_year(self, bad_status):
        invalid_data = BOOK_DATA
        invalid_data["status"] = bad_status
        with pytest.raises(ValueError):
            Book(**invalid_data)

class TestInjection:
    SQL_INJECTION_PAYLOADS = [
        "' OR '1'='1",
        "'; DROP TABLE books; --",
        "1 UNION SELECT username, password FROM users--",
        "admin'/*",
    ]

    XSS_PAYLOADS = [
        "<script>alert('XSS')</script>",
        "<img src=x onerror=alert(1)>",
        "javascript:alert(document.cookie)",
        "<svg onload=alert('XSS')>",
    ]

    FIELDS = ["name", "author", "year_published", "book_type", "status"]

    @pytest.mark.parametrize("field", FIELDS)
    @pytest.mark.parametrize("payload", SQL_INJECTION_PAYLOADS)
    def test_book_sql_injection_payloads(self, field, payload):
        invalid_data = BOOK_DATA.copy()
        invalid_data[field] = payload
        with pytest.raises(ValueError):
            Book(**invalid_data)

    @pytest.mark.parametrize("field", FIELDS)
    @pytest.mark.parametrize("payload", XSS_PAYLOADS)
    def test_book_xss_payloads(self, field, payload):
        invalid_data = BOOK_DATA.copy()
        invalid_data[field] = payload
        with pytest.raises(ValueError):
            Book(**invalid_data)

class TestExtremeData:
    @pytest.mark.parametrize("length", [65, 1000, 1_000_000])
    def test_book_name_too_long(self, length):
        data = BOOK_DATA.copy()
        data["name"] = "a" * length
        with pytest.raises(ValueError):
            Book(**data)

    @pytest.mark.parametrize("length", [65, 1000, 1_000_000])
    def test_book_author_too_long(self, length):
        data = BOOK_DATA.copy()
        data["author"] = "a" * length
        with pytest.raises(ValueError):
            Book(**data)

    @pytest.mark.parametrize("bad_year", [2**31, 2**63, 2**64, -(2**63), 10**100, -(10**100)])
    def test_book_year_huge_integers(self, bad_year):
        data = BOOK_DATA.copy()
        data["year_published"] = bad_year
        with pytest.raises(ValueError):
            Book(**data)

    @pytest.mark.parametrize("bad_year", [float("inf"), float("-inf"), float("nan"), True, False])
    def test_book_year_special_values(self, bad_year):
        data = BOOK_DATA.copy()
        data["year_published"] = bad_year
        with pytest.raises(ValueError):
            Book(**data)

    @pytest.mark.parametrize("field", ["name", "author", "book_type", "status"])
    @pytest.mark.parametrize("bad_value", ["abc\x00def", "ab\x07cd", "ab\x1b[31mcd", "ab\r\ncd"])
    def test_book_control_characters(self, field, bad_value):
        data = BOOK_DATA.copy()
        data[field] = bad_value
        with pytest.raises(ValueError):
            Book(**data)

    @pytest.mark.parametrize("bad_value", ["\u202eresu", "ad\u200bmin", "\ufeffTytuł"])
    def test_book_invisible_unicode_in_name(self, bad_value):
        data = BOOK_DATA.copy()
        data["name"] = bad_value
        with pytest.raises(ValueError):
            Book(**data)

    @pytest.mark.parametrize("bad_type", ["2DAYS", " 2days", "2days ", "2days\n", "２days", "2days" * 1000])
    def test_book_type_near_misses(self, bad_type):
        data = BOOK_DATA.copy()
        data["book_type"] = bad_type
        with pytest.raises(ValueError):
            Book(**data)

    @pytest.mark.parametrize("bad_status", ["AVAILABLE", " available", "available\x00", "available" * 1000])
    def test_book_status_near_misses(self, bad_status):
        data = BOOK_DATA.copy()
        data["status"] = bad_status
        with pytest.raises(ValueError):
            Book(**data)

    @pytest.mark.parametrize("bad_value", [b"bytes", [1, 2], {"a": 1}, (1,), object()])
    def test_book_exotic_types(self, bad_value):
        for field in ("name", "author", "book_type", "status"):
            data = BOOK_DATA.copy()
            data[field] = bad_value
            with pytest.raises(ValueError):
                Book(**data)