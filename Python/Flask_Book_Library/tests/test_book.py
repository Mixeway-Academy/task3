import pytest
from project.books.models import Book


def test_correct_input():
    inputs = [
        "Dziady cz. III",
        "Ksiegi narodu polskiego i pielgrzymstwa polskiego",
    ]
    for v in inputs:
        Book(v, "Adam Mickiewicz", 1832, "Literatura piekna")


@pytest.mark.xfail(reason="Brak walidacji danych wejściowych")
def test_incorrect_input():
    payloads = [
        None,
        "null",
        "nil",
        "0",
        "",
        " ",
        "\t",
        "\n",
        "john.doe\n@hospital.com",
        " @hospital.com",
        "%20@hospital.com",
        "john.d%20e@hospital.com",
        "john._doe@hospital.com",
        "--",
        "e x a m p l e @ h o s p i t a l . c o m",
    ]
    for p in payloads:
        for args in [
            (p,                "Adam Mickiewicz", 1832, "Literatura piekna"),
            ("Dziady cz. III", p,                 1832, "Literatura piekna"),
            ("Dziady cz. III", "Adam Mickiewicz", 1832, p),
        ]:
            with pytest.raises(Exception):
                Book(*args)


@pytest.mark.xfail(reason="Brak walidacji danych wejściowych")
def test_invalid_year():
    payloads = [
        None,
        "not an int",
        "",
        1.5,
        -1,
        0,
        2**31,
        [],
    ]
    for p in payloads:
        with pytest.raises(Exception):
            Book("Dziady cz. III", "Adam Mickiewicz", p, "Literatura piekna")


@pytest.mark.xfail(reason="Brak walidacji danych wejściowych")
def test_xss_injection():
    payloads = [
        '"-prompt(8)-"',
        "`-prompt(8)-`",
        "<img/src/onerror=prompt(8)>",
        '<script\\x3Dtype="text/javascript">javascript:alert(1);</script>',
        '"\'\\x3Cscript>javascript:alert(1)</script>',
        '<script src=1 href=1 onerror="javascript:alert(1)"></script>',
    ]
    for p in payloads:
        for args in [
            (p,                "Adam Mickiewicz", 1832, "Literatura piekna"),
            ("Dziady cz. III", p,                 1832, "Literatura piekna"),
            ("Dziady cz. III", "Adam Mickiewicz", 1832, p),
        ]:
            with pytest.raises(Exception):
                Book(*args)


@pytest.mark.xfail(reason="Brak walidacji danych wejściowych")
def test_sql_injection():
    payloads = [
        "'-- or #",
        '" OR 1 = 1 --',
        "' UNION SELECT '2',",
        "1' ORDER BY 1--",
        "' UNION SELECT sum(columnname) from tablename --",
        "(select * from (select(sleep(10)))a)",
    ]
    for p in payloads:
        for args in [
            (p,                "Adam Mickiewicz", 1832, "Literatura piekna"),
            ("Dziady cz. III", p,                 1832, "Literatura piekna"),
            ("Dziady cz. III", "Adam Mickiewicz", 1832, p),
        ]:
            with pytest.raises(Exception):
                Book(*args)


@pytest.mark.xfail(reason="Brak walidacji danych wejściowych")
def test_extreme_input():
    payloads = [
        "X" * 10000,
        "X" * 100000,
        "X" * 1000000,
        "X" * 2000000,
        "X" * 4000000,
    ]
    for p in payloads:
        for args in [
            (p,                "Adam Mickiewicz", 1832, "Literatura piekna"),
            ("Dziady cz. III", p,                 1832, "Literatura piekna"),
            ("Dziady cz. III", "Adam Mickiewicz", 1832, p),
        ]:
            with pytest.raises(Exception):
                Book(*args)
