from fastapi import Depends, HTTPException, status, Request
from jwt import PyJWKClient
import jwt
import os

COGNITO_REGION = "us-east-2"
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

jwks_client = PyJWKClient(JWKS_URL)

def validar_token_jwt(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Não autenticado. Token não encontrado nos cookies."
        )
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            issuer=ISSUER
        )
        if payload.get("client_id") != CLIENT_ID:
            raise jwt.InvalidTokenError("client_id inválido para este token.")
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido, expirado ou corrompido."
        )

def requer_admin(payload: dict = Depends(validar_token_jwt)):
    grupos = payload.get("cognito:groups", [])
    if "Administrador" not in grupos:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a Administradores."
        )
    return payload

def obter_usuario_opcional(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        return None
    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            issuer=ISSUER
        )
        if payload.get("client_id") != CLIENT_ID:
            return None
        return payload
    except Exception:
        return None
