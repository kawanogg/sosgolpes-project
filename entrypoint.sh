#!/bin/sh

KEYS_DIR="/var/keys"

if [ ! -f "$KEYS_DIR/private_key.pem" ]; then
    echo "Gerando par de chaves RSA..."
    mkdir -p "$KEYS_DIR"
    openssl genrsa -out "$KEYS_DIR/private_key.pem" 2048
    openssl rsa -in "$KEYS_DIR/private_key.pem" -pubout -out "$KEYS_DIR/public_key.pem"
    chown -R www-data:www-data "$KEYS_DIR"
    echo "Chaves RSA geradas com sucesso."
fi

exec apache2-foreground
