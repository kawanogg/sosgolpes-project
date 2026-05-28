import os
import urllib.parse
import ipaddress
import base64
import requests

def analisar_heuristica(url: str, dominio: str, partes: urllib.parse.ParseResult) -> dict:
    alertas = []
    pontuacao = 0

    try:
        ipaddress.ip_address(dominio)
        alertas.append("URL usa endereco IP em vez de dominio.")
        pontuacao += 25
    except ValueError:
        pass

    tlds_suspeitos = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.buzz', '.click']
    if any(dominio.endswith(tld) for tld in tlds_suspeitos):
        tld_encontrado = next(tld for tld in tlds_suspeitos if dominio.endswith(tld))
        alertas.append(f"TLD suspeito detectado ({tld_encontrado}).")
        pontuacao += 15

    encurtadores = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'cutt.ly', 'rb.gy']
    if dominio in encurtadores:
        alertas.append(f"URL encurtada ({dominio}).")
        pontuacao += 20

    if partes.port and partes.port not in [80, 443]:
        alertas.append(f"Porta nao padrao ({partes.port}).")
        pontuacao += 10

    if not alertas:
        alertas.append("Nenhum padrao suspeito detectado.")

    return {
        'nome': 'Analise Heuristica',
        'status': 'alerta' if pontuacao > 0 else 'ok',
        'alertas': alertas,
        'pontuacao': min(pontuacao, 40)
    }

def analisar_google_safe_browsing(url: str) -> dict:
    chave = os.getenv('GOOGLE_SAFE_BROWSING_KEY')
    if not chave:
         return {'nome': 'Google Safe Browsing', 'status': 'indisponivel', 'alertas': ['Chave de API nao configurada.'], 'pontuacao': 0}

    payload = {
        'client': {'clientId': 'sos-golpes', 'clientVersion': '1.0'},
        'threatInfo': {
            'threatTypes': ['MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE'],
            'platformTypes': ['ANY_PLATFORM'],
            'threatEntryTypes': ['URL'],
            'threatEntries': [{'url': url}],
        }
    }
    
    try:
        resposta = requests.post(f"https://safebrowsing.googleapis.com/v4/threatMatches:find?key={chave}", json=payload, timeout=10)
        resultado = resposta.json()
        
        if 'matches' in resultado and len(resultado['matches']) > 0:
            tipos_dict = {'MALWARE': 'Malware', 'SOCIAL_ENGINEERING': 'Phishing', 'UNWANTED_SOFTWARE': 'Software Indesejado'}
            encontrados = [tipos_dict.get(m['threatType'], m['threatType']) for m in resultado['matches']]
            
            return {
                'nome': 'Google Safe Browsing',
                'status': 'perigo',
                'alertas': [f"PERIGO: Google identificou como: {', '.join(encontrados)}."],
                'pontuacao': 50
            }
            
        return {
            'nome': 'Google Safe Browsing',
            'status': 'ok',
            'alertas': ['URL nao consta na base de ameacas do Google.'],
            'pontuacao': 0
        }
    except Exception:
        return {
            'nome': 'Google Safe Browsing',
            'status': 'indisponivel',
            'alertas': ['Erro na consulta a API.'],
            'pontuacao': 0
        }

def analisar_virus_total(url: str) -> dict:
    chave = os.getenv('VIRUSTOTAL_KEY')
    if not chave:
         return {'nome': 'VirusTotal', 'status': 'indisponivel', 'alertas': ['Chave de API nao configurada.'], 'pontuacao': 0}

    url_id = base64.urlsafe_b64encode(url.encode('utf-8')).decode('utf-8').rstrip('=')
    
    headers = {
        "accept": "application/json",
        "x-apikey": chave
    }
    
    try:
        resposta = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers, timeout=30)
        if resposta.status_code == 200:
            resultado = resposta.json()
            positivos = resultado.get('data', {}).get('attributes', {}).get('last_analysis_stats', {}).get('malicious', 0)
            
            if positivos > 0:
                return {
                    'nome': 'VirusTotal',
                    'status': 'perigo',
                    'alertas': [f"PERIGO: VirusTotal identificou {positivos} deteccoes maliciosas."],
                    'pontuacao': 50
                }
            else:
                return {
                    'nome': 'VirusTotal',
                    'status': 'ok',
                    'alertas': ['URL nao apresentou deteccoes maliciosas no VirusTotal.'],
                    'pontuacao': 0
                }
        else:
             return {'nome': 'VirusTotal', 'status': 'indisponivel', 'alertas': [f"Erro na consulta a API (Status {resposta.status_code})."], 'pontuacao': 0}
    except Exception:
        return {
            'nome': 'VirusTotal',
            'status': 'indisponivel',
            'alertas': ['Erro na consulta a API.'],
            'pontuacao': 0
        }