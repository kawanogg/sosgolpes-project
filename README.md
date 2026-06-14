# SOS Golpes

**Importante**: o foco desse projeto **não** é o desenvolvimento das features de análise ou torná-las extremamente detalhadas. A ideia aqui é trabalhar com princípios de DevSecOps, Kubernetes, microserviços e segurança no geral. 
Além disso, uma boa prática de segurança (e.g. criptografia em trânsito) pode não ser observada em todos os locais onde faria sentido se ter essa boa prática, mas pode ter sido implementada 1 única vez para fins de PoC e atendimento de requisitos breves, os quais foram estipulados antes da implementação desse projeto.

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
- [x] Estatisticas de Tipo de Ameaca *(painel geral e agregação por nível de ameaça implementados no microserviço de admin)*
- [x] Edicao de Perfil do Usuario
- [x] Historico de pesquisas anteriores *(tem o botao "Meu Historico", mas eh dummy :\))*
- [x] Alertas de Riscos
- [x] Denuncia de links e golpes

### Fase 1: Autenticacao e Controle de Acesso

- [x] Login com Amazon Cognito
- [x] Registro de usuario com hash BCRYPT
- [x] Duplo fator de autenticacao — TOTP *(falta fluxo completo no login)*
- [x] Middleware RBAC nas rotas da API (Administrador / Cidadao)
- [x] Controle de sessao (JWT)

### Fase 2: Painel do Administrador

- [x] Interface do Painel Administrativo
- [x] CRUD completo da tabela Registro_Leak *(falta update/edit de registros)*
- [x] Visualizacao de estatisticas gerais e Log_Acesso
- [x] Estatísticas por tipo de ameaça no painel administrativo

### Fase 3: Seguranca de Aplicacao (AppSec)

- [x] Verificacao de logs (nenhuma senha em texto claro)
- [x] SAST (Bandit + Snyk Code)
- [x] DAST (OWASP ZAP)
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

- [x] Migrar de monolito para microservicos (front, back, features tudo em microservico)
- [x] Comunicacao REST entre microservicos
- [ ] Deployments (nao Pods estaticos)
- [x] Services para interconexao entre componentes
- [ ] Disponibilidade/redundancia
- [x] Dockerfiles separados por microservico

---

Made with ❤️ by OqQueVcMePedeSorrindoQueEuNaoFacoChorando&trade;
