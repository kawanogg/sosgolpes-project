# SOS Golpes

Plataforma web desenvolvida em PHP focada na capacitacao do cidadao contra ataques de engenharia social (Phishing, Quishing e Vazamento de Credenciais).

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

### 3. Acessar a aplicação

- Auditoria de Senhas: http://localhost:8080/main/views/password_checker.html
- Analise de Links: http://localhost:8080/main/views/link_analysis.html
- Painel Administrativo: http://localhost:8080/main/views/admin_panel.php

### 3. Parar os containers

```bash
docker-compose down
```

Para remover tambem os dados do banco:

```bash
docker-compose down -v
```

---

## Proximos Passos

### Fase 0: Modificar Stack

- [ ] Python Backend
- [ ] FastAPI
- [ ] Microserviços

### Fase 1: Autenticacao Segura e 2FA

- [ ] Paginas de Login e Registro
- [ ] Autenticacao com hashes BCRYPT
- [ ] Duplo fator de autenticacao (TOTP)
- [ ] Controle de sessao com RBAC (Administrador / Cidadao)

### Fase 2: Painel do Administrador

- [x] Interface do Painel Administrativo
- [x] CRUD da tabela Registro_Leak
- [x] Visualizacao de estatisticas e Log_Acesso

### Fase 4: Seguranca

- [ ] Revisao de Prepared Statements (SQL Injection)
- [ ] Verificacao de logs (nenhuma senha em texto claro)
- [ ] Revisao do DFD
- [ ] SAST
- [ ] DAST
- [ ] SCA