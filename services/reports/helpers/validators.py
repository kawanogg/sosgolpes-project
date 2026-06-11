import re
from urllib.parse import urlparse

def validar_url(url: str) -> bool:
    """Valida se a string é uma URL válida"""
    try:
        resultado = urlparse(url)
        return all([resultado.scheme in ['http', 'https'], resultado.netloc])
    except:
        return False

def sanitizar_comentarios(comentario: str) -> str:
    """Sanitiza comentários para evitar ataques básicos"""
    if not comentario:
        return ""
    
    # Remove caracteres de controle perigosos, mas mantém espaços e quebras de linha
    comentario = re.sub(r'[\x00-\x08\x0B-\x0C\x0E-\x1F]', '', comentario)
    
    # Limita o tamanho
    return comentario[:2000].strip()

def validar_tipo_golpe(tipo_golpe: str) -> bool:
    """Valida tipos de golpes permitidos"""
    tipos_permitidos = [
        'Phishing',
        'Quishing',
        'Malware',
        'Ransomware',
        'Fraude',
        'Clonagem de Site',
        'Outro'
    ]
    return tipo_golpe in tipos_permitidos

def validar_ip(ip: str) -> bool:
    """Valida formato de IP"""
    # Regex simples para IPv4 e IPv6
    ipv4_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    ipv6_pattern = r'^([0-9a-fA-F]{0,4}:){2,7}[0-9a-fA-F]{0,4}$'
    
    if re.match(ipv4_pattern, ip):
        # Verifica se cada octeto é <= 255
        octetos = ip.split('.')
        return all(0 <= int(octet) <= 255 for octet in octetos)
    
    return bool(re.match(ipv6_pattern, ip))
