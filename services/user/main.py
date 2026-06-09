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
from helpers.auth import requer_cidadao
from helpers.crypto import decifrar_hibrido

cognito_client = boto3.client('cognito-idp', region_name='us-east-2')
USER_POOL_ID = os.getenv('COGNITO_USER_POOL_ID')

app = FastAPI()

@app.get("/api/user/profile")
async def user_profile(usuario: dict = Depends(requer_cidadao), db=Depends(get_db)):
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


@app.get("/api/user/history")
async def user_history(usuario: dict = Depends(requer_cidadao), db=Depends(get_db)):
    cognito_username = usuario.get("username")

    if not cognito_username:
        raise HTTPException(status_code=400, detail="Usuário não identificado.")

    try:
        response_cognito = cognito_client.admin_get_user(
            UserPoolId=USER_POOL_ID,
            Username=cognito_username
        )
        atributos = {attr['Name']: attr['Value'] for attr in response_cognito['UserAttributes']}
        email_real = atributos.get('email', cognito_username)

        cursor = db.cursor(dictionary=True)
        cursor.execute("SELECT id_usuario FROM Usuario WHERE email = %s", (email_real,))
        usuario_db = cursor.fetchone()

        if not usuario_db:
            return {"status": "sucesso", "historico": []}

        cursor.execute(
            "SELECT url_analisada, nivel_perigo, detalhes_analise, data_consulta, chave_cifrada "
            "FROM Analise_Link WHERE id_usuario = %s ORDER BY data_consulta DESC LIMIT 50",
            (usuario_db["id_usuario"],)
        )
        registros = cursor.fetchall()

        historico = []
        for reg in registros:
            url = reg["url_analisada"]
            detalhes = reg["detalhes_analise"]

            if reg.get("chave_cifrada"):
                try:
                    url = decifrar_hibrido(reg["url_analisada"], reg["chave_cifrada"])
                    if reg["detalhes_analise"]:
                        detalhes = decifrar_hibrido(reg["detalhes_analise"], reg["chave_cifrada"])
                except Exception as dec_err:
                    print(f"Erro ao decifrar registro de historico: {dec_err}")

            historico.append({
                "url": url,
                "nivel": reg["nivel_perigo"],
                "detalhes": detalhes,
                "data": reg["data_consulta"].isoformat() if reg["data_consulta"] else None
            })

        return {"status": "sucesso", "historico": historico}
    except Exception as e:
        print(f"Erro ao buscar histórico: {e}")
        raise HTTPException(status_code=500, detail="Erro interno ao buscar histórico.")