<?php
header('Content-Type: application/json');
require_once '../../database/database.php';
$pdo = conectarBanco();
$method = $_SERVER['REQUEST_METHOD'];

if ($method === 'GET') {
    $stmt = $pdo->query("SELECT * FROM Registro_Leak ORDER BY id_leak DESC");
    echo json_encode($stmt->fetchAll(PDO::FETCH_ASSOC));
    exit;
}

if ($method === 'POST') {
    $data = json_decode(file_get_contents('php://input'), true);
    $action = $data['action'] ?? '';

    if ($action === 'add') {
        $stmt = $pdo->prepare("INSERT INTO Registro_Leak (senha_vazada_hash, fonte_vazamento) VALUES (?, ?)");
        $stmt->execute([htmlspecialchars($data['senha_hash']), htmlspecialchars($data['fonte'])]);
        echo json_encode(['status' => 'sucesso', 'mensagem' => 'Registro adicionado!']);
    } elseif ($action === 'delete') {
        $stmt = $pdo->prepare("DELETE FROM Registro_Leak WHERE id_leak = ?");
        $stmt->execute([(int)$data['id']]);
        echo json_encode(['status' => 'sucesso', 'mensagem' => 'Registro deletado!']);
    }
    else {
        echo json_encode(['status' => 'erro', 'mensagem' => 'Ação inválida!']);
    }
}
?>