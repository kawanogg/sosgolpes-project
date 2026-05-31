# SOS Golpes

Plataforma web desenvolvida em Python focada na capacitacao do cidadao contra ataques de engenharia social (Phishing, Quishing e Vazamento de Credenciais).

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

### Fase 0: Requisitos Funcionais

- [x] Validacao de QR Codes
- [ ] Estatisticas de Tipo de Ameaca *(painel geral pronto, falta agregar dados por ameaca)*
- [ ] Edicao de Perfil do Usuario
- [ ] Historico de pesquisas anteriores *(tem o botao "Meu Historico", mas eh dummy :\))*
- [ ] Alertas de Riscos
- [ ] Denuncia de links e golpes

### Fase 1: Autenticacao e Controle de Acesso

- [ ] Login com Amazon Cognito
- [x] Registro de usuario com hash BCRYPT
- [ ] Duplo fator de autenticacao — TOTP *(falta fluxo completo no login)*
- [ ] Middleware RBAC nas rotas da API (Administrador / Cidadao)
- [ ] Controle de sessao (JWT)

### Fase 2: Painel do Administrador

- [x] Interface do Painel Administrativo
- [x] CRUD completo da tabela Registro_Leak *(update/edit de registros implementado)*
- [x] Visualizacao de estatisticas gerais e Log_Acesso

### Fase 3: Seguranca de Aplicacao (AppSec)

- [ ] Revisao de Prepared Statements (SQL Injection)
- [x] Verificacao de logs (nenhuma senha em texto claro)
- [x] SAST (Bandit + Snyk Code)
- [ ] DAST (OWASP ZAP)
- [x] SCA (Snyk)

### Fase 4: Seguranca de Infraestrutura

- [ ] Politica de seguranca de Pods
- [ ] Criptografia para Kubernetes Secrets (encryption at rest)

### Fase 5: Experiencia do Usuario e Monitoramento

- [ ] Feedbacks de erro para o usuario *(hj o user nao sabe o que deu errado)*
- [ ] Monitoramento e Telemetria

### Fase 6: Pipeline CI/CD (completo)

- [x] CI (SAST + SCA + Build)
- [ ] CD (deploy automatizado para producao no K8s)

### Fase 7: Arquitetura e Infraestrutura

- [ ] Migrar de monolito para microservicos (front, back, features tudo em microservico)
- [ ] Comunicacao REST entre microservicos
- [ ] Deployments (nao Pods estaticos)
- [ ] Services para interconexao entre componentes
- [ ] Disponibilidade/redundancia
- [ ] Dockerfiles separados por microservico

---

Made with ❤️ by OqQueVcMePedeSorrindoQueEuNaoFacoChorando&trade;
