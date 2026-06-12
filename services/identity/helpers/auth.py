from fastapi import Depends, HTTPException, Security, status, Request, Response
from jwt import PyJWKClient
import jwt
import os
import requests
import hmac
import hashlib
import base64

COGNITO_REGION = "us-east-2"
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')
CLIENT_SECRET = os.getenv('COGNITO_CLIENT_SECRET')
ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

jwks_client = PyJWKClient(JWKS_URL)

def calcular_secret_hash(username: str):
    mensagem = bytes(username + CLIENT_ID, 'utf-8')
    chave = bytes(CLIENT_SECRET, 'utf-8')

    secret_hash = base64.b64encode(
        hmac.new(chave, mensagem, digestmod=hashlib.sha256).digest()
    ).decode()

    return secret_hash

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

def processa_resposta_cognito(cognito_client, response_cognito: dict, response: Response, email: str):
    if 'ChallengeName' in response_cognito:
        challenge = response_cognito['ChallengeName']
        session = response_cognito['Session']

        if challenge == 'NEW_PASSWORD_REQUIRED':
            return {
                "status": "desafio_nova_senha",
                "mensagem": "Troca de senha inicial obrigatória",
                "session": session,
                "email": email
            }
        elif challenge == 'SOFTWARE_TOKEN_MFA':
            return {
                "status": "desafio_mfa",
                "mensagem": "Insira o código do seu aplicativo autenticador.",
                "session": session,
                "email": email
            }
        elif challenge == 'MFA_SETUP':

            totp_response = cognito_client.associate_software_token(Session=session)
            return {
                "status": "setup_mfa",
                "mensagem": "Configuração de MFA obrigatória. Escaneie o QR Code.",
                "totp_secret": totp_response['SecretCode'],
                "session": totp_response['Session'],
                "email": email
            }
        else:
            raise HTTPException(status_code=500, detail=f"Desafio não suportado: {challenge}")
    elif 'AuthenticationResult' in response_cognito:
        resultado_auth = response_cognito['AuthenticationResult']

        response.set_cookie(
            key="access_token",
            value=resultado_auth['AccessToken'],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=resultado_auth['ExpiresIn']
        )

        response.set_cookie(
            key="refresh_token",
            value=resultado_auth['RefreshToken'],
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=5*24*60*60
        )
        
        return {"status": "sucesso", "mensagem": "Login realizado com sucesso!"}
    else:
        raise HTTPException(status_code=500, detail="Resposta inesperada do Cognito.")