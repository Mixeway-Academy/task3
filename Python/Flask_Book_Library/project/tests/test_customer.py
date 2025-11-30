from project.customers.models import Customer
import pytest
from project.tests.fixtures import app, session
import sqlite3


# 1. Testy poprawnych danych
def test_create_valid_customer(session):
    """Przykładowe poprawne dane"""
    customer = Customer(
        name="Jan Kowalski",
        city="Warszawa",
        age=35,
        pesel="90010112345",
        street="Marszałkowska 10",
        appNo="12",
    )

    session.add(customer)
    session.commit()

    saved_customer = Customer.query.filter_by(pesel="90010112345").first()
    assert saved_customer is not None
    assert saved_customer.name == "Jan Kowalski"
    assert saved_customer.city == "Warszawa"


def test_customer_repr(session):
    """Testowanie reprezentacji tekstowej"""
    customer = Customer(
        name="Jan Kowalski",
        city="Warszawa",
        age=35,
        pesel="90010112345",
        street="Marszałkowska 10",
        appNo="12",
    )

    session.add(customer)
    session.commit()

    c_id = customer.id
    expected_repr = f"Customer(ID: {c_id}, Name: Jan Kowalski, City: Warszawa, Age: 35, Pesel: 90010112345, Street: Marszałkowska 10, AppNo: 12)"

    assert str(customer) == expected_repr


def test_duplicate_name(session):
    """Klienci mogą mieć takie same imię i nazwisko i nie powinno to zwrócić błędu"""
    c1 = Customer("Jan Kowalski", "Gdańsk", 40, "80010111111", "Długa 1", "X1")
    session.add(c1)
    session.commit()

    c2 = Customer("Jan Kowalski", "Gdynia", 41, "80010122222", "Morska 2", "X2")
    session.add(c2)
    session.commit()


# 2. Testy niepoprawnych danych
def test_duplicate_pesel_error(session):
    """
    Nie powinno być 2 klientów o takim samym numerze pesel
    """
    c1 = Customer("Jan Kowalski", "Gdańsk", 40, "80010111111", "Długa 1", "X1")
    session.add(c1)
    session.commit()

    c2 = Customer("Anna Nowak", "Gdynia", 40, "80010111111", "Morska 2", "X2")
    session.add(c2)

    with pytest.raises(sqlite3.IntegrityError):
        session.commit()


def test_missing_fields_behavior(session):
    """
    Sprawdzenie czy klient nie zostanie utworzony gdy nie ma danych
    """
    customer = Customer(None, None, None, None, None, None)

    session.add(customer)
    session.commit()

    with pytest.raises(sqlite3.IntegrityError):
        session.commit()

def test_age_as_string(session):
    """
    Sprawdzenie czy wiek musi być liczbą
    """
    customer = Customer("Jan Kowalski", "Gdańsk", "czterdzieści", "80010111111", "Długa 1", "X1")

    session.add(customer)
    session.commit()

    with pytest.raises(sqlite3.IntegrityError):
        session.commit()

def test_negative_age(session):
    """Sprawdzenie czy błąd gdy wiek ujemny"""
    customer = Customer(
        name="Jan Kowalski",
        city="Warszawa",
        age=-1,
        pesel="90010112345",
        street="Marszałkowska 10",
        appNo="12",
    )
    session.add(customer)

    with pytest.raises((sqlite3.IntegrityError)):
        session.commit()

# 3. Testy Injection (SQL & JavaScript)
def test_sql_injection_in_name(session):
    """Sprawdza odporność na SQL Injection w polu name."""
    malicious_name = "Jan'); DROP TABLE customers; --"
    customer = Customer(
        malicious_name, "Gdynia", 40, "80010111111", "Morska 2", "X2"
    )

    session.add(customer)
    session.commit()

    assert Customer.query.count() == 1
    saved = Customer.query.filter_by(pesel="80010111111").first()
    assert saved.name == malicious_name


def test_xss_in_street_field(session):
    """
    Sprawdza zapisywanie skryptów JS w polu street. 
    Założenie że powinny być czyszczone przed zapisem do bazy (Input Sanitization).
    """
    xss_payload = "<script>alert('Stealing Data')</script>"
    customer = Customer("Jan Kowalski", "Gdańsk", 40, "80010111111", xss_payload, "X1")

    session.add(customer)
    session.commit()

    saved = Customer.query.filter_by(name="Jan Kowalski").first()

    assert saved.street != xss_payload


# 4. Testy ekstremalne (Boundary Values)
def test_boundary_appNo_overflow(session):
    """Limit na 10 znaków, powinno rzucić błąd."""
    customer = Customer(
        name="Jan Kowalski",
        city="Warszawa",
        age=35,
        pesel="90010112345",
        street="Marszałkowska 10",
        appNo="A" * 1000,
    )
    session.add(customer)
    
    with pytest.raises((sqlite3.IntegrityError)):
        session.commit()

def test_age_extreme_values(session):
    """Sprawdza logikę dla zbyt dużego wieku."""
    c = Customer(
        name="Jan Kowalski",
        city="Warszawa",
        age=999999,
        pesel="90010112345",
        street="Marszałkowska 10",
        appNo="12",
    )

    session.add(c)
    with pytest.raises((sqlite3.IntegrityError)):
        session.commit()


def test_pesel_too_long(session):
    """
    Sprawdza pole PESEL, który powinien mieć 11 znaków
    """
    c = Customer(
        name="Jan Kowalski",
        city="Warszawa",
        age=30,
        pesel="1" * 64,
        street="Marszałkowska 10",
        appNo="12",
    )

    session.add(c)
    with pytest.raises((sqlite3.IntegrityError)):
        session.commit()
