import os
import urllib
import time
from datetime import datetime
from fastapi import FastAPI, Request, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, PlainTextResponse
import mysql.connector

from app.db.connect_db import get_db
from app.helpers.crypto import (
    descriptografar_e_gerar_hash,
    gerar_hash_senha
)
from app.helpers.analise_links import (
    analisar_heuristica, 
    analisar_google_safe_browsing, 
    analisar_virus_total
)

app = FastAPI()

def get_db():
    db = mysql.connector.connect(
        host='db',
        database='sos_golpes',
        user='root',
        password=os.getenv('MYSQL_ROOT_PASSWORD')
    )
    try:
        yield db
    finally:
        db.close()

# --- ROTAS DE VIEWS ---
@app.get("/")
def home():
    return FileResponse("app/views/index.html")

@app.get("/link_analysis")
def link_analysis():
    return FileResponse("app/views/link_analysis.html")

@app.get("/password_checker")
def password_checker():
    return FileResponse("app/views/password_checker.html")

@app.get("/admin_panel")
def admin_panel():
    return FileResponse("app/views/admin_panel.html")

@app.get("/admin_crud")
def admin_crud():
    return FileResponse("app/views/admin_crud.html")

@app.get("/admin_stats")
def admin_stats():
    return FileResponse("app/views/admin_stats.html")

@app.get("/register")
def register ():
    return FileResponse("app/views/register.html")

@app.get("/login")
def login():
    return FileResponse("app/views/login.html")

# --- ROTAS DE API ---
@app.get("/api/chave_publica")
def get_public_key():
    caminho = '/var/keys/public_key.pem'
    if not os.path.exists(caminho):
        raise HTTPException(status_code=500, detail="Chave publica nao encontrada.")
    with open(caminho, 'r') as f:
        return PlainTextResponse(f.read())

@app.post("/api/processar_senha")
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

@app.post("/api/analisar_link")
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

@app.post("/api/registrar_usuario")
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
@app.get("/api/admin_crud")
async def listar_leaks(db=Depends(get_db)):
    cursor = db.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Registro_Leak ORDER BY id_leak DESC")
    resultados = cursor.fetchall()
    return resultados

@app.post("/api/admin_crud")
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

@app.get("/api/admin_stats")
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
    
app.mount("/static", StaticFiles(directory="app/static"), name="static")