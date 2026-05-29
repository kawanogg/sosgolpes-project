FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    openssl \
    dos2unix \
    gcc \
    libffi-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

WORKDIR /app

RUN adduser --disabled-password --gecos "" appuser

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app

RUN dos2unix /app/entrypoint.sh && chmod +x /app/entrypoint.sh

RUN chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]