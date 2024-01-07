# Używamy oficjalnego obrazu Pythona
FROM python:3.9-slim as base

# Ustawiamy katalog roboczy w kontenerze
WORKDIR /app

# Kopiujemy pliki projektu do kontenera
COPY . .
ENV FLASK_ENV=development
ENV PASSWORD=1qaz@WSX
# Instalujemy zależności
RUN pip install --no-cache-dir -r requirements.txt

# Ustawiamy zmienną środowiskową, aby Flask wiedział, jak uruchomić aplikację
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Perform tests
FROM base as test
COPY tests tests/
RUN ["coverage", "run", "--source=.", "-m", "pytest", "tests/test_book_models_extreme.py", "tests/test_book_models_inject.py", "tests/test_book_models_invalid.py", "tests/test_book_models_valid.py"]


FROM base as prod
# Expose the port the app runs on
EXPOSE 5000

# Uruchamiamy aplikację
CMD ["flask", "run"]