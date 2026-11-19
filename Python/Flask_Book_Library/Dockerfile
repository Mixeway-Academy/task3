FROM python:3.9-slim AS base
WORKDIR /app

ENV FLASK_ENV=development
ENV PASSWORD=1qaz@WSX

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

FROM base AS test

COPY requirements-test.txt .
RUN pip install --no-cache-dir -r requirements-test.txt

COPY . .

RUN python -m pytest -v && touch /tmp/tests-passed

FROM base AS final

# dodanie zaleznosci, zeby nie pomijac testow
COPY --from=test /tmp/tests-passed /tmp/tests-passed

# Kopiujemy tylko kod aplikacji
COPY app.py .
COPY project/ ./project/

# Ustawiamy zmienną środowiskową, aby Flask wiedział, jak uruchomić aplikację
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Expose the port the app runs on
EXPOSE 5000

# Uruchamiamy aplikację
CMD ["flask", "run"]
