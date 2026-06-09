import base64
import os
from fastapi import HTTPException
from cryptography.hazmat.primitives import serialization, hashes, padding as sym_padding
from cryptography.hazmat.primitives.asymmetric import padding as crypto_padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

CAMINHO_CHAVE_PRIVADA = '/var/keys/private_key.pem'


def carregar_chave_privada():
    if not os.path.exists(CAMINHO_CHAVE_PRIVADA):
        raise HTTPException(status_code=500, detail="Chave privada nao encontrada.")
    with open(CAMINHO_CHAVE_PRIVADA, "rb") as f:
        return serialization.load_pem_private_key(
            f.read(), password=None, backend=default_backend()
        )


def decifrar_hibrido(dado_cifrado_b64: str, chave_aes_cifrada_b64: str) -> str:
    chave_privada = carregar_chave_privada()
    aes_key = chave_privada.decrypt(
        base64.b64decode(chave_aes_cifrada_b64),
        crypto_padding.OAEP(
            mgf=crypto_padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )

    blob = base64.b64decode(dado_cifrado_b64)
    iv, ciphertext = blob[:16], blob[16:]

    decifrador = Cipher(
        algorithms.AES(aes_key), modes.CBC(iv), backend=default_backend()
    ).decryptor()
    dados_preenchidos = decifrador.update(ciphertext) + decifrador.finalize()

    unpadder = sym_padding.PKCS7(algorithms.AES.block_size).unpadder()
    texto = unpadder.update(dados_preenchidos) + unpadder.finalize()
    return texto.decode("utf-8")
