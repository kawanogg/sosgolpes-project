#!/bin/bash
KEYS_DIR="/var/keys"

while [ ! -f "$KEYS_DIR/private_key.pem" ]; do
    sleep 1
done

exec uvicorn main:app --host 0.0.0.0 --port 8000 --proxy-headers --forwarded-allow-ips "*"
