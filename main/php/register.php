<?php
    header('Content-Type: application/json; charset=utf-8');
    require_once '../../database/database.php';

    if ($_SERVER['REQUEST_METHOD'] != 'POST') {
        http_response_code(405);
        die(json_encode(['status' => 'erro', 'mensagem' => 'Metodo nao permitido']));
    }

    $dados = json_decode(file_get_contents('php://input'), true);
    
    if (empty($dados['email']) || empty($dados['nome']) || empty($dados['senha'])) {
        http_response_code(422);
        die(json_encode(['status' => 'erro', 'mensagem' => 'Dados cadastrais incompletos']));
    }

    $nome = $dados['nome'];
    $senha = $dados['senha'];
    $email = $dados['email'];

    try {
        $pdo = conectarBanco();
        $stmt = $pdo->prepare("INSERT INTO Usuario (id_perfil, nome, email, senha_hash, criado_em) VALUES (?, ?, ?, ?, ?");
        $stmt->execute(['2', $nome, $email, $senha, ])
    }



?>