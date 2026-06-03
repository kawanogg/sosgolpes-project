import os
import urllib
import time
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
import mysql.connector

from db.connect_db import get_db

from helpers.analise_links import (
    analisar_heuristica, 
    analisar_google_safe_browsing, 
    analisar_virus_total
)

from helpers.crypto import descriptografar_e_gerar_hash

app = FastAPI()

@app.get("/api/threats/chave_publica")
def get_public_key():
    caminho = '/tmp/keys/public_key.pem'
    if not os.path.exists(caminho):
        raise HTTPException(status_code=500, detail="Chave publica nao encontrada.")
    with open(caminho, 'r') as f:
        return PlainTextResponse(f.read())

@app.post("/api/threats/processar_senha")
async def processar_senha(request: Request, db=Depends(get_db)):
    try:
        dados_recebidos = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Requisicao invalida.")

    dados_b64 = dados_recebidos.get("dadosCriptografados")
    if not dados_b64:
        raise HTTPException(status_code=400, detail="Dados ausentes.")

    hash_pesquisa = descriptografar_e_gerar_hash(dados_b64)

    cursor = db.cursor(dictionary=True)
    query = "SELECT fonte_vazamento FROM Registro_Leak WHERE senha_vazada_hash = %s LIMIT 1"
    cursor.execute(query, (hash_pesquisa,))
    resultado = cursor.fetchone()

    ip = request.client.host if request.client else 'unknown'
    acao_log = f"Verificacao de senha - Status: {'Vazada' if resultado else 'Segura'}"
    try:
        cursor.execute(
            "INSERT INTO Log_Acesso (id_usuario, acao_realizada, endereco_ip) VALUES (NULL, %s, %s)",
            (acao_log, ip)
        )
        db.commit()
    except Exception as log_err:
        print(f"Erro ao salvar log: {log_err}")

    if resultado:
        fonte = resultado['fonte_vazamento']
        return {
            "status": "perigo",
            "mensagem": f"Identificamos que esta senha vazou na base de dados: {fonte}. Recomendamos fortemente que voce altere esta senha em todos os servicos onde a utiliza."
        }
    else:
        return {
            "status": "seguro",
            "mensagem": "Sua senha parece estar segura e nao foi encontrada em nossa base de vazamentos."
        }

@app.post("/api/threats/analisar_link")
async def analisar_link(request: Request, db=Depends(get_db)):
    try:
        dados_recebidos = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Corpo da requisicao invalido.")

    url_crua = dados_recebidos.get("url", "").strip()
    if not url_crua:
        return {"status": "erro", "mensagem": "URL nao fornecida."}

    if not url_crua.startswith(('http://', 'https://')):
        url_crua = 'http://' + url_crua

    partes = urllib.parse.urlparse(url_crua)
    dominio = partes.netloc.lower()

    if not dominio:
        return {"status": "erro", "mensagem": "Dominio invalido."}

    heuristica = analisar_heuristica(url_crua, dominio, partes)
    gsb = analisar_google_safe_browsing(url_crua)
    vt = analisar_virus_total(url_crua)

    pontuacao = heuristica['pontuacao'] + gsb['pontuacao'] + vt['pontuacao']
    pontuacao = min(pontuacao, 100)

    if pontuacao >= 60:
        nivel = 'Malicioso'
        resumo = 'ALERTA: Esta URL apresenta fortes indicios de ser maliciosa.'
    elif pontuacao >= 30:
        nivel = 'Suspeito'
        resumo = 'ATENCAO: Esta URL apresenta caracteristicas suspeitas.'
    else:
        nivel = 'Seguro'
        resumo = 'Esta URL nao apresentou indicios significativos de risco.'

    try:
        acao_log = f"Analise de link: {url_crua} - Nivel: {nivel}"
        ip = request.client.host if request.client else 'unknown'
        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Log_Acesso (id_usuario, acao_realizada, endereco_ip) VALUES (NULL, %s, %s)",
            (acao_log, ip)
        )
        db.commit()
    except Exception as log_err:
        print(f"Erro ao salvar log: {log_err}")

    return {
        'url_analisada': url_crua,
        'dominio': dominio,
        'analises': {
            'heuristica': heuristica,
            'google_safe_browsing': gsb,
            'virus_total': vt,
        },
        'pontuacao_risco': pontuacao,
        'nivel_perigo': nivel,
        'resumo': resumo,
    }