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

# Run the unit tests before the image is finished.
# pytest exits with a non-zero code when any test fails, which makes `docker build` fail.
RUN pip install --no-cache-dir -r requirements-test.txt \
    && python -m pytest tests -v -p no:cacheprovider

# Ustawiamy zmienną środowiskową, aby Flask wiedział, jak uruchomić aplikację
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port the app runs on
EXPOSE 5000

# Uruchamiamy aplikację
CMD ["flask", "run"]