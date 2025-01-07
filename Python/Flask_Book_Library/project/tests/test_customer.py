import pytest
from project.customers.models import Customer


def test_valid_customer():
    valid_customers = [
        { "name": "Jan kowalski", "city": "Warsaw", "age": 30, "pesel": "12345678901", "street": "Modlińska 123", "appNo": "1" },
        { "name": "Jan Kowalski", "city": "Krakow", "age": 45, "pesel": "09876543210", "street": "Sawer Armii Krajowej 456", "appNo": "2" },
        { "name": "Jan", "city": "Gdansk", "age": 25, "pesel": "56789012345", "street": "Beverly Hills 90210", "appNo": "3" },
        { "name": "Ab", "city": "Poznan", "age": 50, "pesel": "11223344556", "street": "Jana Pawła II", "appNo": "04b" },
        { "name": "名字", "city": "Wroclaw", "age": 35, "pesel": "66554433221", "street": "09a Stalina", "appNo": "51515" },
        { "name": "Адряна White", "city": "Lublin", "age": 28, "pesel": "99887766554", "street": "ABC", "appNo": "A006" },
        { "name": "Rhoshandiatellyneshiaunneveshenk Koyaanisquatsiuth Williams", "city": "Szczecin", "age": 40, "pesel": "22334455667", "street": "ul. Nowowiejska", "appNo": "12A" },
    ]
    for customer in valid_customers:
        entity = Customer(name=customer["name"], city=customer["city"], age=customer["age"], pesel=customer["pesel"], street=customer["street"], appNo=customer["appNo"])

        assert entity.name == customer["name"]
        assert entity.city == customer["city"]
        assert entity.age == customer["age"]
        assert entity.pesel == customer["pesel"]
        assert entity.street == customer["street"]
        assert entity.appNo == customer["appNo"]

def test_invalid_name():
    invalid_names = [
        "",  
        None,  
        " ",  
    ]
    for name in invalid_names:
        with pytest.raises(Exception):
            Customer(name=name, city="City", age=25, pesel="12345678901", street="Ulica", appNo="1")

def test_invalid_city():
    invalid_cities = [
        "",  
        None,  
        " ",  
    ]
    for city in invalid_cities:
        with pytest.raises(Exception):
            Customer(name="John Doe", city=city, age=25, pesel="12345678901", street="Ulica", appNo="1")

def test_invalid_age():
    invalid_ages = [
        -1,  
        0,   
        200, 
        None 
    ]
    for age in invalid_ages:
        with pytest.raises(Exception):
            Customer(name="John Doe", city="City", age=age, pesel="12345678901", street="Ulica", appNo="1")

def test_invalid_pesel():
    invalid_pesels = [
        "",         
        "abcd",     
        "123",      
        "12345678901234567890", 
        None          
    ]
    for pesel in invalid_pesels:
        with pytest.raises(Exception):
            Customer(name="John Doe", city="City", age=25, pesel=pesel, street="Ulica", appNo="1")

def test_invalid_street():
    invalid_streets = [
        "",  
        None,  
        " ",  
    ]
    for street in invalid_streets:
        with pytest.raises(Exception):
            Customer(name="John Doe", city="City", age=25, pesel="12345678901", street=street, appNo="1")

def test_invalid_appNo():
    invalid_appNos = [
        "",  
        None,  
        " ",
        "  11  s",
        "12345678901000",  
    ]
    for appNo in invalid_appNos:
        with pytest.raises(Exception):
            Customer(name="John Doe", city="City", age=25, pesel="12345678901", street="Ulica", appNo=appNo)

def test_invalid_customer_data():
    invalid_customers = [
        { "name": "John Wick", "city": "Warsaw", "age": 30, "pesel":"12345678901", "street" :"Main St 123", "appNo": "A001"},
    ]
    with pytest.raises(Exception):
        for customer in invalid_customers:
            Customer(name=customer["name"], city=customer["city"], age=customer["age"], pesel=customer["pesel"], street=customer["street"], appNo=customer["appNo"])

def test_sql_injection():
    base_customer = { "name": "John Wick", "city": "Warsaw", "age": 30, "pesel": "12345678901", "street": "Main St 123", "appNo": "A001" }
    malicious_data = []
    injections = [
        "-- or # ",
        "John'; DROP TABLE books; --",
        "\" OR 1 = 1 -- -",
        "''''''''''UNION SELECT '2",
        "1' ORDER BY 1--+",
        ]
    for key in base_customer.keys():
        if isinstance(base_customer[key], str):
            for injection in injections:
                malicious_customer = base_customer.copy()
                malicious_customer[key] = injection

                malicious_data.append(malicious_customer)

    with pytest.raises(Exception):
        for customer in malicious_data:
            Customer(name=customer["name"], city=customer["city"], age=customer["age"], pesel=customer["pesel"], street=customer["street"], appNo=customer["appNo"])

def test_javascript_injection():
    base_customer = { "name": "John Wick", "city": "Warsaw", "age": 30, "pesel": "12345678901", "street": "Main St 123", "appNo": "A001" }
    malicious_data = []
    injections = [
        "<script>alert('XSS')</script>",
        "\"-prompt(8)-\""
        "\";a=prompt,a()//",
        "';a=prompt,a()//",
        "'-eval(\"window['pro'%2B'mpt'](8)\")-'",
        "\"-eval(\"window['pro'%2B'mpt'](8)\")-\"",
        "\"onclick=prompt(8)>\"@x.y",
        "\"onclick=prompt(8)><svg/onload=prompt(8)>\"@x.y",
        ]
    
    for key in base_customer.keys():
        if isinstance(base_customer[key], str):
            for injection in injections:
                malicious_customer = base_customer.copy()
                malicious_customer[key] = injection

                malicious_data.append(malicious_customer)
                
    with pytest.raises(Exception):
        for customer in malicious_data:
            Customer(name=customer["name"], city=customer["city"], age=customer["age"], pesel=customer["pesel"], street=customer["street"], appNo=customer["appNo"])

def test_extreme_customer_data():
    base_customer = { "name": "John Wick", "city": "Warsaw", "age": 30, "pesel": "12345678901", "street": "Main St 123", "appNo": "A001" }
    extreme_data = []
    extreme_values = [
        10_000, 100_000, 
        # 1_000_000, 2_000_000, 4_000_000
        ]
    for key in base_customer.keys():
        for rep in extreme_values:
            extreme_customer = base_customer.copy()
            if isinstance(extreme_customer[key], int):
                extreme_customer[key] = rep * 10000
            elif isinstance(extreme_customer[key], str):
                extreme_customer[key] = "X" * rep
            extreme_data.append(extreme_customer)

    with pytest.raises(Exception):
        for customer in extreme_data:
            Customer(name=customer["name"], city=customer["city"], age=customer["age"], pesel=customer["pesel"], street=customer["street"], appNo=customer["appNo"])

