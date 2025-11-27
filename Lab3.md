# Zadanie 1
Przy pisaniu testów skupiłem się na obiekcie `Book` i głównie logice tworzenia tego obiektu, walidacji danych jakie trafiają do konstruktora. W związku z tym zostały zaimplementowane testy, gdzie wprowadzane są:
1. poprawne dane,
2. niepoprawne dane - niepoprawna nazwa autora,
3. niepoprawne dane - data wydania książki w przyszłości,
4. niepoprawne dane (SQL Injection) - niepoprawne znaki w nazwie autora, w tym polecenia sql,
5. niepoprawne dane (XSS Injection) - skrypt JS w polu nazwa książki,
6. test ekstremalny - bardzo długa nazwa książki (10 000 znaków).

Ze względu na brak implementacji walidacji testowanego konstruktora, tylko i wyłącznie test nr 1 powinien przejść a reszta powinna zfailować. 

W ramach zadania dokonałem również zmian w pliku dockerfile, dzięki czemu jeżeli testy nie przejdą to obraz się nie zbuduje. To co widzimy podczas buildowania obrazu:
## Docker Build Log

```
[+] Building 12.5s (9/9) FINISHED                                                                                                                                                                           docker:default
 => [internal] load build definition from Dockerfile                                                                                                                                                                  0.0s
 => => transferring dockerfile: 637B                                                                                                                                                                                  0.0s 
 => [internal] load metadata for docker.io/library/python:3.9-slim                                                                                                                                                    0.5s 
 => [internal] load .dockerignore                                                                                                                                                                                     0.0s
 => => transferring context: 2B                                                                                                                                                                                       0.0s 
 => [1/5] FROM docker.io/library/python:3.9-slim@sha256:2d97f6910b16bd338d3060f261f53f144965f755599aab1acda1e13cf1731b1b                                                                                              0.0s 
 => [internal] load build context                                                                                                                                                                                     0.0s 
 => => transferring context: 2.49kB                                                                                                                                                                                   0.0s 
 => CACHED [2/5] WORKDIR /app                                                                                                                                                                                         0.0s 
 => [3/5] COPY . .                                                                                                                                                                                                    0.0s 
 => [4/5] RUN pip install --no-cache-dir -r requirements.txt                                                                                                                                                         10.7s 
 => ERROR [5/5] RUN python -m unittest discover -s project/tests -t project                                                                                                                                           1.1s
------
 > [5/5] RUN python -m unittest discover -s project/tests -t project:
1.030 .FFFFF
1.034 ======================================================================
1.034 FAIL: test_extreme_string_length (tests.test_book_model.BookModelTestCase)
1.034 Sprawdza czy konstruktor odrzuca zbyt długą nazwę
1.034 ----------------------------------------------------------------------
1.034 Traceback (most recent call last):
1.034   File "/app/project/tests/test_book_model.py", line 92, in test_extreme_string_length
1.034     Book(name=long_name, author="Author", year_published=2020, book_type="Type")
1.034 AssertionError: ValueError not raised
1.034
1.034 ======================================================================
1.034 FAIL: test_reject_book_author (tests.test_book_model.BookModelTestCase)
1.034 Test powinien rzucić wyjątek przy próbie utworzenia książki z niepoprawnymi znakami w nazwie autora
1.034 ----------------------------------------------------------------------
1.034 Traceback (most recent call last):
1.034   File "/app/project/tests/test_book_model.py", line 36, in test_reject_book_author
1.034     Book(
1.034 AssertionError: ValueError not raised
1.034
1.034 ======================================================================
1.035 FAIL: test_reject_future_year (tests.test_book_model.BookModelTestCase)
1.035 Test powinien rzucić wyjątek przy próbie utworzenia książki z datą z przyszłości
1.035 ----------------------------------------------------------------------
1.035 Traceback (most recent call last):
1.035   File "/app/project/tests/test_book_model.py", line 51, in test_reject_future_year
1.035     Book(
1.035 AssertionError: ValueError not raised
1.035
1.035 ======================================================================
1.035 FAIL: test_sql_injection_sanitization (tests.test_book_model.BookModelTestCase)
1.035 Sprawdza czy konstruktor czyści nazwę z potencjalnego kodu SQL i niepoprawnych znaków
1.035 ----------------------------------------------------------------------
1.035 Traceback (most recent call last):
1.035   File "/app/project/tests/test_book_model.py", line 68, in test_sql_injection_sanitization
1.035     self.assertNotIn(";", book.name, "Średnik powinien zostać usunięty")
1.035   File "/app/project/tests/test_book_model.py", line 68, in test_sql_injection_sanitization
1.035     self.assertNotIn(";", book.name, "Średnik powinien zostać usunięty")
1.035     self.assertNotIn(";", book.name, "Średnik powinien zostać usunięty")
1.035 AssertionError: ';' unexpectedly found in "Wiedźmin'; DROP TABLE books; --" : Średnik powinien zostać usunięty
1.035
1.035 ======================================================================
1.035 FAIL: test_xss_injection_in_author (tests.test_book_model.BookModelTestCase)
1.035 Sprawdza czy konstruktor czyści autora z kodu JavaScript
1.035 ----------------------------------------------------------------------
1.035 Traceback (most recent call last):
1.035   File "/app/project/tests/test_book_model.py", line 81, in test_xss_injection_in_author
1.035     self.assertNotIn("<script>", book.author, "Tag <script> powinien zostać usunięty")
1.035 AssertionError: '<script>' unexpectedly found in "<script>alert('XSS')</script>John Doe" : Tag <script> powinien zostać usunięty
1.035
1.035 ----------------------------------------------------------------------
1.035 Ran 6 tests in 0.006s
1.035
1.036 FAILED (failures=5)
------
Dockerfile:13
--------------------
  11 |     # Instalujemy zależności
  12 |     RUN pip install --no-cache-dir -r requirements.txt
  13 | >>> RUN python -m unittest discover -s project/tests -t project
  14 |
  15 |     # Ustawiamy zmienną środowiskową, aby Flask wiedział, jak uruchomić aplikację
--------------------
ERROR: failed to solve: process "/bin/sh -c python -m unittest discover -s project/tests -t project" did not complete successfully: exit code: 1

View build details: docker-desktop://dashboard/build/default/default/r5shhceuyhr964dsrt9fnhoy9
```

# Zadanie 2