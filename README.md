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

### Fase 0: Funcionais

- [x] Validação de QR Codes
- [ ] Estatísticas de Tipo de Ameaça *(Parcial: Painel geral pronto, falta agregar dados por ameaça)*
- [ ] Edição de Perfil do Usuário
- [ ] Consultas a Pesquisas Anteriores *(tem o botao Meu Histórico, mas é dummy kkkkk)*
- [ ] Alertas de Riscos
- [ ] Denúncia de links e golpes

### Fase 1: Autenticacao Segura e 2FA

- [ ] Páginas de Login e Registro *(falta lógica completa do back)*
- [x] Autenticacao com hashes BCRYPT
- [ ] Duplo fator de autenticacao (TOTP)  *(falta o fluxo no login)*
- [ ] Controle de sessao com RBAC (Administrador / Cidadao) *(falta colocar uns middlewares nas rotas da API para restringir acessos)*

### Fase 2: Painel do Administrador

- [x] Interface do Painel Administrativo
- [ ] CRUD da tabela Registro_Leak *(falta operações de atualizar e editar registros existentes)*
- [x] Visualizacao de estatisticas gerais e Log_Acesso

### Fase 3: Seguranca

- [ ] Revisao de Prepared Statements (SQL Injection)
- [x] Verificacao de logs (nenhuma senha em texto claro)
- [ ] Revisao do DFD
- [x] SAST
- [ ] DAST
- [x] SCA

### Fase 4: Erros
- [ ] Revisar feedbacks para o usuário (mensagens de erro e etc).
- Situação atual: O user nn ta sabendo o pq q deu erro... PAIA.

---

Made with ❤️ by OqQueVcMePedeSorrindoQueEuNaoFacoChorando&trade;
