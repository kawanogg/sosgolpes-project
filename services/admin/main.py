import os
from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
import mysql.connector

from db.connect_db import get_db

app = FastAPI()

class LeakCreate(BaseModel):
    senha_hash: str
    fonte: str

@app.get("/api/admin/leaks")
async def listar_leaks(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Registro_Leak ORDER BY id_leak DESC")
    return cursor.fetchall()

@app.get("/api/admin/leaks/{id_leak}")
async def obter_leak(id_leak: int, db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Registro_Leak WHERE id_leak = %s", (id_leak,))
    resultado = cursor.fetchone()
    if not resultado:
        raise HTTPException(status_code=404, detail="Registro nao encontrado.")
    return resultado

@app.post("/api/admin/leaks")
async def criar_leak(leak: LeakCreate, db=Depends(get_db)):
    if not leak.senha_hash or not leak.fonte:
        raise HTTPException(status_code=400, detail="Campos 'senha_hash' e 'fonte' sao obrigatorios.")

    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_leak FROM Registro_Leak WHERE senha_vazada_hash = %s", (leak.senha_hash,))
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Este hash de senha ja esta registrado na base.")

        cursor.execute(
            "INSERT INTO Registro_Leak (senha_vazada_hash, fonte_vazamento) VALUES (%s, %s)",
            (leak.senha_hash, leak.fonte)
        )
        db.commit()
        return {"status": "sucesso", "mensagem": "Registro adicionado!", "id": cursor.lastrowid}

    except mysql.connector.Error as err:
        db.rollback()
        if err.errno == 1062:
            raise HTTPException(status_code=409, detail="Este hash de senha ja existe.")
        raise HTTPException(status_code=500, detail="Falha interna no banco de dados.")

@app.put("/api/admin/leaks/{id_leak}")
async def atualizar_leak(id_leak: int, leak: LeakCreate, db=Depends(get_db)):
    if not leak.senha_hash or not leak.fonte:
        raise HTTPException(status_code=400, detail="Campos 'senha_hash' e 'fonte' sao obrigatorios.")

    cursor = db.cursor()
    try:
        cursor.execute("SELECT id_leak FROM Registro_Leak WHERE id_leak = %s", (id_leak,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Registro nao encontrado.")

        cursor.execute(
            "SELECT id_leak FROM Registro_Leak WHERE senha_vazada_hash = %s AND id_leak != %s",
            (leak.senha_hash, id_leak)
        )
        if cursor.fetchone():
            raise HTTPException(status_code=409, detail="Outro registro ja usa este hash de senha.")

        cursor.execute(
            "UPDATE Registro_Leak SET senha_vazada_hash = %s, fonte_vazamento = %s WHERE id_leak = %s",
            (leak.senha_hash, leak.fonte, id_leak)
        )
        db.commit()
        return {"status": "sucesso", "mensagem": "Registro atualizado!"}

    except mysql.connector.Error as err:
        db.rollback()
        if err.errno == 1062:
            raise HTTPException(status_code=409, detail="Este hash de senha ja existe.")
        raise HTTPException(status_code=500, detail="Falha interna no banco de dados.")

@app.delete("/api/admin/leaks/{id_leak}")
async def deletar_leak(id_leak: int, db=Depends(get_db)):
    cursor = db.cursor()
    cursor.execute("DELETE FROM Registro_Leak WHERE id_leak = %s", (id_leak,))
    if cursor.rowcount == 0:
        raise HTTPException(status_code=404, detail="Registro nao encontrado.")
    db.commit()
    return {"status": "sucesso", "mensagem": "Registro deletado!"}

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