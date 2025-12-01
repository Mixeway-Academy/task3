# Zad 1
Testy dodano z wykorzystaniem biblioteki `pytest`.

Przykładowy test sprawdzający obsługe za długiego pesela:
``` python
def test_customer_invalid_pesel_too_long():
    with pytest.raises(ValueError, match="Invalid pesel"):
        Customer(
            name="Marek Test",
            city="Poznań",
            age=25,
            pesel="123456789012345",
  [          street="ul. Łąkowa 4",
            appNo="D444"
        )
```

Do pliku `requriments.txt` dodano
```python
pytest==8.2.2
```

A w dockerfile dodano:

``` 

ENV PYTHONPATH="/app"
# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

#uruchomienie testow
RUN pytest -vv --disable-warnings --maxfail=1
```

Otrzymany output:

![zdjećie builda](https://github.com/KarolZebala/kz-tbo-task3/blob/main/zad1-b%C5%82edy.png?raw=true)

# Zad 2
## Opis ataku
Zalogowanie się z wykorzystaniem tokenu JWT Boba:
![token boba](https://github.com/KarolZebala/kz-tbo-task3/blob/main/bob-token.png?raw=true)
Token Boba:

``` 
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50IjoiQm9iIiwicm9sZSI6IlVzZXIiLCJpYXQiOjE3NjQ0MDYxMDMsImF1ZCI6Imh0dHBzOi8vMTI3LjAuMC4xL2p3dC9ub25lIn0.xanMFAYuWRhqKRZ2KRRMoioSyEGoCTkYpvzgilEapTQ
```

Zmodyfikowany token

```
eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJhY2NvdW50IjoiQm9iIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNzY0NDA2MTAzLCJhdWQiOiJodHRwczovLzEyNy4wLjAuMS9qd3Qvbm9uZSJ9.
```

Odpowiedź z endpointu:
![token-atak](https://github.com/KarolZebala/kz-tbo-task3/blob/main/bob-atak-token.png?raw=true)

W ataku zmieniono Header tokana tak, ze ustawiono pole `"alg"` na `"none"`.
Następnie zmieniono w Payload role Boba na `admin`.
W kolejnym kroku trzeba usunąć sygnaturę pozostawiając kropkę na końcu

## Poprawa podatności
W ramach naprawy podatności trzeba zmodyfikować funkcję `JWT.verify` tak, zeby nie akceptowała algorytmu `none`. 

![zdj po poprawie](https://github.com/KarolZebala/kz-tbo-task3/blob/main/po-poprawi.png?raw=true)

