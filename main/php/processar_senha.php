<?php
header('Content-Type: application/json');

$json_bruto = file_get_contents('php://input');
$dados_recebidos = json_decode($json_bruto, true);

if ($_SERVER['REQUEST_METHOD'] !== 'POST' || empty($dados_recebidos['carga_criptografada'])) {
    http_response_code(400);
    die(json_encode(['status' => 'erro', 'mensagem' => 'Requisição inválida ou dados ausentes.']));
}

$carga_base64 = $dados_recebidos['carga_criptografada'];
$dados_criptografados = base64_decode($carga_base64);

$caminho_chave_privada = __DIR__ . '/../keys/private_key.pem';

if (!file_exists($caminho_chave_privada)) {
    error_log("Chave privada não encontrada no caminho especificado.");
    http_response_code(500);
    die(json_encode(['status' => 'erro', 'mensagem' => 'Erro interno de configuração do servidor.']));
}

$chave_privada = openssl_pkey_get_private(file_get_contents($caminho_chave_privada));
$senha_clara = '';

$sucesso = openssl_private_decrypt(
    $dados_criptografados, 
    $senha_clara, 
    $chave_privada,
    OPENSSL_PKCS1_OAEP_PADDING
);

if (!$sucesso || empty($senha_clara)) {
    error_log("Falha ao descriptografar dados.");
    http_response_code(403);
    die(json_encode(['status' => 'erro', 'mensagem' => 'Falha de segurança: Os dados foram corrompidos ou adulterados.']));
}

$hash_pesquisa = hash('sha256', $senha_clara);

$senha_clara = null;
unset($senha_clara);

require_once __DIR__ . '/../config/database.php'; 

try {
    $pdo = conectarBanco();

    $sql = "SELECT fonte_vazamento FROM Registro_Leak WHERE senha_vazada_hash = :hash LIMIT 1";
    $stmt = $pdo->prepare($sql);
    $stmt->execute(['hash' => $hash_pesquisa]);
    
    $resultado = $stmt->fetch(PDO::FETCH_ASSOC);

    if ($resultado) {
        $fonte = htmlspecialchars($resultado['fonte_vazamento']);
        
        echo json_encode([
            'status' => 'perigo',
            'mensagem' => "Identificamos que esta senha vazou na base de dados: {$fonte}. Recomendamos fortemente que você altere esta senha em todos os serviços onde a utiliza."
        ]);
    } else {
        echo json_encode([
            'status' => 'seguro',
            'mensagem' => 'Sua senha parece estar segura e não foi encontrada em nossa base de vazamentos.'
        ]);
    }

} catch (PDOException $e) {
    error_log("Erro de Banco de Dados: " . $e->getMessage());
    http_response_code(500);
    echo json_encode(['status' => 'erro', 'mensagem' => 'Não foi possível consultar o banco de dados no momento.']);
}
?>