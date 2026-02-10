# Backend (Flask) Dockerfile (deployable to Cloud Run / any container platform)
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# System deps (pg_isready for optional DB wait)
RUN apt-get update && apt-get install -y --no-install-recommends \
    postgresql-client \
    build-essential \
    libpq-dev \
  && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN adduser --disabled-password --gecos "" appuser \
  && chown -R appuser:appuser /app
USER appuser

ENV FLASK_ENV=production \
    FLASK_APP=wsgi:app

EXPOSE 8080

ENTRYPOINT ["./docker/entrypoint.sh"]
CMD ["sh", "-c", "gunicorn -b 0.0.0.0:${PORT:-8080} --workers 2 --threads 4 --timeout 60 wsgi:app"]
