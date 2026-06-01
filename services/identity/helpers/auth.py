from fastapi import Depends, HTTPException, Security, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import os
import requests
import hmac
import hashlib
import base64

COGNITO_REGION = "us-east-2"
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
CLIENT_SECRET = os.getenv('COGNITO_CLIENT_SECRET')
JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

jwks = requests.get(JWKS_URL).json()

security = HTTPBearer()

def calcular_secret_hash(username: str):
    mensagem = bytes(username + CLIENT_ID, 'utf-8')
    chave = bytes(CLIENT_SECRET, 'utf-8')

    secret_hash = base64.b64encode(
        hmac.new(chave, mensagem, digestmod=hashlib.sha256).digest()
    ).decode()

    return secret_hash

def validar_token_jwt(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    try:
        payload = jwt.decode(
            token,
            jwks,
            algorithms=['RS256'],
            audience=CLIENT_ID
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, expirado ou corrompido",
            headers={"WWW-Authenticate": "Bearer"}
        )

def requer_admin(payload: dict = Depends(validar_token_jwt)):
    grupos = payload.get("cognito:groups", [])
    if "Administrador" not in grupos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Acesso restrito a Administradores."
        )
    return payload