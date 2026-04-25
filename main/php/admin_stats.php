<?php
header('Content-Type: application/json');
require_once '../../database/database.php';

try {
    $pdo = conectarBanco();
    $stats = [];
    
    $stats['usuarios'] = $pdo->query("SELECT COUNT(*) FROM Usuario")->fetchColumn();
    $stats['analises'] = $pdo->query("SELECT COUNT(*) FROM Analise_Link")->fetchColumn();
    $stats['leaks'] = $pdo->query("SELECT COUNT(*) FROM Registro_Leak")->fetchColumn();
    $stats['logs'] = $pdo->query("SELECT COUNT(*) FROM Log_Acesso")->fetchColumn();
    
    $perigo_stats = $pdo->query("SELECT nivel_perigo, COUNT(*) as count FROM Analise_Link GROUP BY nivel_perigo")->fetchAll(PDO::FETCH_ASSOC);
    $logs = $pdo->query("SELECT l.data_hora, u.nome, l.acao_realizada, l.endereco_ip FROM Log_Acesso l LEFT JOIN Usuario u ON l.id_usuario = u.id_usuario ORDER BY l.data_hora DESC LIMIT 50")->fetchAll(PDO::FETCH_ASSOC);

    echo json_encode([
        'status' => 'sucesso', 
        'stats' => $stats, 
        'perigo_stats' => $perigo_stats, 
        'logs' => $logs
    ]);
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['status' => 'erro', 'mensagem' => $e->getMessage()]);
}
?>