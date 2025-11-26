import pytest
from project.customers.models import Customer

class Test_Customer_Model:

    name = "Jan"
    city = "Londyn"
    age = 19
    street = "Sikorskiego"
    appNo = "20A"

    def test_correctInput(self):
        pesel="12345678911"
        customer=Customer(self.name,self.city,19,pesel,self.street,self.appNo)
        assert customer.name==self.name
        assert customer.city == self.city
        assert customer.age == self.age
        assert customer.street == self.street
        assert customer.appNo == self.appNo
        assert customer.pesel == pesel

    def test_incorrectInput(self):
        incorrect_inputs = (123456789,123,"gggg","","\n",'c',"abcdttttttt",False,True,None)
        for incorrect_input in incorrect_inputs:
            customer=Customer(name=self.name,city=self.city,age=self.age,pesel=incorrect_input,street=self.street,appNo=self.appNo)
            assert isinstance(customer, Customer)
            assert customer.pesel == incorrect_input
    
    def test_extremeInput(self):
        extreme_inputs = ("abc"*1000,"abc"*10000,"abc"*100000,"abc"*1000000,"abc"*10000000)
        for extreme_input in extreme_inputs:
            customer=Customer(name=self.name,city=self.city,age=self.age,pesel=extreme_input,street=self.street,appNo=self.appNo)
            assert customer.pesel == extreme_input

    @pytest.mark.parametrize("sql_input", [
        "'; DROP TABLE customers; --",
        "Robert'); DELETE FROM customers WHERE 1=1; --"
    ])
    def test_sql_injection(self, sql_input):
        customer = Customer(self.name, self.city, self.age, sql_input, self.street, self.appNo)
        assert customer.pesel == sql_input

   
    @pytest.mark.parametrize("js_input", [
        "<script>alert('XSS')</script>",
        "javascript:alert('XSS')"
    ])
    def test_javascript_injection(self, js_input):
        customer = Customer(self.name, self.city, self.age, js_input, self.street, self.appNo)
        assert customer.pesel == js_input
        


