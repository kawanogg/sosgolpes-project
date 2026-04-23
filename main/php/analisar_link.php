<?php
header('Content-Type: application/json; charset=utf-8');
require_once '../../database/database.php';

if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    die(json_encode(['status' => 'erro', 'mensagem' => 'Metodo nao permitido.']));
}

$dados = json_decode(file_get_contents('php://input'), true);

if (empty($dados['url'])) {
    http_response_code(400);
    die(json_encode(['status' => 'erro', 'mensagem' => 'URL nao fornecida.']));
}

$url = trim($dados['url']);
$partes = parse_url($url);
$dominio = strtolower($partes['host'] ?? '');

if (empty($dominio)) {
    http_response_code(400);
    die(json_encode(['status' => 'erro', 'mensagem' => 'Dominio invalido.']));
}

// Executa as 3 analises
$heuristica = analisarHeuristica($url, $dominio, $partes);
$redirect = analisarRedirecionamentos($url);
$gsb = analisarGoogleSafeBrowsing($url);

$pontuacao = $heuristica['pontuacao'] + $redirect['pontuacao'] + $gsb['pontuacao'];
$pontuacao = min($pontuacao, 100);

if ($pontuacao >= 60) {
    $nivel = 'Malicioso';
    $resumo = 'ALERTA: Esta URL apresenta fortes indicios de ser maliciosa.';
} elseif ($pontuacao >= 30) {
    $nivel = 'Suspeito';
    $resumo = 'ATENCAO: Esta URL apresenta caracteristicas suspeitas.';
} else {
    $nivel = 'Seguro';
    $resumo = 'Esta URL nao apresentou indicios significativos de risco.';
}

// Salvar analise no banco
try {
    $pdo = conectarBanco();
    $acao = "Analise de link: {$url} - Nivel: {$nivel}";
    $ip = $_SERVER['REMOTE_ADDR'] ?? 'unknown';
    $stmt = $pdo->prepare("INSERT INTO Log_Acesso (id_usuario, acao_realizada, endereco_ip) VALUES (?, ?, ?)");
    $stmt->execute([null, $acao, $ip]);
} catch (Exception $e) {
    // Log error if needed
    error_log("Erro ao salvar log: " . $e->getMessage());
}

echo json_encode([
    'url_analisada' => $url,
    'dominio' => $dominio,
    'analises' => [
        'heuristica' => $heuristica,
        'redirecionamentos' => $redirect,
        'google_safe_browsing' => $gsb,
    ],
    'pontuacao_risco' => $pontuacao,
    'nivel_perigo' => $nivel,
    'resumo' => $resumo,
], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);

function analisarHeuristica(string $url, string $dominio, array $partes): array
{
    $alertas = [];
    $pontuacao = 0;

    // IP no lugar de dominio
    if (filter_var($dominio, FILTER_VALIDATE_IP)) {
        $alertas[] = 'URL usa endereco IP em vez de dominio.';
        $pontuacao += 25;
    }

    // TLDs suspeitos
    $tlds = ['.tk', '.ml', '.ga', '.cf', '.gq', '.xyz', '.top', '.buzz', '.click'];
    foreach ($tlds as $tld) {
        if (str_ends_with($dominio, $tld)) {
            $alertas[] = "TLD suspeito detectado ({$tld}).";
            $pontuacao += 15;
            break;
        }
    }

    // Encurtadores de URL
    $encurtadores = ['bit.ly', 'tinyurl.com', 'goo.gl', 't.co', 'cutt.ly', 'rb.gy'];
    foreach ($encurtadores as $e) {
        if ($dominio === $e) {
            $alertas[] = "URL encurtada ({$e}).";
            $pontuacao += 20;
            break;
        }
    }

    // Porta nao padrao
    if (!empty($partes['port']) && !in_array($partes['port'], [80, 443])) {
        $alertas[] = "Porta nao padrao ({$partes['port']}).";
        $pontuacao += 10;
    }

    if (empty($alertas)) {
        $alertas[] = 'Nenhum padrao suspeito detectado.';
    }

    return [
        'nome' => 'Analise Heuristica',
        'status' => $pontuacao > 0 ? 'alerta' : 'ok',
        'alertas' => $alertas,
        'pontuacao' => min($pontuacao, 40),
    ];
}

function analisarGoogleSafeBrowsing(string $url): array
{
    $chave = getenv('GOOGLE_SAFE_BROWSING_KEY');

    $payload = json_encode([
        'client' => ['clientId' => 'sos-golpes', 'clientVersion' => '1.0'],
        'threatInfo' => [
            'threatTypes' => ['MALWARE', 'SOCIAL_ENGINEERING', 'UNWANTED_SOFTWARE'],
            'platformTypes' => ['ANY_PLATFORM'],
            'threatEntryTypes' => ['URL'],
            'threatEntries' => [['url' => $url]],
        ],
    ]);

    $contexto = stream_context_create([
        'http' => [
            'method' => 'POST',
            'header' => 'Content-Type: application/json',
            'content' => $payload,
            'timeout' => 10,
        ],
    ]);

    $resposta = @file_get_contents(
        "https://safebrowsing.googleapis.com/v4/threatMatches:find?key={$chave}",
        false,
        $contexto
    );

    if ($resposta === false) {
        return [
            'nome' => 'Google Safe Browsing',
            'status' => 'indisponivel',
            'alertas' => ['Erro na consulta a API.'],
            'pontuacao' => 0,
        ];
    }

    $resultado = json_decode($resposta, true);

    if (!empty($resultado['matches'])) {
        $tipos = ['MALWARE' => 'Malware', 'SOCIAL_ENGINEERING' => 'Phishing', 'UNWANTED_SOFTWARE' => 'Software Indesejado'];
        $encontrados = [];
        foreach ($resultado['matches'] as $m) {
            $encontrados[] = $tipos[$m['threatType']] ?? $m['threatType'];
        }
        return [
            'nome' => 'Google Safe Browsing',
            'status' => 'perigo',
            'alertas' => ['PERIGO: Google identificou como: ' . implode(', ', $encontrados) . '.'],
            'pontuacao' => 50,
        ];
    }

    return [
        'nome' => 'Google Safe Browsing',
        'status' => 'ok',
        'alertas' => ['URL nao consta na base de ameacas do Google.'],
        'pontuacao' => 0,
    ];
}

function analisarRedirecionamentos(string $url): array
{
    $alertas = [];
    $pontuacao = 0;

    $contexto = stream_context_create([
        'http' => [
            'timeout' => 10,
            'follow_location' => 1,
            'max_redirects' => 10,
        ],
        'ssl' => [
            'verify_peer' => false,
            'verify_peer_name' => false,
        ],
    ]);

    $headers = @get_headers($url, true, $contexto);

    if ($headers === false) {
        return [
            'nome' => 'Redirecionamentos',
            'status' => 'indisponivel',
            'alertas' => ['Nao foi possivel verificar redirecionamentos.'],
            'pontuacao' => 0,
        ];
    }

    $locations = $headers['Location'] ?? $headers['location'] ?? [];
    if (is_string($locations)) {
        $locations = [$locations];
    }
    $num_redirects = count($locations);

    if ($num_redirects > 3) {
        $alertas[] = "{$num_redirects} redirecionamentos (possivel ofuscacao).";
        $pontuacao += 20;
    } elseif ($num_redirects > 0) {
        $alertas[] = "{$num_redirects} redirecionamento(s).";
    } else {
        $alertas[] = 'Sem redirecionamentos.';
    }

    $dom_ini = parse_url($url, PHP_URL_HOST);
    $url_final = $num_redirects > 0 ? end($locations) : $url;
    $dom_fim = parse_url($url_final, PHP_URL_HOST);
    
    if ($dom_ini !== $dom_fim) {
        $alertas[] = "Destino final em dominio diferente: {$dom_fim}.";
        $pontuacao += 15;
    }

    return [
        'nome' => 'Redirecionamentos',
        'status' => $pontuacao > 0 ? 'alerta' : 'ok',
        'alertas' => $alertas,
        'pontuacao' => min($pontuacao, 30),
    ];
}
