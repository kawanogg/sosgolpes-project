#!/bin/bash

KEYS_DIR="/var/keys"

if [ ! -f "$KEYS_DIR/private_key.pem" ]; then
    echo "Gerando par de chaves RSA..."
    mkdir -p "$KEYS_DIR"
    openssl genrsa -out "$KEYS_DIR/private_key.pem" 2048
    openssl rsa -in "$KEYS_DIR/private_key.pem" -pubout -out "$KEYS_DIR/public_key.pem"
    echo "Chaves RSA geradas com sucesso."
fi

exec uvicorn main:app --host 0.0.0.0 --port 8080 # uvicorn em prod.