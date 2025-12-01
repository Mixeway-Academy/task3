import pytest
from project.customers.models import Customer

#testy poprawnych danych
def test_customer_valid_input():
    customer = Customer(
        name="Jan Kowalski",
        city="Warszawa",
        age=30,
        pesel="12345678901",
        street="ul. Prosta 1",
        appNo="A123"
    )
    
    assert customer.name == "Jan Kowalski"
    assert customer.city == "Warszawa"
    assert customer.age == 30
    assert customer.pesel == "12345678901"
    assert customer.street == "ul. Prosta 1"
    assert customer.appNo == "A123"

def test_customer_minimum_age():
    customer = Customer(
        name="Młody Użytkownik",
        city="Gdańsk",
        age=1,
        pesel="12345678901",
        street="ul. Krótka 1",
        appNo="1"
    )
    
    assert customer.age == 1

def test_customer_senior_age():
    customer = Customer(
        name="Jan Senior",
        city="Poznań",
        age=99,
        pesel="23456789012",
        street="ul. Długa 100",
        appNo="99"
    )
    
    assert customer.age == 99

#testy niepoprawnych danych

def test_customer_missing_required_field():
    with pytest.raises(TypeError):
        Customer(
            city="Kraków",
            age=40,
            pesel="12345678901",
            street="ul. Długa 5",
            appNo="B222"
        )


def test_customer_invalid_age_type():
    with pytest.raises(ValueError):
        Customer(
            name="Anna Nowak",
            city="Gdańsk",
            age="dwadzieścia",
            pesel="98765432109",
            street="ul. Krótka 3",
            appNo="C333"
        )

def test_customer_invalid_age_negative():
    with pytest.raises(ValueError, match="Age must not be negative"):
        Customer(
            name="Test User",
            city="Wrocław",
            age=-10,
            pesel="12345678901",
            street="ul. Testowa 1",
            appNo="T1"
        )

def test_customer_invalid_pesel_length():
    print('xd')
    with pytest.raises(ValueError):
        Customer(
            name="Marek Test",
            city="Poznań",
            age=25,
            pesel="123",
            street="ul. Łąkowa 4",
            appNo="D444"
        )

def test_customer_invalid_pesel_too_long():
    with pytest.raises(ValueError, match="Invalid pesel"):
        Customer(
            name="Marek Test",
            city="Poznań",
            age=25,
            pesel="123456789012345",
            street="ul. Łąkowa 4",
            appNo="D444"
        )


#SQL injection
def test_customer_sql_injection_in_name():
    with pytest.raises(ValueError, match="Name contains invalid characters"):
        Customer(
            name="'; DROP TABLE customers; --",
            city="Poznań",
            age=25,
            pesel="12345678901",
            street="ul. Łąkowa 4",
            appNo="D444"
        )


def test_customer_sql_injection_in_city():
    with pytest.raises(ValueError, match="City contains invalid characters"):
        Customer(
            name="Jan kowalskki",
            city="'; DROP TABLE customers; --",
            age=25,
            pesel="12345678901",
            street="ul. Łąkowa 4",
            appNo="D444"
        )

def test_customer_sql_injection_in_street():
    with pytest.raises(ValueError, match="Street contains invalid characters"):
        Customer(
            name="Jan kowalskki",
            city="Warszawa",
            age=25,
            pesel="12345678901",
            street="'; DROP TABLE customers; --",
            appNo="D444"
        )

def test_customer_sql_injection_in_pesel():
    with pytest.raises(ValueError, match="Pesel contains invalid characters"):
        Customer(
            name="Jan kowalskki",
            city="Warszawa",
            age=25,
            pesel="'; DROP TABLE customers; --",
            street="testowa ulica",
            appNo="D444"
        )

def test_customer_sql_injection_in_appno():
    with pytest.raises(ValueError, match="Pesel contains invalid characters"):
        Customer(
            name="Jan kowalskki",
            city="Warszawa",
            age=25,
            pesel="12345678901",
            street="testowa ulica",
            appNo="'; DROP TABLE customers; --"
        )
#JavaScript Injection

def test_customer_javascript_injection_in_name():
    with pytest.raises(ValueError, match="Name contains invalid characters"):
        Customer(
            name="<script>alert('Atak')</script>",
            city="Poznań",
            age=25,
            pesel="12345678901",
            street="ul. Łąkowa 4",
            appNo="D444"
        )


def test_customer_javascript_injection_in_city():
    with pytest.raises(ValueError, match="City contains invalid characters"):
        Customer(
            name="Jan kowalskki",
            city="<script>alert('Atak')</script>",
            age=25,
            pesel="12345678901",
            street="ul. Łąkowa 4",
            appNo="D444"
        )

def test_customer_javascript_injection_in_street():
    with pytest.raises(ValueError, match="Street contains invalid characters"):
        Customer(
            name="Jan kowalskki",
            city="Warszawa",
            age=25,
            pesel="12345678901",
            street="<script>alert('Atak')</script>",
            appNo="D444"
        )

def test_customer_javascript_injection_in_pesel():
    with pytest.raises(ValueError, match="Pesel contains invalid characters"):
        Customer(
            name="Jan kowalskki",
            city="Warszawa",
            age=25,
            pesel="<script>alert('Atak')</script>",
            street="testowa ulica",
            appNo="D444"
        )

def test_customer_javascript_injection_in_appno():
    with pytest.raises(ValueError, match="Pesel contains invalid characters"):
        Customer(
            name="Jan kowalskki",
            city="Warszawa",
            age=25,
            pesel="12345678901",
            street="testowa ulica",
            appNo="<script>alert('Atak')</script>"
        )

#testy ekstremalne
def test_customer_very_long_name():
    with pytest.raises(ValueError, match="Name is too long"):
        Customer(
            name="A" * 1000,
            city="Warszawa",
            age=30,
            pesel="77777777777",
            street="ul. Długa 1",
            appNo="L1"
        )

def test_customer_very_long_name():
    with pytest.raises(ValueError, match="Name is too long"):
        Customer(
            name='Jan kowalskki',
            city="A" * 1000,
            age=30,
            pesel="77777777777",
            street="ul. Długa 1",
            appNo="L1"
        )

def test_customer_whitespace_only_name():
    with pytest.raises(ValueError, match="Name cannot be empty"):
        Customer(
            name="   ",
            city="Warszawa",
            age=25,
            pesel="77777777777",
            street="ul. Długa 1",
            appNo="A2"
        )