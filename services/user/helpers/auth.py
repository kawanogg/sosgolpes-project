from fastapi import Depends, HTTPException, Security, status, Request
from jwt import PyJWKClient
import jwt
import os
import requests

COGNITO_REGION = "us-east-2"
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
CLIENT_SECRET = os.getenv('COGNITO_CLIENT_SECRET')
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
        return payload
    except jwt.ExpiredSignatureError:
        print("Erro: O token expirou.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token expirado. Faça login novamente.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except jwt.InvalidTokenError as e:
        # Imprime o erro real no console para você debugar (ex: "Signature verification failed", etc)
        print(f"Erro na validação do JWT: {str(e)}") 
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Token inválido ou corrompido.",
            headers={"WWW-Authenticate": "Bearer"}
        )