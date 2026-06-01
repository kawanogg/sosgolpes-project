import os
import urllib
import time
import boto3
from botocore.exceptions import ClientError
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
import mysql.connector

from db.connect_db import get_db
from helpers.crypto import (
    descriptografar_e_gerar_hash,
    gerar_hash_senha
)
from helpers.auth import calcular_secret_hash

cognito_client = boto3.client('cognito-idp', region_name='us-east-2')
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')
CLIENT_ID = os.getenv('COGNITO_CLIENT_ID')

app = FastAPI()

# --- ROTAS DE API ---
@app.get("/api/chave_publica")
def get_public_key():
    caminho = '/var/keys/public_key.pem'
    if not os.path.exists(caminho):
        raise HTTPException(status_code=500, detail="Chave publica nao encontrada.")
    with open(caminho, 'r') as f:
        return PlainTextResponse(f.read())

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
    except Exception as err:
        return {"status": "erro", "mensagem": "Erro ao se conectar ao banco de dados"}


    

# --- ROTAS DE ADMIN ---
