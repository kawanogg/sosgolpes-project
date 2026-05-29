import os
import urllib
import time
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
    senha, salt = gerar_hash_senha(dados_recebidos.get("senha").strip())
    if not email or not nome or not senha:
        return {"status": "erro", "mensagem": "Dados cadastrais incompletos"}
    
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
            "INSERT INTO Usuario (id_perfil, nome, email, senha_hash, salt, criado_em) VALUES (2, %s, %s, %s, %s, %s)",
            (nome, email, senha, salt, current_ts))
        db.commit()
    except Exception as err:
        return {"status": "erro", "mensagem": "Erro ao se conectar ao banco de dados"}


    

# --- ROTAS DE ADMIN ---
