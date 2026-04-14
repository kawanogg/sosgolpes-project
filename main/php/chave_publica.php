<?php
header('Content-Type: text/plain');

$caminho = '/var/keys/public_key.pem';

if (!file_exists($caminho)) {
    http_response_code(500);
    die('Chave publica nao encontrada.');
}

echo file_get_contents($caminho);
