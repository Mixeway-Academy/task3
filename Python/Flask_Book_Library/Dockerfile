# Używamy oficjalnego obrazu Pythona
FROM python:3.9-slim

# Ustawiamy katalog roboczy w kontenerze
WORKDIR /app

# Kopiujemy pliki projektu do kontenera
COPY . .
ENV FLASK_ENV=development
ENV PASSWORD=1qaz@WSX
# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Testy jednostkowe — build przerywa się, jeśli ktorykolwiek test nie przejdzie
RUN pip install --no-cache-dir pytest
RUN python -m pytest project/books/test_book.py -v

# Ustawiamy zmienną środowiskową, aby Flask wiedział, jak uruchomić aplikację
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port the app runs on
EXPOSE 5000

# Uruchamiamy aplikację
CMD ["flask", "run"]
