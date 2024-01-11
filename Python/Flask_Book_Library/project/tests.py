import pytest
from project.customers.models import Customer


def test_valid_customer_data():
    customer = Customer(
        name="John Doe",
        city="New York",
        age=30,
        pesel="1234567890",
        street="5th Avenue",
        appNo="101",
    )
    assert customer.name == "John Doe"
    assert customer.city == "New York"
    assert customer.age == 30
    assert customer.pesel == "1234567890"
    assert customer.street == "5th Avenue"
    assert customer.appNo == "101"


def test_invalid_customer_data():
    # Assuming age must be an integer and name must be a string
    with pytest.raises(ValueError):
        customer = Customer(
            name=12345,
            city="123",
            age="InvalidAge",
            pesel="abcdefghij",
            street="Broadway",
            appNo="102",
        )


def test_sql_injection_attempt():
    malicious_sql = "DROP TABLE customers;"
    with pytest.raises(ValueError):
        customer = Customer(
            name=malicious_sql,
            city="New York",
            age=30,
            pesel="sqlinject",
            street="Wall Street",
            appNo="103",
        )


def test_javascript_injection_attempt():
    malicious_js = "<script>alert('Hacked');</script>"
    with pytest.raises(ValueError):
        customer = Customer(
            name="Alice",
            city=malicious_js,
            age=40,
            pesel="jsinject",
            street="Madison Avenue",
            appNo="104",
        )
    assert customer.city == malicious_js  # Assuming no sanitation in place
