import pytest
from project.books.models import Book

@pytest.fixture
def example_valid_data():
    return [
        "The Book",
        "Jan Kowalski",
        2000,
        "2days",
        "available"
    ]


def test_valid_book_name(example_valid_data):
    valid_names = ['The Hummingbird',
                   'Zwiadowcy',
                   'x' * 64]

    for valid_name in valid_names:
        name, author, year_published, book_type, status = example_valid_data
        book = Book(name = valid_name,
                    author = author,
                    year_published = year_published,
                    book_type = book_type,
                    status = status)

        assert isinstance(book.name, str)
        assert book.name == valid_name

def test_valid_book_author(example_valid_data):
    valid_authors = ['Magnus Carlsen',
                     'Ian Nepomniachtchi',
                     'x' * 64]

    for valid_author in valid_authors:
        name, author, year_published, book_type, status = example_valid_data
        book = Book(name = name,
                    author = valid_author,
                    year_published = year_published,
                    book_type = book_type,
                    status = status)

        assert isinstance(book.author, str)
        assert book.author == valid_author

def test_valid_book_year_published(example_valid_data):
    valid_years = [2000, 2023, 9999, 1900]

    for valid_year in valid_years:
        name, author, year_published, book_type, status = example_valid_data
        book = Book(name=name,
                    author=author,
                    year_published=valid_year,
                    book_type=book_type,
                    status=status)

        assert isinstance(book.year_published, int)
        assert book.year_published == valid_year

def test_valid_book_type(example_valid_data):
    valid_types = ['2days', 'Up to 2 days', '5days', 'Up to 5 days', '10days', 'Up to 10 days']

    for valid_type in valid_types:
        name, author, year_published, book_type, status = example_valid_data
        book = Book(name=name,
                    author=author,
                    year_published=year_published,
                    book_type=valid_type,
                    status=status)

        assert isinstance(book.book_type, str)
        assert book.book_type == valid_type

def test_valid_book_status(example_valid_data):
    valid_statuses = ['available', 'Checked Out', 'Reserved', 'x' * 20]

    for valid_status in valid_statuses:
        name, author, year_published, book_type, status = example_valid_data
        book = Book(name=name,
                    author=author,
                    year_published=year_published,
                    book_type=book_type,
                    status=valid_status)

        assert isinstance(book.status, str)
        assert book.status == valid_status

# ----- #

def test_invalid_book_name(example_valid_data):
    invalid_names = ['',
                   'Zwia\ndowcy',
                   'x' * 65,
                   'x' * 1000]

    for valid_name in invalid_names:
        name, author, year_published, book_type, status = example_valid_data
        book = Book(name = valid_name,
                    author = author,
                    year_published = year_published,
                    book_type = book_type,
                    status = status)

        assert isinstance(book.name, str)
        assert book.name == valid_name

def test_invalid_book_author(example_valid_data):
    invalid_authors = ['',
                     'Mag\nus Carlsen',
                     'x' * 65,
                     'x' * 1000]

    for valid_author in invalid_authors:
        name, author, year_published, book_type, status = example_valid_data
        with pytest.raises(Exception):
            book = Book(name = name,
                        author = valid_author,
                        year_published = year_published,
                        book_type = book_type,
                        status = status)

def test_invalid_book_year_published(example_valid_data):
    invalid_years = [-1000, '0', None]

    for valid_year in invalid_years:
        name, author, year_published, book_type, status = example_valid_data
        with pytest.raises(Exception):
            book = Book(name=name,
                        author=author,
                        year_published=valid_year,
                        book_type=book_type,
                        status=status)

def test_invalid_book_type(example_valid_data):
    invalid_types = [1, '', 'ss\nss']

    for valid_type in invalid_types:
        name, author, year_published, book_type, status = example_valid_data
        with pytest.raises(Exception):
            book = Book(name=name,
                        author=author,
                        year_published=year_published,
                        book_type=valid_type,
                        status=status)

def test_invalid_book_status(example_valid_data):
    invalid_statuses = [1000, 'Checked Out', 'Reserved', 'x' * 100]

    for valid_status in invalid_statuses:
        name, author, year_published, book_type, status = example_valid_data
        with pytest.raises(Exception):
            book = Book(name=name,
                        author=author,
                        year_published=year_published,
                        book_type=book_type,
                        status=valid_status)


def test_injections(example_valid_data):
    injections = [
            """
            javascript://'/</title></style></textarea></script>--><p" onclick=alert()//>*/alert()/*
            """,
            """
            javascript://</title>"/</script></style></textarea/-->*/<alert()/*' onclick=alert()//>/
            """,
            """
            javascript://</title></style></textarea>--></script><a"//' onclick=alert()//>*/alert()/*
            """,
            """
            javascript://'//" --></textarea></style></script></title><b onclick= alert()//>*/alert()/*
            """
    ]

    for injection in injections:
        with pytest.raises(Exception):
            book = Book(name=injection,
                        author=injection,
                        year_published=injection,
                        book_type=injection,
                        status=injection)

def test_large_strings():
    payload = "x" * 1000000000
    with pytest.raises(Exception):
        Book(
            name=payload,
            author=payload,
            year_published=2024,
            book_type=payload,
            status=payload
        )

def test_large_ints():
    payload = 10 ** 40
    name, author, year_published, book_type, status = example_valid_data
    with pytest.raises(Exception):
        Book(
            name=name,
            author=author,
            year_published=payload,
            book_type=book_type,
            status=status
        )
