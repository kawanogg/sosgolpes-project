import os
import urllib
import time
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
import mysql.connector

from db.connect_db import get_db

app = FastAPI()

@app.get("/api/admin/admin_crud")
async def listar_leaks(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Registro_Leak ORDER BY id_leak DESC")
    resultados = cursor.fetchall()
    return resultados

@app.post("/api/admin/admin_crud")
async def gerenciar_leaks(request: Request, db=Depends(get_db)):
    try:
        dados = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Corpo da requisicao invalido.")

    acao = dados.get("action", "")
    cursor = db.cursor()

    try:
        if acao == "add":
            senha_hash = dados.get("senha_hash", "")
            fonte = dados.get("fonte", "")
            
            # O SELECT continua aqui como primeira linha de defesa
            cursor.execute("SELECT id_leak FROM Registro_Leak WHERE senha_vazada_hash = %s", (senha_hash,))
            if cursor.fetchone():
                return {"status": "erro", "mensagem": "Este hash de senha já está registrado na base."}
            
            # Se passar, tenta inserir
            cursor.execute(
                "INSERT INTO Registro_Leak (senha_vazada_hash, fonte_vazamento) VALUES (%s, %s)",
                (senha_hash, fonte)
            )
            db.commit()
            return {"status": "sucesso", "mensagem": "Registro adicionado!"}
            
        elif acao == "delete":
            id_leak = dados.get("id")
            cursor.execute("DELETE FROM Registro_Leak WHERE id_leak = %s", (id_leak,))
            db.commit()
            return {"status": "sucesso", "mensagem": "Registro deletado!"}
            
        else:
            return {"status": "erro", "mensagem": "Acao invalida!"}

    except mysql.connector.Error as err:
        db.rollback()
        if err.errno == 1062: 
            print("Tentativa de registro duplicado bloqueada.")
            return {"status": "erro", "mensagem": "Este hash de senha já existe."}
        else:
            print(f"Erro de Banco de Dados: {err}")
            raise HTTPException(status_code=500, detail="Falha interna no banco de dados.")
            
    except Exception as e:
        print(f"Erro no servidor: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro interno do servidor.")

@app.get("/api/admin/admin_stats")
async def obter_estatisticas(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    try:
        stats = {}
        
        cursor.execute("SELECT COUNT(*) as count FROM Usuario")
        stats['usuarios'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Analise_Link")
        stats['analises'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Registro_Leak")
        stats['leaks'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT COUNT(*) as count FROM Log_Acesso")
        stats['logs'] = cursor.fetchone()['count']
        
        cursor.execute("SELECT nivel_perigo, COUNT(*) as count FROM Analise_Link GROUP BY nivel_perigo")
        perigo_stats = cursor.fetchall()
        
        query_logs = """
            SELECT l.data_hora, u.nome, l.acao_realizada, l.endereco_ip 
            FROM Log_Acesso l 
            LEFT JOIN Usuario u ON l.id_usuario = u.id_usuario 
            ORDER BY l.data_hora DESC LIMIT 50
        """
        cursor.execute(query_logs)
        logs = cursor.fetchall()
        
        for log in logs:
            if log['data_hora']:
                log['data_hora'] = str(log['data_hora'])
                
        return {
            'status': 'sucesso',
            'stats': stats,
            'perigo_stats': perigo_stats,
            'logs': logs
        }
    except Exception as e:
        print(f"Erro ao obter estatisticas: {e}")
        return {"status": "erro", "mensagem": "Falha interna ao recolher as estatisticas."}