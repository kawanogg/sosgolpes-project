🛡️ SOS Golpes

O SOS Golpes é uma plataforma web desenvolvida em PHP focada na capacitação do cidadão contra ataques de engenharia social (Phishing, Quishing e Vazamento de Credenciais).

Este projeto foi construído com a mentalidade de Security by Design, implementando criptografia assimétrica (RSA) no lado do cliente, sanitização rigorosa de dados e proteção contra as principais vulnerabilidades web (OWASP).

🐳 1. Infraestrutura e Execução (Docker)

Para garantir que o ambiente de desenvolvimento seja idêntico para todos os membros da equipe e fácil de testar, o projeto foi conteinerizado utilizando o Docker.

1.1. Estrutura Docker

Crie os seguintes arquivos na raiz do projeto:

Arquivo: Dockerfile
Este arquivo prepara o servidor web Apache com o PHP e as extensões de segurança necessárias (OpenSSL e PDO MySQL).

FROM php:8.2-apache

# Atualiza os pacotes e instala as extensões necessárias para o projeto
RUN apt-get update && apt-get install -y \
    libssl-dev \
    && docker-php-ext-install pdo pdo_mysql

# Ativa o mod_rewrite do Apache para rotas amigáveis (caso necessário futuramente)
RUN a2enmod rewrite

# Define o diretório de trabalho principal
WORKDIR /var/www/html

# Garante que o usuário do Apache tenha as permissões corretas
RUN chown -R www-data:www-data /var/www/html


Arquivo: docker-compose.yml
Este arquivo orquestra o servidor web (PHP) e o servidor de banco de dados (MySQL), conectando-os em uma rede interna segura.

version: '3.8'

services:
  web:
    build: .
    container_name: sos_golpes_web
    ports:
      - "8080:80"
    volumes:
      # Mapeia a raiz do seu projeto para a raiz do Apache
      - ./:/var/www/html
    environment:
      - DB_HOST=db
      - DB_NAME=sos_golpes
      - DB_USER=root
      - DB_PASS=root_password
    depends_on:
      - db

  db:
    image: mysql:8.0
    container_name: sos_golpes_db
    restart: always
    environment:
      MYSQL_DATABASE: sos_golpes
      MYSQL_ROOT_PASSWORD: root_password
    ports:
      - "3306:3306"
    volumes:
      # Executa o seu schema.sql automaticamente na primeira vez que o banco subir
      - ./database:/docker-entrypoint-initdb.d


1.2. Como Executar

Certifique-se de ter o Docker e o Docker Compose instalados na sua máquina.

Abra o terminal na raiz do projeto e execute:

docker-compose up -d


Acesse a aplicação através do navegador em: http://localhost:8080/main/views/password_checker.php

O banco de dados estará disponível na porta 3306 localmente.

🚀 2. Planejamento e Próximos Passos

Com a infraestrutura base pronta e o módulo de Auditoria de Senhas (RSA + BCRYPT/SHA-256) concluído, o desenvolvimento vai focar nos seguintes pilares táticos para cumprir os requisitos do projeto:

Fase 1: Autenticação Segura e 2FA (Requisito #3)

O coração do controle de acesso ao painel administrativo.

[ ] Criar a base visual das páginas de Login e Registro.

[ ] Desenvolver a classe AuthController.php responsável por validar credenciais utilizando hashes BCRYPT.

[ ] Implementar a geração e validação de tokens TOTP (Time-Based One-Time Password) para o duplo fator de autenticação (2FA) obrigatório.

[ ] Criar o middleware de controle de sessão para garantir o Role-Based Access Control (RBAC) - Requisito #7.

Fase 2: Painel do Administrador (CRUD de Ameaças - Requisito #9)

A interface de gestão interna do sistema.

[ ] Desenvolver a view (HTML/CSS) do Painel Administrativo.

[ ] Criar o controller (AdminController.php) para executar o CRUD na tabela Registro_Leak, permitindo a inserção de novas senhas expostas.

[ ] Implementar a visualização de Estatísticas e a listagem da tabela Log_Acesso para que o administrador possa monitorar abusos do sistema (Requisito #2).

Fase 3: Motor de Análise de Links e QR Codes (Requisitos #4 e #5)

A ferramenta primária de defesa contra Phishing e Quishing.

[ ] Construir a interface para os usuários inserirem URLs ou enviarem imagens de QR Codes.

[ ] Desenvolver a lógica no LinkController.php para validar o nível de perigo das URLs submetidas.

[ ] Integrar biblioteca JavaScript de processamento de imagem para extrair a URL de um QR Code e enviá-la para a análise segura no backend.

Fase 4: Auditoria de Segurança e Testes Finais

Validação intensiva para garantir que nenhuma vulnerabilidade foi introduzida.

[ ] Sanitização Global: Revisar todos os formulários e controllers para garantir o uso estrito de Prepared Statements (PDO) contra SQL Injection (Requisito #8).

[ ] Limpeza de Logs: Verificar ativamente os registros de erro e acesso para garantir que nenhuma informação sensível (como senhas em texto claro) esteja sendo gravada (Requisito #10).

[ ] Revisão final do fluxo do Diagrama de Fluxo de Dados (DFD).