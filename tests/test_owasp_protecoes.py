import base64
import hashlib
import hmac
import importlib.util
import os
import sys

import pytest

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SERVICES = os.path.join(RAIZ, "services")

def carregar_modulo(nome: str, caminho_relativo: str):
    caminho = os.path.join(SERVICES, caminho_relativo)
    spec = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(spec)
    sys.modules[nome] = modulo
    spec.loader.exec_module(modulo)
    return modulo


def test_hash_senha_bcrypt_nao_armazena_texto_claro():
    import bcrypt

    crypto = carregar_modulo("identity_crypto", "identity/helpers/crypto.py")

    senha = "SenhaSecreta123!"
    hashed, salt = crypto.gerar_hash_senha(senha)

    if senha.encode("utf-8") in hashed:
        pytest.fail("O hash contem a senha em texto claro")

    if not bcrypt.checkpw(senha.encode("utf-8"), hashed):
        pytest.fail("A senha correta nao foi validada")
    
    if bcrypt.checkpw(b"senha-errada", hashed):
        pytest.fail("A senha errada foi validada")

def test_cifragem_hibrida(tmp_path):
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa

    # Gerando um par RSA apenas para o teste :)
    chave_privada = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    pem_privada = chave_privada.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_publica = chave_privada.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    caminho_pub = tmp_path / "public_key.pem"
    caminho_priv = tmp_path / "private_key.pem"
    caminho_pub.write_bytes(pem_publica)
    caminho_priv.write_bytes(pem_privada)

    threat_crypto = carregar_modulo("threat_crypto", "threat/helpers/crypto.py")
    user_crypto = carregar_modulo("user_crypto", "user/helpers/crypto.py")

    threat_crypto.CAMINHO_CHAVE_PUBLICA = str(caminho_pub)
    user_crypto.CAMINHO_CHAVE_PRIVADA = str(caminho_priv)

    original = "https://sitemalicioso.com/login"
    campos_cifrados, chave_aes_cifrada = threat_crypto.cifrar_hibrido({"url": original})

    if original in campos_cifrados["url"]:
        pytest.fail("O dado cifrado contem o texto claro")

    recuperado = user_crypto.decifrar_hibrido(campos_cifrados["url"], chave_aes_cifrada)
    if recuperado != original:
        pytest.fail("O texto decifrado nao corresponde ao original")

def test_sanitizar_comentarios():
    validators = carregar_modulo("reports_validators", "reports/helpers/validators.py")

    entrada = "Comentario\x00valido\x07com lixo"
    if validators.sanitizar_comentarios(entrada) != "Comentariovalidocom lixo":
        pytest.fail("Caracteres de controle nao foram removidos corretamente")

    if len(validators.sanitizar_comentarios("a" * 5000)) != 2000:
        pytest.fail("O comprimento nao foi limitado a 2000 caracteres")

    if validators.sanitizar_comentarios("") != "":
        pytest.fail("Entrada vazia nao retornou string vazia")

def test_validacao_entrada_allowlist():
    validators = carregar_modulo("reports_validators", "reports/helpers/validators.py")

    # Apenas valores da allowlist
    if not validators.validar_tipo_golpe("Phishing"):
        pytest.fail("Tipo de golpe valido foi rejeitado")
    if validators.validar_tipo_golpe("DROP TABLE"):
        pytest.fail("Tipo de golpe invalido foi aceito")

    # Valida esquema
    if not validators.validar_url("https://exemplo.com"):
        pytest.fail("URL valida foi rejeitada")
    if validators.validar_url("javascript:alert(1)"):
        pytest.fail("URL invalida foi aceita")

    # Rejeita IPs invalidos
    if not validators.validar_ip("192.168.0.1"):
        pytest.fail("IP valido foi rejeitado")
    if validators.validar_ip("999.999.999.999"):
        pytest.fail("IP invalido foi aceito")
