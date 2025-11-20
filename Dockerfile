FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Dependencias de sistema necesarias (libpq para psycopg/binaries de wheels si se usa Postgres)
RUN apt-get update && apt-get install -y build-essential libpq-dev gcc --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copiar el código
COPY . .

# Intentar collectstatic en build (no bloquear si falla por falta de variables en build)
RUN python manage.py collectstatic --noinput || true

ENV PORT 8080

CMD ["gunicorn", "obstetricia.wsgi", "--bind", "0.0.0.0:8080", "--workers", "3"]
