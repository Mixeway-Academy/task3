
# Zadanie 1

## Przygotowanie testów jednostkowych

Do realizacji zadania wybrano aplikację w języku Python (`Flask_Book_Library`) oraz klasę modelu `Book` z pliku `project/books/models.py`.

Dla wybranego obiektu przygotowano rozszerzony zestaw testów jednostkowych z wykorzystaniem biblioteki `pytest` (plik `project/tests/test_book.py`). Zestaw testów został podzielony na następujące grupy:

* **Poprawne dane wejściowe**: weryfikacja poprawnego utworzenia instancji obiektu `Book` z prawidłowymi wartościami atrybutów oraz sprawdzenie ustawienia domyślnego statusu (`available`).
* **Niepoprawne dane wejściowe**: przekazywanie wartości pustych, ciągów złożonych z samych białych znaków, wartości `None`, nieobsługiwanych typów książek oraz niepoprawnych typów i zakresów dla roku wydania (wartości nieliczbowe, ujemne czy z dalekiej przyszłości).
* **Próby wstrzyknięcia kodu SQL (SQL Injection)**: testowanie zachowania pól tekstowych przy próbie wstrzyknięcia popularnych payloadów (np. `' OR 1=1 --`, zapytania z `UNION SELECT`, podzapytania ze `sleep`).
* **Próby wstrzyknięcia JavaScript (XSS)**: przekazywanie ładunków skryptowych w polach tekstowych (np. `<script>alert(1)</script>`, `"-prompt(8)-"`, wektory oparte o zdarzenia tagów `<img>`).
* **Wartości ekstremalne i warunki brzegowe**: przekazywanie bardzo długich ciągów znaków (przekraczających zdefiniowane w modelu limity kolumn `String(64)` i `String(20)`, aż do 1 000 000 znaków).

## Uruchomienie testów w trakcie docker build

Zmodyfikowano plik `Dockerfile`, aby testy były uruchamiane na etapie budowania obrazu, bezpośrednio po instalacji zależności z `requirements.txt`:

```dockerfile
# Uruchomienie testów jednostkowych przed finalizacją budowy obrazu
RUN python -m pytest -v 

```

Użycie `python -m pytest` zapobiega problemom ze ścieżkami środowiskowymi, a flaga `--tb=line` zapewnia czytelny, zwięzły log wyników w konsoli Dockera.

## Wyniki wykonania

Podczas uruchomienia komendy `docker build`:

* Testy dla poprawnych danych zakończyły się sukcesem (`PASSED`).
* Testy niepoprawnych danych, payloadów SQLi/XSS oraz wartości ekstremalnych zakończyły się niepowodzeniem (`FAILED`), ponieważ klasa `Book` nie posiada wbudowanych mechanizmów walidacji i akceptuje złośliwe lub uszkodzone wartości.


Zgodnie z założeniem zadania błędy w testach zwróciły kod wyjścia różny od zera, co natychmiast przerwało operację `docker build` i zapobiegło utworzeniu podatnego obrazu kontenera.