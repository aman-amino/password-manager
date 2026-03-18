FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# System deps commonly needed for psycopg2 and builds
RUN apt-get update && apt-get install -y --no-install-recommends     gcc     libpq-dev     postgresql-client   && rm -rf /var/lib/apt/lists/*

# Create a non-privileged user
RUN groupadd -r vault && useradd -r -g vault -d /app -s /sbin/nologin vault &&     chown -R vault:vault /app

COPY --chown=vault:vault requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY --chown=vault:vault . /app/

# Switch to the non-privileged user
USER vault

EXPOSE 8000
