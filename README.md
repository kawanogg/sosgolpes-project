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

- Página Inicial: http://localhost:8080/
- Auditoria de Senhas: http://localhost:8080/password_checker
- Análise de Links: http://localhost:8080/link_analysis
- Painel Administrativo: http://localhost:8080/admin_panel

### 4. Estrutura do Projeto
- /app/helpers: Lógicas (Criptografia e integração com APIs de análise).
- /app/db: Configuração e conexão com o banco de dados.
- /app/views: Arquivos HTML.
- /app/static: Arquivos estáticos (CSS, JS, Imagens).
- main.py: Ponto de entrada da aplicação.

### 5. Parar os containers

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

- [x] Migração PHP para Python
- [x] FastAPI
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

- [x] Revisao de Prepared Statements (SQL Injection)
- [ ] Verificacao de logs (nenhuma senha em texto claro)
- [ ] Revisao do DFD
- [x] SAST
- [ ] DAST
- [x] SCA

### Fase 5: Erros
- [ ] Revisar feedbacks para o usuário (mensagens de erro e etc).
- Situação atual: O user nn ta sabendo o pq q deu erro... PAIA.

---

Made with ❤️ by OqQueVcMePedeSorrindoQueEuNaoFacoChorando&trade;
