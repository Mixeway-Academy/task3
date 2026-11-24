# Raport z realizacji zadań - Testy jednostkowe (Python) oraz JWT

---

## Zadanie 1 - Rozszerzony zestaw testów jednostkowych

### Wybrana klasa

Testy przygotowano dla klasy **`Book`** z pliku
`Python/Flask_Book_Library/project/books/models.py`.

### Lokalizacja testów

| Plik | Zawartość |
|------|-----------|
| `project/.../tests/conftest.py` | konfiguracja pytest + fixture `session` (czysta baza dla każdego testu) |
| `project/.../tests/test_book_model.py` | właściwy scenariusz testów |

### Zakres testów (4 wymagane kategorie)

1. **Testy poprawnych danych** (`TestValidData`) - poprawne ustawienie atrybutów   w konstruktorze, domyślny status `available`, zapis i odczyt z bazy,   akceptacja wszystkich dozwolonych typów książki.
2. **Testy niepoprawnych danych** (`TestInvalidData`) - nazwa dłuższa niż `String(64)`, `name=None`, rok jako tekst, rok ujemny, niedozwolony `book_type`, zduplikat nazwy (ograniczenie `unique`).
3. **Testy wstrzyknięcia SQL i JavaScript** (`TestSqlInjection`, `TestJavaScriptInjection`) - ładunki `'; DROP TABLE books; --`, `' OR '1'='1`, `<script>alert('xss')</script>`, `<img src=x onerror=alert(1)>`.
4. **Testy ekstremalne** (`TestExtreme`) - pusta nazwa, nazwa 100 000 znaków, rok `10^18`, rok `-10^9`, znaki Unicode/emoji.

### Wynik uruchomienia i jego interpretacja

```
 > [6/6] RUN python -m pytest tests/ -v:
1.021 ============================= test session starts ==============================
1.021 platform linux -- Python 3.9.25, pytest-8.4.2, pluggy-1.6.0 -- /usr/local/bin/python
1.021 cachedir: .pytest_cache
1.021 rootdir: /app
1.021 collecting ... collected 21 items
1.037
1.037 tests/test_book_model.py::TestValidData::test_attributes_set_on_construction PASSED [  4%]
1.040 tests/test_book_model.py::TestValidData::test_default_status_is_available PASSED [  9%]
1.040 tests/test_book_model.py::TestValidData::test_explicit_status_is_kept PASSED [ 14%]
1.041 tests/test_book_model.py::TestValidData::test_persisted_and_queried_back PASSED [ 19%]
1.363 tests/test_book_model.py::TestValidData::test_all_valid_book_types_accepted PASSED [ 23%]
1.684 tests/test_book_model.py::TestInvalidData::test_name_longer_than_column_limit_is_rejected FAILED [ 28%]
2.001 tests/test_book_model.py::TestInvalidData::test_name_cannot_be_none FAILED [ 33%]
2.266 tests/test_book_model.py::TestInvalidData::test_year_published_must_be_integer FAILED [ 38%]
2.537 tests/test_book_model.py::TestInvalidData::test_year_published_must_not_be_negative FAILED [ 42%]
2.806 tests/test_book_model.py::TestInvalidData::test_book_type_must_be_a_valid_choice FAILED [ 47%]
3.075 tests/test_book_model.py::TestInvalidData::test_duplicate_name_is_rejected PASSED [ 52%]
3.345 tests/test_book_model.py::TestSqlInjection::test_sql_payload_in_name_is_stored_as_literal_data PASSED [ 57%]
3.612 tests/test_book_model.py::TestSqlInjection::test_table_survives_sql_payload PASSED [ 61%]
3.914 tests/test_book_model.py::TestSqlInjection::test_filter_is_not_vulnerable_to_boolean_injection PASSED [ 66%]
4.186 tests/test_book_model.py::TestJavaScriptInjection::test_script_payload_is_not_stored_verbatim FAILED [ 71%]
4.465 tests/test_book_model.py::TestJavaScriptInjection::test_html_event_handler_payload_is_neutralised FAILED [ 76%]
4.738 tests/test_book_model.py::TestExtreme::test_empty_name_is_rejected FAILED [ 80%]
5.015 tests/test_book_model.py::TestExtreme::test_extremely_long_name FAILED   [ 85%]
5.296 tests/test_book_model.py::TestExtreme::test_extremely_large_year FAILED  [ 90%]
5.585 tests/test_book_model.py::TestExtreme::test_extremely_negative_year FAILED [ 95%]
5.874 tests/test_book_model.py::TestExtreme::test_unicode_and_emoji_name_roundtrip PASSED [100%]

[...]

6.144 =========================== short test summary info ============================
6.144 FAILED tests/test_book_model.py::TestInvalidData::test_name_longer_than_column_limit_is_rejected
6.144 FAILED tests/test_book_model.py::TestInvalidData::test_name_cannot_be_none - ...
6.144 FAILED tests/test_book_model.py::TestInvalidData::test_year_published_must_be_integer
6.144 FAILED tests/test_book_model.py::TestInvalidData::test_year_published_must_not_be_negative
6.144 FAILED tests/test_book_model.py::TestInvalidData::test_book_type_must_be_a_valid_choice
6.144 FAILED tests/test_book_model.py::TestJavaScriptInjection::test_script_payload_is_not_stored_verbatim
6.144 FAILED tests/test_book_model.py::TestJavaScriptInjection::test_html_event_handler_payload_is_neutralised
6.144 FAILED tests/test_book_model.py::TestExtreme::test_empty_name_is_rejected - A...
6.144 FAILED tests/test_book_model.py::TestExtreme::test_extremely_long_name - Fail...
6.144 FAILED tests/test_book_model.py::TestExtreme::test_extremely_large_year - ass...
6.144 FAILED tests/test_book_model.py::TestExtreme::test_extremely_negative_year - ...
6.271 ======================== 11 failed, 10 passed in 5.12s =========================
```

Wynik jest zgodny z oczekiwaniami. Klasa `Book` nie wykonuje żadnej walidacji danych, dlatego testy sprawdzające poprawne/bezpieczne zachowanie są celowo „failed” - dokumentują brak zabezpieczeń w modelu.

| Kategoria | Wynik | Wniosek |
|-----------|-------|---------|
| Poprawne dane | przechodzą | model poprawnie przechowuje poprawne dane |
| `unique` (duplikat nazwy) | przechodzi | ograniczenie `unique=True` działa |
| Wstrzyknięcie SQL | przechodzą | ORM parametryzuje zapytania - baza odporna na SQLi |
| Niepoprawne dane (długość, typ, zakres, `None`) | nie przechodzą | brak walidacji - obiekt powstaje mimo błędnych danych |
| Wstrzyknięcie JavaScript (XSS) | nie przechodzą | model nie sanityzuje treści `<script>` / `onerror=` |
| Wartości ekstremalne | nie przechodzą | brak ograniczeń długości i zakresu |

### Modyfikacja pliku `Dockerfile`

Do `Dockerfile` dodano uruchomienie testów na etapie budowania obrazu:

```dockerfile
RUN pip install --no-cache-dir pytest
RUN python -m pytest tests/ -v
```

Mechanizm: polecenie `RUN` przerywa budowę, gdy proces zwróci kod wyjścia`!= 0`. `pytest` przy choćby jednym nieudanym teście zwraca kod `1`, więc`docker build` kończy się **niepowodzeniem** i obraz nie zostaje utworzony -dokładnie tak, jak wymaga polecenie (pkt 4).


---

## Zadanie 2 - JWT: wykorzystanie podatności i poprawka

### Zidentyfikowana podatność

Podatność typu **`alg: none`** znajduje się w metodzie obsługującej endpoint`POST /jwt/none` w pliku`JWT/jwt-signature-apis-challenges/app.js` (metoda rozpoczyna się w linii 22).

Wywołanie weryfikujące token dopuszczało algorytm `none`:

```js
// PRZED (podatne):
JWT.verify(jwt_token, secret_key, { algorithms: ['none', 'HS256'], ... })
```

Dopuszczenie `none` powoduje, że serwer akceptuje token **bez podpisu**. Atakujący może dowolnie zmienić ładunek (`payload`), bo nie jest wymagana znajomość klucza - dla `alg:none` `secret_key` jest pustym ciągiem.

### Przebieg ataku

1. `none-obtain-token` → otrzymanie prawidłowego tokena HS256 dla użytkownika `Bob`.
2. Token JWT składa się z trzech części rozdzielonych `.` kodowanych base64url (`nagłówek.ładunek.podpis`) - każdą można edytować niezależnie.
3. W **nagłówku** zmieniamy `"alg": "HS256"` → `"alg": "none"`.
4. W **ładunku** zmieniamy `"account": "Bob"` → `"account": "administrator"`.
5. Usuwamy **podpis**, zostawiając jednak końcową kropkę `.`.
6. Tak spreparowany token wysyłamy w `none-send-token` (parametr `jwt_token` w zakładce `Body`).


### Zrzuty ekranu z Postmana


**1. Request `none-obtain-token` - token wygenerowany dla użytkownika `Bob`**
<img width="1774" height="582" alt="attack1" src="https://github.com/user-attachments/assets/2ca37fa7-0403-4037-b3af-f6ed5f0fa5d6" />

**2. Weryfikacja otrzymanego tokenu**
<img width="1332" height="845" alt="attack2" src="https://github.com/user-attachments/assets/c6fafbae-3172-4618-becf-2d22ae19d9ac" />

**3. Modyfikacja tokenu - modyfikacja parametrów `alg` oraz `account`**
<img width="1332" height="689" alt="attack3" src="https://github.com/user-attachments/assets/766c39d4-0fac-46eb-baee-351c93fa279d" />

**4. Request `none-send-token` - wysłanie spreparowanego tokena**
<img width="1778" height="792" alt="attack4" src="https://github.com/user-attachments/assets/cdd1e541-967a-4b8a-8b41-81c9a5e00bc6" />





### Poprawka

Zgodnie ze wskazówką (usunięcie dosłownie kilku symboli) z listy dozwolonychalgorytmów usunięto `'none'`:

```js
// PO (poprawione):
JWT.verify(jwt_token, secret_key, { algorithms: ['HS256'], ... })
```

Po tej zmianie token z nagłówkiem `alg:none` jest odrzucany z błędem `JsonWebTokenError: invalid algorithm`, ponieważ `none` nie jest już dozwolonym algorytmem weryfikacji.
