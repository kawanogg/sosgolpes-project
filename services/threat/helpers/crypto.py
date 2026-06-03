import base64
import hashlib
import os
import bcrypt
from fastapi import HTTPException
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding as crypto_padding
from cryptography.hazmat.backends import default_backend

def descriptografar_e_gerar_hash(dados_b64: str) -> str:
    caminho_chave_privada = '/tmp/keys/private_key.pem'
    if not os.path.exists(caminho_chave_privada):
        print("Chave privada nao encontrada no caminho especificado.")
        raise HTTPException(status_code=500, detail="Erro interno de configuracao do servidor.")

    with open(caminho_chave_privada, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
            key_file.read(),
            password=None,
            backend=default_backend()
        )

    dados_criptografados = base64.b64decode(dados_b64)
    
    try:
        senha_bytes = private_key.decrypt(
            dados_criptografados,
            crypto_padding.PKCS1v15() 
        )
        senha_clara = senha_bytes.decode('utf-8').strip(" \t\n\r\0\x0B")
    except Exception as e:
        print(f"Falha na descriptografia: {e}")
        raise HTTPException(status_code=403, detail="Falha de seguranca.")

    hash_pesquisa = hashlib.sha256(senha_clara.encode('utf-8')).hexdigest()
    
    senha_clara = None 
    
    return hash_pesquisa