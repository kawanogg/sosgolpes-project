# Protecoes OWASP

---

## 1. A03:2021 - Injection (SQL Injection)

Todas as consultas ao banco usam queries parametrizadas.

Implementacao funcional:
- services/admin/main.py - CRUD.
- services/threat/main.py - insercao de logs e historico.
- services/user/main.py - consultas de perfil e historico.
- services/identity/main.py - busca/insercao de usuario.

CWE: CWE-89 (Improper Neutralization of Special Elements used in an SQL Command).

CVE de referencia: CVE-2014-3704 (Drupal 7 "Drupalgeddon" - SQL injection na API de
abstracao de banco, permitindo execucao de SQL sem autenticacao).

---

## 2. A07:2021 - Identification and Authentication Failures

Autenticacao delegada ao AWS Cognito. A cada requisicao protegida o backend
valida o JWT (assinatura via JWKS, algoritmo RS256, issuer e client_id esperados).
Tokens inválidos sao rejeitados com 401. Alem disso, a mensagem de erro de login e generica, evitando enumeracao de usuarios.

Implementacao funcional:
- services/identity/helpers/auth.py - validar_token_jwt (valida assinatura/issuer/client_id).
- services/user/helpers/auth.py, services/threat/helpers/auth.py, services/admin/helpers/auth.py - mesma validacao em cada microsservico.
- services/identity/main.py - login com Cognito.

CWE: 
- CWE-347 (Improper Verification of Cryptographic Signature)
- CWE-287 (Improper Authentication)
- CWE-204 (Observable Response Discrepancy)

CVE de referencia: 
CVE-2015-9235 (biblioteca jsonwebtoken - confusao de algoritmo / aceita alg: none, permitindo forjar tokens JWT). 
Para enumeracao de usuarios: CVE-2018-15473 (OpenSSH - enumeracao de nomes de usuario por diferenca de resposta).

---

## 3. A01:2021 - Broken Access Control (RBAC)

Controle de acesso baseado em papeis usando os grupos do Cognito (Administrador e Cidadao). As rotas administrativas exigem o grupo Administrador, as rotas de usuario exigem usuario autenticado.

Implementacao funcional:
- services/admin/helpers/auth.py / services/identity/helpers/auth.py - requer_admin.
- services/user/helpers/auth.py - requer_cidadao.
- api-gateway/nginx.conf - auth_request /api/auth/verify_admin nas rotas /admin_*, com redirecionamento para login/home em 401/403.

CWE: 
- CWE-862 (Missing Authorization)
- CWE-285 (Improper Authorization)

CVE de referencia: CVE-2023-22515 (Atlassian Confluence - falha de controle de acesso
que permitia a um usuario nao autorizado escalar privilegios e criar conta de administrador).

---

## 4. A02:2021 - Cryptographic Failures

O historico de analises (URL e detalhes) é armazenado criptografado no banco de forma hibrida. Cada registro é cifrado com AES e a chave AES é protegida com RSA.

Implementacao funcional:
- services/threat/helpers/crypto.py - cifrar_hibrido (cifra ao salvar).
- services/user/helpers/crypto.py - decifrar_hibrido (decifra ao ler).
- db/schema.sql - coluna chave_cifrada em Analise_Link.

CWE: 
- CWE-311 (Missing Encryption of Sensitive Data)
- CWE-312 (Cleartext Storage of Sensitive Information)

CVE de referencia: CVE-2020-11500 (Zoom - uso de AES-128 no modo ECB, que vaza padroes
do texto claro).

---

## 5. A02:2021 - Cryptographic Failures (dados em transito)

O trafego é servido por HTTPS/TLS no api-gateway, com TLSv1.2/TLSv1.3 e
cifras HIGH. Todo acesso em HTTP (porta 8080) é redirecionado para HTTPS.

Implementacao funcional:
- api-gateway/nginx.conf - listen 8443 ssl, ssl_protocols TLSv1.2 TLSv1.3,
  ssl_ciphers HIGH:!aNULL:!MD5 e return 301 https://... na porta 8080.
- api-gateway/entrypoint.sh - geracao do certificado TLS em runtime.

CWE: 
- CWE-319 (Cleartext Transmission of Sensitive Information)

CVE de referencia: CVE-2014-3566 (POODLE - downgrade para SSL 3.0 permitia decifrar dados).

---

## 6. A07/A05:2021 - Protecao de Sessao e Tokens

Os tokens ficam em cookies HttpOnly, Secure e SameSite=Lax, o que impede leitura por JavaScript (mitiga roubo via XSS) e reduz CSRF. Logout com revogacao no Cognito e limpeza dos cookies.

Implementacao funcional:
- services/identity/main.py - set_cookie() no login/nova_senha. Logout com admin_user_global_sign_out e delete_cookie.

CWE: 
- CWE-1004 (Sensitive Cookie Without 'HttpOnly' Flag)
- CWE-614 (Sensitive Cookie in HTTPS Session Without 'Secure' Attribute)
- CWE-352 (CSRF, mitigado por SameSite)
- CWE-613 (Insufficient Session Expiration)

CVE de referencia: CVE-2019-12616 (phpMyAdmin - CSRF que permitia executar SQL em nome da
vitima).

---

## 7. A06:2021 - Vulnerable and Outdated Components (pipeline de seguranca)

O pipeline de CI/CD executa varreduras de seguranca automaticas a cada push/PR. 
- SAST (Bandit, Snyk Code, Semgrep)
- SCA 
- DAST (OWASP ZAP)

Isso detecta dependencias vulneraveis e falhas de codigo antes do deploy.

Implementacao funcional:
- .github/workflows/pipeline.yaml

CWE: 
- CWE-1395 (Dependency on a Vulnerable Third-Party Component)
- CWE-1104 (Use of Unmaintained Third Party Components).

CVE de referencia: CVE-2021-44228 (Log4Shell - RCE na biblioteca Log4j).

---

## 8. Tratamento de Credenciais

O app nao armazena senhas. O cadastro/login é feito pelo Cognito, que é responsável pelo armazenamento das credenciais. A tabela Usuario guarda apenas dados nao sensiveis (nome, email, perfil). No verificador de senhas, a senha trafega cifrada (RSA) e é comparada via hash SHA-256, sem ser persistida.

Implementacao funcional:
- services/identity/main.py - cadastro/login via cognito_client.
- db/schema.sql - Usuario sem coluna de senha.
- services/threat/main.py / services/threat/helpers/crypto.py - verificacao de senha por hash, sem persistir o valor.

CWE:
- CWE-256 (Plaintext Storage of a Password)
- CWE-522 (Insufficiently Protected Credentials).

CVE de referencia: CVE-2019-11510 (Pulse Secure VPN).

---