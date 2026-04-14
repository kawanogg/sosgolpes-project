# SOS Golpes

Plataforma web desenvolvida em PHP focada na capacitacao do cidadao contra ataques de engenharia social (Phishing, Quishing e Vazamento de Credenciais).

Projeto construido com a mentalidade de **Security by Design**, implementando criptografia assimetrica (RSA) no lado do cliente, sanitizacao rigorosa de dados e protecao contra as principais vulnerabilidades web (OWASP).

---

## Estrutura do Projeto

```
sos-golpes/
├── .env                          # Variaveis de ambiente (senhas, API keys)
├── .gitignore
├── Dockerfile                    # PHP 8.2 + Apache + OpenSSL + cURL
├── docker-compose.yml            # Orquestracao web + MySQL
├── entrypoint.sh                 # Gera chaves RSA automaticamente no startup
├── database/
│   ├── database.php              # Conexao PDO com MySQL via env vars
│   └── schema.sql                # Tabelas: Perfil, Usuario, Registro_Leak, etc.
├── keys/                         # Par RSA gerado automaticamente (nao versionar)
│   ├── private_key.pem
│   └── public_key.pem
└── main/
    ├── php/
    │   ├── analisar_link.php     # Motor de analise de links (3 verificacoes)
    │   ├── chave_publica.php     # Endpoint que serve a chave publica RSA
    │   └── processar_senha.php   # Verificacao de senhas vazadas (RSA + SHA-256)
    ├── static/
    │   ├── css/style.css
    │   └── js/
    │       ├── analisar_link.js  # Frontend da analise de links + QR Code
    │       └── crypto_rsa.js     # Criptografia RSA client-side (Web Crypto API)
    └── views/
        ├── link_analysis.html        # Pagina de analise de links e QR Codes
        └── password_checker.html # Pagina de auditoria de senhas
```

---

## Como Executar

### Pre-requisitos

- Docker e Docker Compose instalados

### 1. Configurar variaveis de ambiente

Edite o arquivo `.env` na raiz do projeto:

```env
# Banco de dados
DB_HOST=db
MYSQL_DATABASE=sos_golpes
MYSQL_ROOT_PASSWORD=root_password

# Google Safe Browsing (opcional - obter em https://console.cloud.google.com)
GOOGLE_SAFE_BROWSING_KEY=
```

### 2. Subir os containers

```bash
docker-compose up -d
```

Na primeira execucao, o sistema automaticamente:
- Cria o banco de dados e executa o `schema.sql`
- Gera o par de chaves RSA em `keys/`

### 3. Acessar a aplicacao

- **Auditoria de Senhas:** http://localhost:8080/main/views/password_checker.html
- **Analise de Links:** http://localhost:8080/main/views/link_analysis.html

### 4. Parar os containers

```bash
docker-compose down
```

Para remover tambem os dados do banco:

```bash
docker-compose down -v
```

---

## Modulos Implementados

### Auditoria de Senhas

Verifica se uma senha ja foi exposta em vazamentos de dados.

**Fluxo de seguranca:**
1. Senha e criptografada com RSA (Web Crypto API) no navegador
2. Enviada ao backend via HTTPS (base64)
3. Backend descriptografa com chave privada
4. Gera hash SHA-256 da senha
5. Limpa a senha da memoria imediatamente
6. Consulta o hash contra a tabela `Registro_Leak`

### Analise de Links

Analisa URLs com 3 verificacoes reais de seguranca:

| Verificacao | Descricao | Pontuacao Max |
|---|---|---|
| **Heuristica** | Detecta IPs, TLDs suspeitos, encurtadores, portas nao padrao | 40 pts |
| **Redirecionamentos** | Conta redirects e detecta mudanca de dominio via `get_headers()` | 30 pts |
| **Google Safe Browsing** | Consulta base de ameacas do Google (malware, phishing) | 50 pts |

**Classificacao de risco (0-100):**
- **0-29:** Seguro
- **30-59:** Suspeito
- **60+:** Malicioso

### Analise de QR Codes

Decodifica QR Codes no navegador usando a biblioteca `html5-qrcode` e envia a URL extraida para o motor de analise de links.

---

## Tecnologias

| Componente | Tecnologia |
|---|---|
| Backend | PHP 8.2 + Apache |
| Banco de Dados | MySQL 8.0 |
| Criptografia | RSA 2048-bit (OpenSSL + Web Crypto API) |
| Containers | Docker + Docker Compose |
| Analise de Links | Heuristica + get_headers() + Google Safe Browsing API v4 |
| QR Code | html5-qrcode (client-side) |

---

## Proximos Passos

### Fase 1: Autenticacao Segura e 2FA

- [ ] Paginas de Login e Registro
- [ ] Autenticacao com hashes BCRYPT
- [ ] Duplo fator de autenticacao (TOTP)
- [ ] Controle de sessao com RBAC (Administrador / Cidadao)

### Fase 2: Painel do Administrador

- [ ] Interface do Painel Administrativo
- [ ] CRUD da tabela Registro_Leak
- [ ] Visualizacao de estatisticas e Log_Acesso

### Fase 4: Auditoria de Seguranca

- [ ] Revisao de Prepared Statements (SQL Injection)
- [ ] Verificacao de logs (nenhuma senha em texto claro)
- [ ] Revisao final do DFD
