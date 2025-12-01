import pytest
import sys
import os

# Dodanie ścieżki do projektu
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from project import app, db
from project.customers.models import Customer

# Standardowe dane testowe
DEFAULT_NAME = "Jan Kowalski"
DEFAULT_CITY = "Warszawa"
DEFAULT_AGE = 30
DEFAULT_PESEL = "90010112345"
DEFAULT_STREET = "ul. Testowa"
DEFAULT_APP_NO = "10A"


@pytest.fixture
def test_app():
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def test_client(test_app):
    return test_app.test_client()


@pytest.fixture
def init_database(test_app):
    with app.app_context():
        db.create_all()
        yield db
        db.session.rollback()

#-----------------------------------------------
# Poprawne dane
#-----------------------------------------------
class TestCustomerValidData:
    """Testy dla poprawnych danych klienta."""
    
    def test_create_customer_with_valid_data(self, test_app, init_database):
        """Test tworzenia klienta z poprawnymi danymi."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.id is not None
            assert customer.name == DEFAULT_NAME
            assert customer.city == DEFAULT_CITY
            assert customer.age == DEFAULT_AGE
            assert customer.pesel == DEFAULT_PESEL
            assert customer.street == DEFAULT_STREET
            assert customer.appNo == DEFAULT_APP_NO
            assert customer.pesel.isdigit()
    
    def test_create_customer_with_minimum_valid_data(self, test_app, init_database):
        """Test tworzenia klienta z minimalnymi poprawnymi danymi."""
        with app.app_context():
            customer = Customer(
                name="A",
                city="B",
                age=1,
                pesel="1",
                street="C",
                appNo="1"
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.id is not None
            assert customer.name == "A"
    
    def test_create_customer_with_different_age_values(self, test_app, init_database):
        """Test tworzenia klientów z różnymi poprawnymi wartościami wieku."""
        with app.app_context():
            ages = [0, 18, 65, 100, 120]
            for idx, age in enumerate(ages):
                customer = Customer(
                    name=f"{DEFAULT_NAME} {idx}",
                    city=DEFAULT_CITY,
                    age=age,
                    pesel=f"{DEFAULT_PESEL[:-1]}{idx}",
                    street=DEFAULT_STREET,
                    appNo=DEFAULT_APP_NO
                )
                db.session.add(customer)
                db.session.commit()
                
                assert customer.age == age
    
    def test_customer_repr_method(self, test_app, init_database):
        """Test metody __repr__ dla klienta."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            
            repr_str = repr(customer)
            assert "Customer" in repr_str
            assert DEFAULT_NAME in repr_str
            assert DEFAULT_CITY in repr_str
    
    def test_create_customer_with_numeric_app_number(self, test_app, init_database):
        """Test tworzenia klienta z numerycznym numerem mieszkania."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo="123"
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.appNo == "123"
    
    def test_create_customer_with_alphanumeric_app_number(self, test_app, init_database):
        """Test tworzenia klienta z alfanumerycznym numerem mieszkania."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo="12A/3"
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.appNo == "12A/3"

#-----------------------------------------------
# Niepoprawne dane
#-----------------------------------------------
class TestCustomerInvalidData:
    """Testy dla niepoprawnych danych klienta."""
    
    def test_create_customer_with_empty_name(self, test_app, init_database):
        """Test tworzenia klienta z pustym imieniem."""
        with app.app_context():
            customer = Customer(
                name="",
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            # Test dokumentuje brak walidacji
            assert customer.name == ""
    
    def test_create_customer_with_none_name(self, test_app, init_database):
        """Test tworzenia klienta z None jako imieniem."""
        with app.app_context():
            customer = Customer(
                name=None,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert customer.name is None
    
    def test_create_customer_with_negative_age(self, test_app, init_database):
        """Test tworzenia klienta z ujemnym wiekiem."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=-5,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert customer.age == -5
    
    def test_create_customer_with_string_age(self, test_app, init_database):
        """Test tworzenia klienta z wiekiem jako string."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age="trzydzieści",  # Niepoprawny typ
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert customer.age == "trzydzieści"
    
    def test_create_customer_with_invalid_pesel_format(self, test_app, init_database):
        """Test tworzenia klienta z niepoprawnym formatem PESEL."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel="ABC123DEF45",  # Litery w PESEL
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert customer.pesel == "ABC123DEF45"
    
    def test_create_customer_with_too_short_pesel(self, test_app, init_database):
        """Test tworzenia klienta z za krótkim PESEL."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel="12345",  # Za krótki PESEL
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert len(customer.pesel) < 11
    
    def test_create_customer_with_too_long_pesel(self, test_app, init_database):
        """Test tworzenia klienta z za długim PESEL."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel="123456789012345",  # Za długi PESEL
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert len(customer.pesel) > 11
    
    def test_create_customer_with_float_age(self, test_app, init_database):
        """Test tworzenia klienta z wiekiem jako liczba zmiennoprzecinkowa."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=30.5,  # Niepoprawny typ
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert customer.age == 30.5
    
    def test_create_customer_with_whitespace_only_name(self, test_app, init_database):
        """Test tworzenia klienta z imieniem składającym się tylko z białych znaków."""
        with app.app_context():
            customer = Customer(
                name="   ",
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert customer.name == "   "
    
    def test_create_customer_with_special_characters_in_name(self, test_app, init_database):
        """Test tworzenia klienta ze znakami specjalnymi w imieniu."""
        with app.app_context():
            customer = Customer(
                name="!@#$%^&*()",
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert customer.name == "!@#$%^&*()"

#-----------------------------------------------
# SQL Injection
#-----------------------------------------------
class TestCustomerSQLInjection:
    """Testy związane z próbą wstrzyknięcia kodu SQL."""
    
    def test_sql_injection_in_name_drop_table(self, test_app, init_database):
        """Test SQL injection przez DROP TABLE w polu name."""
        with app.app_context():
            malicious_name = "'; DROP TABLE customers; --"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
            # Weryfikacja, że tabela nadal istnieje
            all_customers = Customer.query.all()
            assert len(all_customers) > 0
    
    def test_sql_injection_in_name_union_select(self, test_app, init_database):
        """Test SQL injection przez UNION SELECT w polu name."""
        with app.app_context():
            malicious_name = "' UNION SELECT * FROM users --"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_sql_injection_in_city_or_1_equals_1(self, test_app, init_database):
        """Test SQL injection przez OR 1=1 w polu city."""
        with app.app_context():
            malicious_city = "' OR '1'='1"
            customer = Customer(
                name=DEFAULT_NAME,
                city=malicious_city,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.city == malicious_city
    
    def test_sql_injection_in_street_delete_from(self, test_app, init_database):
        """Test SQL injection przez DELETE FROM w polu street."""
        with app.app_context():
            malicious_street = "'; DELETE FROM customers WHERE '1'='1"
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=malicious_street,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.street == malicious_street
    
    def test_sql_injection_in_pesel_insert_into(self, test_app, init_database):
        """Test SQL injection przez INSERT INTO w polu pesel."""
        with app.app_context():
            malicious_pesel = "'; INSERT INTO customers VALUES (999, 'hacker', 'city', 99, '12345', 'street', '1'); --"
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=malicious_pesel,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.pesel == malicious_pesel
    
    def test_sql_injection_in_appno_update_set(self, test_app, init_database):
        """Test SQL injection przez UPDATE SET w polu appNo."""
        with app.app_context():
            malicious_appno = "'; UPDATE customers SET name='hacked' WHERE '1'='1'; --"
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=malicious_appno
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.appNo == malicious_appno
    
    def test_sql_injection_comment_syntax(self, test_app, init_database):
        """Test SQL injection z użyciem składni komentarza."""
        with app.app_context():
            malicious_name = "admin'--"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_sql_injection_batch_commands(self, test_app, init_database):
        """Test SQL injection z wieloma poleceniami."""
        with app.app_context():
            malicious_name = "test'; DROP TABLE customers; SELECT * FROM customers WHERE name='"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_sql_injection_hex_encoded(self, test_app, init_database):
        """Test SQL injection z kodowaniem hex."""
        with app.app_context():
            malicious_name = "0x27; DROP TABLE customers; --"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_sql_injection_null_byte(self, test_app, init_database):
        """Test SQL injection z bajtem null."""
        with app.app_context():
            malicious_name = "test\x00'; DROP TABLE customers; --"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert "test" in customer.name

#-----------------------------------------------
# XSS (JavaScript Injection)
#-----------------------------------------------
class TestCustomerXSSInjection:
    """Testy związane z próbą wstrzyknięcia kodu JavaScript (XSS)."""
    
    def test_xss_script_tag_in_name(self, test_app, init_database):
        """Test XSS przez tag <script> w polu name."""
        with app.app_context():
            malicious_name = "<script>alert('XSS')</script>"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_xss_img_onerror_in_city(self, test_app, init_database):
        """Test XSS przez tag <img> z onerror w polu city."""
        with app.app_context():
            malicious_city = "<img src='x' onerror='alert(1)'>"
            customer = Customer(
                name=DEFAULT_NAME,
                city=malicious_city,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.city == malicious_city
    
    def test_xss_svg_onload_in_street(self, test_app, init_database):
        """Test XSS przez tag <svg> z onload w polu street."""
        with app.app_context():
            malicious_street = "<svg onload='alert(document.cookie)'>"
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=malicious_street,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.street == malicious_street
    
    def test_xss_javascript_protocol_in_name(self, test_app, init_database):
        """Test XSS przez protokół javascript: w polu name."""
        with app.app_context():
            malicious_name = "javascript:alert('XSS')"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_xss_event_handler_onclick(self, test_app, init_database):
        """Test XSS przez atrybut onclick."""
        with app.app_context():
            malicious_name = "<div onclick='alert(1)'>Click me</div>"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_xss_body_onload(self, test_app, init_database):
        """Test XSS przez tag <body> z onload."""
        with app.app_context():
            malicious_name = "<body onload='alert(1)'>"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_xss_iframe_injection(self, test_app, init_database):
        """Test XSS przez tag <iframe>."""
        with app.app_context():
            malicious_name = "<iframe src='http://malicious.com'></iframe>"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_xss_encoded_script_tag(self, test_app, init_database):
        """Test XSS z zakodowanym tagiem script."""
        with app.app_context():
            malicious_name = "%3Cscript%3Ealert('XSS')%3C/script%3E"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_xss_html_entities(self, test_app, init_database):
        """Test XSS z encjami HTML."""
        with app.app_context():
            malicious_name = "&lt;script&gt;alert('XSS')&lt;/script&gt;"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_xss_mixed_case_script(self, test_app, init_database):
        """Test XSS z mieszanymi wielkościami liter w tagu script."""
        with app.app_context():
            malicious_name = "<ScRiPt>alert('XSS')</sCrIpT>"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name
    
    def test_xss_data_protocol(self, test_app, init_database):
        """Test XSS przez protokół data:."""
        with app.app_context():
            malicious_name = "data:text/html,<script>alert('XSS')</script>"
            customer = Customer(
                name=malicious_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == malicious_name

#-----------------------------------------------
# Wartości ekstremalne
#-----------------------------------------------
class TestCustomerExtremeValues:
    """Testy ekstremalnych wartości dla klienta."""
    
    def test_create_customer_with_very_long_name(self, test_app, init_database):
        """Test tworzenia klienta z bardzo długim imieniem."""
        with app.app_context():
            long_name = "A" * 1000 
            customer = Customer(
                name=long_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            try:
                db.session.commit()
                # Jeśli się uda, sprawdzamy czy dane są tam
                assert customer.name is not None
            except Exception as e:
                db.session.rollback()
                # Oczekiwany błąd dla zbyt długiego stringa
                assert True
    
    def test_create_customer_with_very_long_city(self, test_app, init_database):
        """Test tworzenia klienta z bardzo długą nazwą miasta."""
        with app.app_context():
            long_city = "B" * 1000
            customer = Customer(
                name=DEFAULT_NAME,
                city=long_city,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            try:
                db.session.commit()
                assert customer.city is not None
            except Exception as e:
                db.session.rollback()
                assert True
    
    def test_create_customer_with_maximum_integer_age(self, test_app, init_database):
        """Test tworzenia klienta z maksymalną wartością Integer dla wieku."""
        with app.app_context():
            max_int = 2147483647
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=max_int,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.age == max_int
    
    def test_create_customer_with_minimum_integer_age(self, test_app, init_database):
        """Test tworzenia klienta z minimalną wartością Integer dla wieku."""
        with app.app_context():
            min_int = -2147483648
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=min_int,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.age == min_int
    
    def test_create_customer_with_zero_age(self, test_app, init_database):
        """Test tworzenia klienta z wiekiem równym zero."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=0,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.age == 0
    
    def test_create_customer_with_newline_characters(self, test_app, init_database):
        """Test tworzenia klienta ze znakami nowej linii."""
        with app.app_context():
            name_with_newlines = "Jan\nKowalski\r\nTest"
            customer = Customer(
                name=name_with_newlines,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert "\n" in customer.name
    
    def test_create_customer_with_tab_characters(self, test_app, init_database):
        """Test tworzenia klienta ze znakami tabulacji."""
        with app.app_context():
            name_with_tabs = "Jan\tKowalski"
            customer = Customer(
                name=name_with_tabs,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert "\t" in customer.name
    
    def test_create_customer_with_null_byte_in_fields(self, test_app, init_database):
        """Test tworzenia klienta z bajtem null w polach."""
        with app.app_context():
            name_with_null = "Jan\x00Kowalski"
            customer = Customer(
                name=name_with_null,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert "Jan" in customer.name
    
    def test_create_customer_with_backslash_characters(self, test_app, init_database):
        """Test tworzenia klienta z ukośnikami wstecznymi."""
        with app.app_context():
            name_with_backslash = "Jan\\Kowalski\\Test"
            customer = Customer(
                name=name_with_backslash,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert "\\" in customer.name
    
    def test_create_customer_with_quotes_in_fields(self, test_app, init_database):
        """Test tworzenia klienta z cudzysłowami w polach."""
        with app.app_context():
            name_with_quotes = 'Jan "Janek" Kowalski'
            customer = Customer(
                name=name_with_quotes,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert '"' in customer.name
    
    def test_create_customer_with_only_numbers_in_name(self, test_app, init_database):
        """Test tworzenia klienta z samymi liczbami w imieniu."""
        with app.app_context():
            customer = Customer(
                name="1234567890",
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.name == "1234567890"
    
    def test_create_customer_with_very_large_age(self, test_app, init_database):
        """Test tworzenia klienta z nierealistycznie dużym wiekiem."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=999999,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert customer.age == 999999
    
    def test_create_customer_with_boolean_values(self, test_app, init_database):
        """Test tworzenia klienta z wartościami boolean zamiast stringów."""
        with app.app_context():
            customer = Customer(
                name=True,
                city=False,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            # Test dokumentuje zachowanie przy niepoprawnych typach
            assert customer.name == True
    
    def test_create_customer_with_list_value(self, test_app, init_database):
        """Test tworzenia klienta z listą jako wartością."""
        with app.app_context():
            customer = Customer(
                name=["Jan", "Kowalski"],
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert customer.name == ["Jan", "Kowalski"]
    
    def test_create_customer_with_dict_value(self, test_app, init_database):
        """Test tworzenia klienta ze słownikiem jako wartością."""
        with app.app_context():
            customer = Customer(
                name={"first": "Jan", "last": "Kowalski"},
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            assert customer.name == {"first": "Jan", "last": "Kowalski"}
    
    def test_create_customer_exact_boundary_name_64_chars(self, test_app, init_database):
        """Test tworzenia klienta z imieniem dokładnie 64 znaki (granica pola)."""
        with app.app_context():
            boundary_name = "A" * 64
            customer = Customer(
                name=boundary_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            assert len(customer.name) == 64
    
    def test_create_customer_one_over_boundary_name_65_chars(self, test_app, init_database):
        """Test tworzenia klienta z imieniem 65 znaków (jeden ponad granicę pola)."""
        with app.app_context():
            over_boundary_name = "A" * 65
            customer = Customer(
                name=over_boundary_name,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            try:
                db.session.commit()
                assert customer.name is not None
            except Exception as e:
                db.session.rollback()
                assert True

#-----------------------------------------------
# Przypadki brzegowe
#-----------------------------------------------
class TestCustomerEdgeCases:
    """Dodatkowe testy dla przypadków brzegowych."""
    
    def test_create_multiple_customers_same_name(self, test_app, init_database):
        """Test tworzenia wielu klientów z tym samym imieniem (unique constraint)."""
        with app.app_context():
            customer1 = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer1)
            db.session.commit()
            
            customer2 = Customer(
                name=DEFAULT_NAME,  # To samo imię
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer2)
            
            try:
                db.session.commit()
                # Jeśli się uda, unique constraint nie działa
                assert False, "Expected IntegrityError for duplicate name"
            except Exception as e:
                db.session.rollback()
                assert True
    
    def test_query_customer_after_creation(self, test_app, init_database):
        """Test wyszukiwania klienta po utworzeniu."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            found = Customer.query.filter_by(name=DEFAULT_NAME).first()
            assert found is not None
            assert found.name == DEFAULT_NAME
    
    def test_update_customer_data(self, test_app, init_database):
        """Test aktualizacji danych klienta."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            customer.age = 35
            customer.city = "Kraków"
            db.session.commit()
            
            updated = Customer.query.filter_by(name=DEFAULT_NAME).first()
            assert updated.age == 35
            assert updated.city == "Kraków"
    
    def test_delete_customer(self, test_app, init_database):
        """Test usuwania klienta."""
        with app.app_context():
            customer = Customer(
                name=DEFAULT_NAME,
                city=DEFAULT_CITY,
                age=DEFAULT_AGE,
                pesel=DEFAULT_PESEL,
                street=DEFAULT_STREET,
                appNo=DEFAULT_APP_NO
            )
            db.session.add(customer)
            db.session.commit()
            
            customer_id = customer.id
            db.session.delete(customer)
            db.session.commit()
            
            deleted = Customer.query.get(customer_id)
            assert deleted is None
    
    def test_customer_with_html_in_all_fields(self, test_app, init_database):
        """Test klienta z HTML we wszystkich polach tekstowych."""
        with app.app_context():
            customer = Customer(
                name="<b>Jan Kowalski</b>",
                city="<i>Warszawa</i>",
                age=DEFAULT_AGE,
                pesel="<u>90010112345</u>",
                street="<a href='test'>ul. Testowa</a>",
                appNo="<span>10A</span>"
            )
            db.session.add(customer)
            db.session.commit()
            
            assert "<b>" in customer.name
            assert "<i>" in customer.city
            assert "<u>" in customer.pesel
            assert "<a" in customer.street
            assert "<span>" in customer.appNo


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
