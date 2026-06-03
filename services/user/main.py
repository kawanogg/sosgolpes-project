import os
import urllib
import time
import boto3
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
import mysql.connector

from db.connect_db import get_db
from helpers.auth import validar_token_jwt

cognito_client = boto3.client('cognito-idp', region_name='us-east-2')
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')

app = FastAPI()

@app.get("/api/user/profile")
async def user_profile(usuario: dict = Depends(validar_token_jwt), db=Depends(get_db)):
    email_logado = usuario.get("username")

    if not email_logado:
        raise HTTPException(status_code=400, detail="Usuário não identificado.")
    
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT nome, email FROM Usuario WHERE email = %s",
            [email_logado]
        )
        resultado_db = cursor.fetchone()

        if resultado_db:
            return {
                "status": "sucesso",
                "nome": resultado_db["nome"],
                "email": resultado_db["email"]
            }
        else:
            response_cognito = cognito_client.admin_get_user(
                UserPoolId=USER_POOL_ID,
                Username=email_logado
            )

            atributos = { attr['Name']: attr['Value'] for attr in response_cognito['UserAttributes'] }

            return {
                "status": "sucesso",
                "nome": atributos.get("name"),
                "email": atributos.get("email")
            }
    except cognito_client.exceptions.UserNotFoundException:
        raise HTTPException(status_code=404, detail="Usuário não encontrado nem no banco nem no Cognito.")
    except Exception as e:
        raise HTTPException(status_code=500, detail="Erro interno ao buscar dados do perfil.")