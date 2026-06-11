from fastapi import FastAPI, Request, HTTPException, Depends
from pydantic import BaseModel
import mysql.connector

from db.connect_db import get_db
from helpers.validators import validar_url, sanitizar_comentarios, validar_tipo_golpe
from helpers.auth import requer_admin, obter_usuario_opcional

app = FastAPI()

class DenunciaCreate(BaseModel):
    link: str
    tipo_golpe: str
    comentarios: str = ""

class StatusUpdate(BaseModel):
    status: str

STATUSES_VALIDOS = ['Pendente', 'Analisando', 'Confirmado', 'Falso Positivo']


@app.post("/api/reports/create")
async def criar_denuncia(
    denuncia: DenunciaCreate,
    request: Request,
    db=Depends(get_db)
):
    if not validar_url(denuncia.link):
        raise HTTPException(status_code=400, detail="URL inválida. Inclua http:// ou https://")

    if not validar_tipo_golpe(denuncia.tipo_golpe):
        raise HTTPException(status_code=400, detail="Tipo de golpe não reconhecido.")

    comentarios_sanitizados = sanitizar_comentarios(denuncia.comentarios)
    ip_cliente = request.client.host if request.client else 'unknown'

    usuario = obter_usuario_opcional(request)
    email_denunciante = usuario.get("email", "Anônimo") if usuario else "Anônimo"

    try:
        cursor = db.cursor()
        cursor.execute(
            """INSERT INTO Denuncia_Link
               (link_denunciado, tipo_golpe, comentarios, email_denunciante,
                endereco_ip, denuncia_status, data_denuncia)
               VALUES (%s, %s, %s, %s, %s, 'Pendente', NOW())""",
            (denuncia.link, denuncia.tipo_golpe, comentarios_sanitizados,
             email_denunciante, ip_cliente)
        )
        db.commit()
        return {
            "status": "sucesso",
            "mensagem": "Denúncia recebida com sucesso!",
            "id_denuncia": cursor.lastrowid
        }
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao processar denúncia: {str(err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/reports/all")
async def listar_todas_denuncias(
    db=Depends(get_db),
    usuario: dict = Depends(requer_admin)
):
    try:
        cursor = db.cursor(dictionary=True)
        cursor.execute(
            """SELECT id_denuncia, link_denunciado, tipo_golpe, comentarios,
                      email_denunciante, denuncia_status AS status,
                      endereco_ip, data_denuncia
               FROM Denuncia_Link
               ORDER BY data_denuncia DESC"""
        )
        denuncias = cursor.fetchall()

        por_status = {s: [] for s in STATUSES_VALIDOS}
        for d in denuncias:
            s = d.get('status', 'Pendente')
            if s in por_status:
                por_status[s].append(d)
            else:
                por_status['Pendente'].append(d)

        return {
            "status": "sucesso",
            "total": len(denuncias),
            "por_status": por_status
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.put("/api/reports/{id_denuncia}/status")
async def atualizar_status(
    id_denuncia: int,
    body: StatusUpdate,
    db=Depends(get_db),
    usuario: dict = Depends(requer_admin)
):
    if body.status not in STATUSES_VALIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Status inválido. Use: {', '.join(STATUSES_VALIDOS)}"
        )
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT id_denuncia FROM Denuncia_Link WHERE id_denuncia = %s",
            (id_denuncia,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Denúncia não encontrada.")

        cursor.execute(
            "UPDATE Denuncia_Link SET denuncia_status = %s WHERE id_denuncia = %s",
            (body.status, id_denuncia)
        )
        db.commit()
        return {"status": "sucesso", "mensagem": f"Status atualizado para '{body.status}'."}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar status: {str(err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/api/reports/{id_denuncia}")
async def deletar_denuncia(
    id_denuncia: int,
    db=Depends(get_db),
    usuario: dict = Depends(requer_admin)
):
    try:
        cursor = db.cursor()
        cursor.execute(
            "SELECT id_denuncia FROM Denuncia_Link WHERE id_denuncia = %s",
            (id_denuncia,)
        )
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Denúncia não encontrada.")

        cursor.execute(
            "DELETE FROM Denuncia_Link WHERE id_denuncia = %s",
            (id_denuncia,)
        )
        db.commit()
        return {"status": "sucesso", "mensagem": "Denúncia removida com sucesso."}
    except mysql.connector.Error as err:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar denúncia: {str(err)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
