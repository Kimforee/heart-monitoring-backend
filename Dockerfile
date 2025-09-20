# Dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

# system deps (for psycopg2)
RUN apt-get update && apt-get install -y build-essential libpq-dev --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# copy requirements early to leverage cache
COPY requirements.txt /app/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

# copy project
COPY . /app/

# copy entrypoint and make executable
COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENV DJANGO_SETTINGS_MODULE=heart_monitoring.settings_prod

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["gunicorn", "heart_monitoring.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3"]
