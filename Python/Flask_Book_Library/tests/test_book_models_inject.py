import pytest
from random import randint, choice
from string import ascii_letters
from datetime import date

from project.books.models import Book

# constants
MAX_NAME_LENGTH = 64
MAX_AUTHOR_LENGTH = 64
MAX_BOOK_TYPE_LENGTH = 20
MAX_STATUS_LENGTH = 20
MAX_YEAR_PUBLISHED = date.today().year
ITERATIONS_PER_TEST = 10

class Test_Book_Models_Inject:
    @pytest.fixture
    def sqli_polyglots(self):
        return [
            'SLEEP(1) /*‘ or SLEEP(1) or ‘“ or SLEEP(1) or “*/',
            """
            SLEEP(1) /*' or SLEEP(1) or '" or SLEEP(1) or "*/'
            """,
            """
            IF(SUBSTR(@@version,1,1)<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),SLEEP(1))/*'XOR(IF(SUBSTR(@@version,1,1)<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),SLEEP(1)))OR'|"XOR(IF(SUBSTR(@@version,1,1)<5,BENCHMARK(2000000,SHA1(0xDE7EC71F1)),​SLEEP(1)))OR"*/
            """
        ]
    
    @pytest.fixture
    def xss_polyglots(self):
        # from dmiessler
        return [
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

    def test_sqli(self, sqli_polyglots):
        for payload in sqli_polyglots:
            book = Book(
                name=payload,
                author=payload,
                year_published=2022,
                book_type=payload,
                status=payload
            )
        assert isinstance(book.__repr__(), str)
        assert len(book.name) <= MAX_NAME_LENGTH
        assert len(book.author) <= MAX_AUTHOR_LENGTH
        assert len(book.book_type) <= MAX_BOOK_TYPE_LENGTH
        assert len(book.status) <= MAX_STATUS_LENGTH

    def test_xss(self, xss_polyglots):
        for payload in xss_polyglots:
            book = Book(
                name=payload,
                author=payload,
                year_published=2022,
                book_type=payload,
                status=payload
            )
        assert isinstance(book.__repr__(), str)
        assert len(book.name) <= MAX_NAME_LENGTH
        assert len(book.author) <= MAX_AUTHOR_LENGTH
        assert len(book.book_type) <= MAX_BOOK_TYPE_LENGTH
        assert len(book.status) <= MAX_STATUS_LENGTH


if __name__ == "__main__":
    raise NotImplementedError("Use run_tests.bash")