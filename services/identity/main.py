import os
import urllib
import time
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends, Response
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
import mysql.connector

from db.connect_db import get_db

from helpers.auth import (
    calcular_secret_hash,
    validar_token_jwt
)

cognito_client = boto3.client('cognito-idp', region_name='us-east-2')
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')

app = FastAPI()

# --- ROTAS DE API ---
@app.post("/api/auth/registrar_usuario")
async def registrar_usuario(request: Request, db=Depends(get_db)):
    try:
        dados_recebidos = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Corpo da requisicao invalido.")
    
    email = dados_recebidos.get("email").strip()
    nome = dados_recebidos.get("nome").strip()
    senha = dados_recebidos.get("senha").strip()

    if not email or not nome or not senha:
        return {"status": "erro", "mensagem": "Dados cadastrais incompletos"}

    try:
        hash_calculado = calcular_secret_hash(email)

        response = cognito_client.sign_up(
            ClientId=CLIENT_ID,
            SecretHash=hash_calculado,
            Username=email,
            Password=senha,
            UserAttributes=[
                {'Name': 'name', 'Value': nome},
                {'Name': 'email', 'Value': email}
            ]
        )

        cognito_client.admin_confirm_sign_up(
            UserPoolId=USER_POOL_ID,
            Username=email,
        )

        cognito_client.admin_add_user_to_group(
            UserPoolId=USER_POOL_ID,
            Username=email,
            GroupName='Cidadao'
        )
    
    except ClientError as e:
        erro_aws = e.response['Error']['Message']
        return {"status": "erro", "mensagem": f"Erro no cadastro: {erro_aws}"}
    
    current_ts = datetime.now()
    try:
        cursor = db.cursor()

        cursor.execute(
            "SELECT * FROM Usuario WHERE email = %s",
            [email]
        )
        resultado = cursor.fetchall()
        if resultado:
            return {"status": "info", "mensagem": "Usuário já existe"}

        cursor.execute(
            "INSERT INTO Usuario (id_perfil, nome, email, criado_em) VALUES (2, %s, %s, %s)",
            (nome, email, current_ts))
        db.commit()
        return {"status": "sucesso", "mensagem": "Cadastro realizado com sucesso"}
    except Exception as err:
        return {"status": "erro", "mensagem": "Erro ao se conectar ao banco de dados"}


@app.post("/api/auth/login")
async def login(request: Request, response: Response):
    try:
        dados = await request.json()
        email = dados.get("email").strip()
        senha = dados.get("senha").strip()

        if not email or not senha:
            raise HTTPException(status_code=400, detail="E-mail e senha são obrigatórios.")
        
        response_cognito = cognito_client.admin_initiate_auth(
            UserPoolId=USER_POOL_ID,
            ClientId=CLIENT_ID,
            AuthFlow='ADMIN_NO_SRP_AUTH',
            AuthParameters={
                'USERNAME': email,
                'PASSWORD': senha,
                'SECRET_HASH': calcular_secret_hash(email)
            }
        )

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

        return {
            "status": "sucesso",
            "mensagem": "Login realizado com sucesso",
        }
    except ClientError as e:
        codigo_erro = e.response['Error']['Code']

        if codigo_erro == 'NotAuthorizedException':
            raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
        elif codigo_erro == 'UserNotFoundException':
            raise HTTPException(status_code=401, detail="E-mail ou senha incorretos.")
        elif codigo_erro == 'UserNotConfirmedException':
            raise HTTPException(status_code=403, detail="A conta ainda não foi confirmada.")
        else:
            raise HTTPException(status_code=500, detail=f"Erro interno de autenticação: {e.response['Error']['Message']}")

@app.post("/api/auth/logout")
async def logout(response: Response, usuario: dict = Depends(validar_token_jwt)):
    try:
        username = usuario.get("username")

        cognito_client.admin_user_global_sign_out(
            UserPoolId=USER_POOL_ID,
            Username=username
        )

        response.delete_cookie(key="access_token", httponly=True, secure=True, samesite="lax")
        response.delete_cookie(key="refresh_token", httponly=True, secure=True, samesite="lax")

        return {"status": "sucesso", "mensagem": "Sessão encerrada com segurança no servidor."}
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro ao processar logout no servidor.")