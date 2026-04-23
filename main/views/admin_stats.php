<?php
require_once '../../database/database.php';

// Conectar ao banco
try {
    $pdo = conectarBanco();
} catch (Exception $e) {
    die("Erro ao conectar ao banco: " . $e->getMessage());
}

// Estatísticas
$stats = [];

// Total de usuários
$stmt = $pdo->query("SELECT COUNT(*) as total FROM Usuario");
$stats['usuarios'] = $stmt->fetch()['total'];

// Total de análises de links
$stmt = $pdo->query("SELECT COUNT(*) as total FROM Analise_Link");
$stats['analises'] = $stmt->fetch()['total'];

// Total de registros de leak
$stmt = $pdo->query("SELECT COUNT(*) as total FROM Registro_Leak");
$stats['leaks'] = $stmt->fetch()['total'];

// Total de logs de acesso
$stmt = $pdo->query("SELECT COUNT(*) as total FROM Log_Acesso");
$stats['logs'] = $stmt->fetch()['total'];

// Análises por nível de perigo
$stmt = $pdo->query("SELECT nivel_perigo, COUNT(*) as count FROM Analise_Link GROUP BY nivel_perigo");
$perigo_stats = $stmt->fetchAll(PDO::FETCH_ASSOC);

// Logs de acesso recentes
$stmt = $pdo->query("SELECT l.*, u.nome FROM Log_Acesso l LEFT JOIN Usuario u ON l.id_usuario = u.id_usuario ORDER BY l.data_hora DESC LIMIT 50");
$logs = $stmt->fetchAll(PDO::FETCH_ASSOC);
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Estatísticas e Logs - SOS Golpes</title>
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <header>
        <h1>Estatísticas e Logs de Acesso</h1>
        <nav>
            <a href="admin_panel.php">Painel Admin</a>
            <a href="admin_crud_leak.php">Gerenciar Vazamentos</a>
        </nav>
    </header>

    <main>
        <section>
            <h2>Estatísticas Gerais</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>Total de Usuários</h3>
                    <p><?php echo $stats['usuarios']; ?></p>
                </div>
                <div class="stat-card">
                    <h3>Análises de Links</h3>
                    <p><?php echo $stats['analises']; ?></p>
                </div>
                <div class="stat-card">
                    <h3>Registros de Vazamento</h3>
                    <p><?php echo $stats['leaks']; ?></p>
                </div>
                <div class="stat-card">
                    <h3>Logs de Acesso</h3>
                    <p><?php echo $stats['logs']; ?></p>
                </div>
            </div>
        </section>

        <section>
            <h2>Análises por Nível de Perigo</h2>
            <ul>
                <?php foreach ($perigo_stats as $stat): ?>
                    <li><?php echo $stat['nivel_perigo']; ?>: <?php echo $stat['count']; ?> análises</li>
                <?php endforeach; ?>
            </ul>
        </section>

        <section>
            <h2>Logs de Acesso Recentes</h2>
            <table>
                <thead>
                    <tr>
                        <th>Data/Hora</th>
                        <th>Usuário</th>
                        <th>Ação</th>
                        <th>IP</th>
                    </tr>
                </thead>
                <tbody>
                    <?php foreach ($logs as $log): ?>
                        <tr>
                            <td><?php echo $log['data_hora']; ?></td>
                            <td><?php echo $log['nome'] ?? 'Anônimo'; ?></td>
                            <td><?php echo $log['acao_realizada']; ?></td>
                            <td><?php echo $log['endereco_ip']; ?></td>
                        </tr>
                    <?php endforeach; ?>
                </tbody>
            </table>
        </section>
    </main>

    <footer>
        <p>&copy; 2024 SOS Golpes - Segurança e Privacidade para Web</p>
    </footer>
</body>
</html>