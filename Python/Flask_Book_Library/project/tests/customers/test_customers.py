import pytest
from project.customers.models import Customer

def test_valid_input():
    customer = Customer(
        name="Adam",
        city="Warszawa",
        age=33,
        pesel="04545506411",
        street="Krzywa 10/12",
        appNo="A123"
    )

    assert customer.name == "Adam"
    assert customer.city == "Warszawa"
    assert customer.age == 33
    assert customer.pesel == "04545506411"
    assert customer.street == "Krzywa 10/12"
    assert customer.appNo == "A123"

def test_invalid_age():
    with pytest.raises(ValueError, match="Age must be greater than 0"):
        Customer(
            name="Dummy",
            city="Warszawa",
            age=-23,
            pesel="12344448911",
            street="Krzywa 10/11",
            appNo="A133"
        )

def test_missing_required_fields():
    with pytest.raises(TypeError):
        Customer(
            name="Dummy",
            city="Warszawa",
            age=40,
            pesel="12345555501"
        )

def test_invalid_age_type():
    with pytest.raises(ValueError):
        Customer(
            name="Adam",
            city="Kraków",
            age="sto",
            pesel="98765435555",
            street="Słoniowa 69",
            appNo="D442"
        )

def test_invalid_length_of_pesel_too_long():
    with pytest.raises(ValueError):
        Customer(
            name="Arek",
            city="Gdańsk",
            age=235,
            pesel="112331231231255565",
            street="Bącza 4",
            appNo="D444"
        )

def test_invalid_length_of_pesel_too_short():
    with pytest.raises(ValueError):
        Customer(
            name="Arek",
            city="Gdańsk",
            age=235,
            pesel="115",
            street="Bącza 4",
            appNo="D444"
        )

def test_sql_injection_like_name():
    with pytest.raises(ValueError, match="Invalid character in name"):
        Customer(
            name="'; DROP_DISABLED_TABLE customers; --",
            city="Poznań",
            age=25,
            pesel="12345678901",
            street="ul. Łąkowa 4",
            appNo="X101"
        )

def test_sql_injection_like_city():
    with pytest.raises(ValueError, match="Invalid character in city"):
        Customer(
            name="Adam",
            city="OR '1'='1' /*TEST*/",
            age=31,
            pesel="98765432109",
            street="ul. Długa 12",
            appNo="X102"
        )

def test_js_injection_like_name():
    with pytest.raises(ValueError, match="Invalid character in name"):
        Customer(
            name="<script>alert('test')</script>",
            city="Kraków",
            age=22,
            pesel="12345678901",
            street="ul. Wiślana 5",
            appNo="X103"
        )

def test_js_injection_on_city():
    with pytest.raises(ValueError, match="Invalid character in city"):
        Customer(
            name="Marek",
            city="<img src=x onerror='alert(1)' />",
            age=44,
            pesel="23456789012",
            street="ul. Torowa 9",
            appNo="X104"
        )

def test_extreme_long_name():
    long_name = "A" * 10000 
    with pytest.raises(ValueError):
        Customer(
            name=long_name,
            city="Kraków",
            age=30,
            pesel="12345678901",
            street="ul. Długa 2",
            appNo="X999"
        )

def test_unicode_chaos_name():
    zalgo = "A̷͉̙̥͔͇̍̈́͋̕͝d̵̠̖̜̽̎̏á̷̼̮̥͓m̴̠͈͐̉͐"
    with pytest.raises(ValueError):
        Customer(
            name=zalgo,
            city="Łódź",
            age=22,
            pesel="98765432109",
            street="ul. Chaotyczna 1",
            appNo="X111"
        )

def test_extreme_js_injection_like():
    payload = "<script>while(true){console.log('🔥');}</script>"
    with pytest.raises(ValueError):
        Customer(
            name="Marek",
            city=payload,
            age=28,
            pesel="11122233344",
            street="ul. XSSowa 1",
            appNo="X303"
        )
