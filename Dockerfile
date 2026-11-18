FROM python:3.13-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    SIMULATOR_DB_PATH=/data/simulator.db

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
RUN mkdir -p /data \
    && addgroup --system app \
    && adduser --system --ingroup app app \
    && chown -R app:app /app /data

USER app
EXPOSE 8000

CMD ["sh", "-c", "python -c 'from backend.database import init_db; init_db()' && exec gunicorn --workers 2 --threads 4 --timeout 120 --bind 0.0.0.0:${PORT} backend.app:app"]
