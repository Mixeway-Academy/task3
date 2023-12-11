import datetime
from typing import Optional
import pytest

from .models import Book


def book(
    title: Optional[str] = None,
    author: Optional[str] = None,
    year_published: Optional[int] = None,
    book_type: Optional[str] = None,
    status: Optional[str] = None,
) -> Book:
    title = title or "Title"
    author = author or "Author"
    year_published = year_published or 2023
    book_type = book_type or "2days"
    status = status or "available"
    Book(title, "Author", 2023, "2days", "available")


# Correct data


@pytest.mark.parametrize(
    "title",
    [
        "T",
        "T" * 3,
        "T" * 64,
        "Generic Book Title",
        "So Long, and Thanks for All the Fish (Hitchhiker's Guide to the Galaxy, #4)",
        "Do Androids Dream of Electric Sheep?",
        "Androids & Dream - Electric Sheep!",
        "I Could Pee on This: and Other Poems by Cats",
    ],
)
def test_correct_title(title: str):
    book(title=title)


@pytest.mark.parametrize(
    "author",
    [
        "A",
        "A" * 3,
        "A" * 64,
        "Æ",
        "George William Russell",
        "J.K. Rowling",
        "Yi-Fen Chou",
        "Fernán Caballero",
        "Françoise Sagan",
        "P. Mustapää",
    ],
)
def test_correct_author(author: str):
    book(author=author)


@pytest.mark.parametrize(
    "year_published",
    [
        -1000,
        0,
        1000,
        1984,
        2000,
        2023,
        datetime.datetime.now(datetime.timezone.utc).year,
    ],
)
def test_correct_year_published(year_published: int):
    book(year_published=year_published)


@pytest.mark.parametrize(
    "book_type",
    [
        "2days",
        "5days",
        "10days",
    ],
)
def test_correct_book_type(book_type):
    book(book_type=book_type)


@pytest.mark.parametrize(
    "status",
    [
        "available",
    ],
)
def test_status(status: str):
    book(status=status)


# Incorrect data


@pytest.mark.parametrize(
    "title",
    [
        None,
        1,
        ("T"),
        ["T"],
        str,
        "",
        "T" * 65,
        "\n",
        "\t",
        "\x00",
        " ",
        '=@$%^*{}[]<>_\\";',
    ],
)
def test_incorrect_title(title: str):
    with pytest.raises(Exception):
        book(title=title)


@pytest.mark.parametrize(
    "author",
    [
        None,
        1,
        ("T"),
        ["T"],
        str,
        "",
        "A" * 65,
        "\n",
        "\t",
        "\x00",
        " ",
        '=@$%^*{}[]<>_\\";',
    ],
)
def test_incorrect_author(author: str):
    with pytest.raises(Exception):
        book(author=author)


@pytest.mark.parametrize(
    "year_published",
    [
        None,
        (1),
        [1],
        int,
        "1",
        -(2**8),
        2**8,
        1.123123123,
        datetime.datetime.now(datetime.timezone.utc).year + 1,
    ],
)
def test_incorrect_year_published(year_published: int):
    with pytest.raises(Exception):
        book(year_published=year_published)


@pytest.mark.parametrize(
    "book_type",
    [
        None,
        1,
        ("T"),
        ["T"],
        str,
        "",
        "T" * 65,
        "\n",
        "\t",
        "\x00",
        " ",
        '=@$%^*{}[]<>_\\";',
        "1days",
        "3days",
        "11days",
    ],
)
def test_incorrect_book_type(book_type):
    with pytest.raises(Exception):
        book(book_type=book_type)


@pytest.mark.parametrize(
    "status",
    [
        None,
        1,
        ("T"),
        ["T"],
        str,
        "",
        "T" * 65,
        "\n",
        "\t",
        "\x00",
        " ",
        '=@$%^*{}[]<>_\\";',
        "unavailable",
    ],
)
def test_instatus(status: str):
    with pytest.raises(Exception):
        book(status=status)


# Injections


SQL_INJECTIONS = [
    # From lecture
    "-- or # ",
    '" OR 1 = 1 -- -',
    "'''''''''''''UNION SELECT '2",
    "1' ORDER BY 1--+",
    "' UNION SELECT sum(columnname ) from tablename --",
    ",(select * from (select(sleep(10)))a)",
    # Subset of https://github.com/payloadbox/sql-injection-payload-list
    "'",
    "''",
    "`",
    "``",
    ",",
    '"',
    '""',
    "/",
    "//",
    "\\",
    "\\\\",
    ";",
    "' OR '1",
    "AND 1",
    "AND 0",
    "AND true",
    "AND false",
    "RLIKE (SELECT (CASE WHEN (4346=4346) THEN 0x61646d696e ELSE 0x28 END)) AND 'Txws'='",
    "1 or sleep(5)#",
    "ORDER BY SLEEP(5)",
    "UNION ALL SELECT NULL",
]


@pytest.mark.parametrize(
    "title",
    SQL_INJECTIONS,
)
def test_sql_injected_title(title: str):
    with pytest.raises(Exception):
        book(title=title)


@pytest.mark.parametrize(
    "author",
    SQL_INJECTIONS,
)
def test_sql_injected_author(author: str):
    with pytest.raises(Exception):
        book(author=author)


@pytest.mark.parametrize(
    "year_published",
    SQL_INJECTIONS,
)
def test_sql_injected_year_published(year_published: str):
    with pytest.raises(Exception):
        book(year_published=year_published)


@pytest.mark.parametrize(
    "book_type",
    SQL_INJECTIONS,
)
def test_sql_injected_book_type(book_type: str):
    with pytest.raises(Exception):
        book(book_type=book_type)


@pytest.mark.parametrize(
    "status",
    SQL_INJECTIONS,
)
def test_sql_injected_status(status: str):
    with pytest.raises(Exception):
        book(status=status)


XSS_INJECTIONS = [
    # From lecture
    '"-prompt(8)-"',
    "'-prompt(8)-'",
    "<img/src/onerror=prompt(8)>",
    '<script\\x20type="text/javascript">javascript:alert(1);</script>',
    "'`\"><\\x3Cscript>javascript:alert(1)</script>",
    '<script src=1 href=1 onerror"javascript:alert(1)"></script>',
    # Subset of https://github.com/payloadbox/xss-payload-list
    '<html onMouseOver html onMouseOver="javascript:javascript:alert(1)"></html onMouseOver>',
    '<marquee onScroll marquee onScroll="javascript:javascript:alert(1)"></marquee onScroll>',
    "\x3Cscript>javascript:alert(1)</script>",
    "'\"`><script>/* *\x2Fjavascript:alert(1)// */</script>",
    "<!--\x3E<img src=xxx:x onerror=javascript:alert(1)> -->",
    "--><!-- --\x3E> <img src=xxx:x onerror=javascript:alert(1)> -->",
    '<a href="javas\x00cript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x07cript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x0Dcript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x0Acript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x08cript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x02cript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x03cript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x04cript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x01cript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x05cript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x0Bcript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x09cript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x06cript:javascript:alert(1)" id="fuzzelement1">test</a>',
    '<a href="javas\x0Ccript:javascript:alert(1)" id="fuzzelement1">test</a>',
]


@pytest.mark.parametrize(
    "title",
    XSS_INJECTIONS,
)
def test_xss_injected_title(title: str):
    with pytest.raises(Exception):
        book(title=title)


@pytest.mark.parametrize(
    "author",
    XSS_INJECTIONS,
)
def test_xss_injected_author(author: str):
    with pytest.raises(Exception):
        book(author=author)


@pytest.mark.parametrize(
    "year_published",
    XSS_INJECTIONS,
)
def test_xss_injected_year_published(year_published: str):
    with pytest.raises(Exception):
        book(year_published=year_published)


@pytest.mark.parametrize(
    "book_type",
    XSS_INJECTIONS,
)
def test_xss_injected_book_type(book_type: str):
    with pytest.raises(Exception):
        book(book_type=book_type)


@pytest.mark.parametrize(
    "status",
    XSS_INJECTIONS,
)
def test_xss_injected_status(status: str):
    with pytest.raises(Exception):
        book(status=status)


# Extreme


EXTREME_STR = [
    "M" * 10000,
    "M" * (2**16),
    "M" * (2**32),
]

EXTREME_STR_IDS = [
    "10000 M",
    "2^16 M",
    "2^32 M",
]

EXTREME_INT = [
    -10000,
    10000,
    -(2**15 + 1),
    2**15,
    2**16,
    -(2**31 + 1),
    2**31,
    2**32,
]


@pytest.mark.parametrize("title", EXTREME_STR, ids=EXTREME_STR_IDS)
def test_extreme_title(title: str):
    with pytest.raises(Exception):
        book(title=title)


@pytest.mark.parametrize("author", EXTREME_STR, ids=EXTREME_STR_IDS)
def test_extreme_author(author: str):
    with pytest.raises(Exception):
        book(author=author)


@pytest.mark.parametrize("year_published", EXTREME_INT)
def test_extreme_year_published(year_published: int):
    with pytest.raises(Exception):
        book(year_published=year_published)


@pytest.mark.parametrize("book_type", EXTREME_STR, ids=EXTREME_STR_IDS)
def test_extreme_book_type(book_type: str):
    with pytest.raises(Exception):
        book(book_type=book_type)


@pytest.mark.parametrize("status", EXTREME_STR, ids=EXTREME_STR_IDS)
def test_extreme_status(status: str):
    with pytest.raises(Exception):
        book(status=status)
