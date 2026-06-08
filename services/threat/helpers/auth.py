import os
import boto3
from jwt import PyJWKClient
import jwt

COGNITO_REGION = "us-east-2"
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
ISSUER = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}"
JWKS_URL = f"https://cognito-idp.{COGNITO_REGION}.amazonaws.com/{USER_POOL_ID}/.well-known/jwks.json"

jwks_client = PyJWKClient(JWKS_URL)
cognito_client = boto3.client('cognito-idp', region_name=COGNITO_REGION)


def extrair_usuario_opcional(request):
    token = request.cookies.get("access_token")
    if not token:
        print("[AUTH] Nenhum cookie access_token encontrado.")
        return None

    try:
        signing_key = jwks_client.get_signing_key_from_jwt(token)
        payload = jwt.decode(
            token,
            signing_key.key,
            algorithms=['RS256'],
            issuer=ISSUER
        )
        print(f"[AUTH] Usuario identificado (sub): {payload.get('username')}")
        return payload
    except Exception as e:
        print(f"[AUTH] Erro ao validar JWT: {e}")
        return None


def resolver_email_cognito(username):
    try:
        response = cognito_client.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=username
        )
        atributos = {attr['Name']: attr['Value'] for attr in response['UserAttributes']}
        email = atributos.get('email')
        nome = atributos.get('name', email)
        print(f"[AUTH] Email resolvido via Cognito: {email}, nome: {nome}")
        return {"email": email, "nome": nome}
    except Exception as e:
        print(f"[AUTH] Erro ao resolver email via Cognito: {e}")
        return None
