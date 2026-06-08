#!/bin/sh

CERT_DIR="/etc/nginx/certs"
CERT_FILE="$CERT_DIR/localhost.pem"
KEY_FILE="$CERT_DIR/localhost-key.pem"

if [ ! -f "$CERT_FILE" ]; then
    echo "Certificado não encontrado. Gerando certificado autoassinado..."
    
    openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
        -keyout "$KEY_FILE" \
        -out "$CERT_FILE" \
        -subj "/C=BR/ST=PR/L=Curitiba/O=SOS-Golpes/CN=localhost"
    
    echo "Certificado gerado com sucesso!"
else
    echo "Certificado já existe. Iniciando o Nginx..."
fi

exec "$@"