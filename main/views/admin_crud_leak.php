<?php
require_once '../../database/database.php';

// Função para sanitizar entrada
function sanitize($data) {
    return htmlspecialchars(strip_tags(trim($data)));
}

// Conectar ao banco
try {
    $pdo = conectarBanco();
} catch (Exception $e) {
    die("Erro ao conectar ao banco: " . $e->getMessage());
}

// Ações CRUD
$action = isset($_GET['action']) ? sanitize($_GET['action']) : 'list';
$message = '';

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    if (isset($_POST['add'])) {
        $senha_hash = sanitize($_POST['senha_hash']);
        $fonte = sanitize($_POST['fonte']);
        if (!empty($senha_hash) && !empty($fonte)) {
            $stmt = $pdo->prepare("INSERT INTO Registro_Leak (senha_vazada_hash, fonte_vazamento) VALUES (?, ?)");
            if ($stmt->execute([$senha_hash, $fonte])) {
                $message = "Registro adicionado com sucesso!";
            } else {
                $message = "Erro ao adicionar registro.";
            }
        } else {
            $message = "Preencha todos os campos.";
        }
    } elseif (isset($_POST['update'])) {
        $id = (int)$_POST['id'];
        $senha_hash = sanitize($_POST['senha_hash']);
        $fonte = sanitize($_POST['fonte']);
        if (!empty($senha_hash) && !empty($fonte)) {
            $stmt = $pdo->prepare("UPDATE Registro_Leak SET senha_vazada_hash = ?, fonte_vazamento = ? WHERE id_leak = ?");
            if ($stmt->execute([$senha_hash, $fonte, $id])) {
                $message = "Registro atualizado com sucesso!";
            } else {
                $message = "Erro ao atualizar registro.";
            }
        } else {
            $message = "Preencha todos os campos.";
        }
    } elseif (isset($_POST['delete'])) {
        $id = (int)$_POST['id'];
        $stmt = $pdo->prepare("DELETE FROM Registro_Leak WHERE id_leak = ?");
        if ($stmt->execute([$id])) {
            $message = "Registro deletado com sucesso!";
        } else {
            $message = "Erro ao deletar registro.";
        }
    }
}

// Buscar registros para listagem
$registros = [];
if ($action === 'list') {
    $stmt = $pdo->query("SELECT * FROM Registro_Leak ORDER BY id_leak DESC");
    $registros = $stmt->fetchAll(PDO::FETCH_ASSOC);
}

// Buscar registro para edição
$registro_edit = null;
if ($action === 'edit' && isset($_GET['id'])) {
    $id = (int)$_GET['id'];
    $stmt = $pdo->prepare("SELECT * FROM Registro_Leak WHERE id_leak = ?");
    $stmt->execute([$id]);
    $registro_edit = $stmt->fetch(PDO::FETCH_ASSOC);
}
?>

<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CRUD Vazamentos - SOS Golpes</title>
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <header>
        <h1>Gerenciar Vazamentos de Senhas</h1>
        <nav>
            <a href="admin_panel.php">Painel Admin</a>
            <a href="?action=list">Listar</a>
            <a href="?action=add">Adicionar</a>
        </nav>
    </header>

    <main>
        <?php if ($message): ?>
            <div class="message"><?php echo $message; ?></div>
        <?php endif; ?>

        <?php if ($action === 'list'): ?>
            <section>
                <h2>Registros de Vazamentos</h2>
                <table>
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Hash da Senha</th>
                            <th>Fonte</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        <?php foreach ($registros as $reg): ?>
                            <tr>
                                <td><?php echo $reg['id_leak']; ?></td>
                                <td><?php echo substr($reg['senha_vazada_hash'], 0, 20) . '...'; ?></td>
                                <td><?php echo $reg['fonte_vazamento']; ?></td>
                                <td>
                                    <a href="?action=edit&id=<?php echo $reg['id_leak']; ?>">Editar</a> |
                                    <form method="post" style="display:inline;">
                                        <input type="hidden" name="id" value="<?php echo $reg['id_leak']; ?>">
                                        <button type="submit" name="delete" onclick="return confirm('Tem certeza?')">Deletar</button>
                                    </form>
                                </td>
                            </tr>
                        <?php endforeach; ?>
                    </tbody>
                </table>
            </section>
        <?php elseif ($action === 'add' || ($action === 'edit' && $registro_edit)): ?>
            <section>
                <h2><?php echo $action === 'add' ? 'Adicionar' : 'Editar'; ?> Registro</h2>
                <form method="post">
                    <?php if ($registro_edit): ?>
                        <input type="hidden" name="id" value="<?php echo $registro_edit['id_leak']; ?>">
                    <?php endif; ?>
                    <label for="senha_hash">Hash da Senha (SHA-256):</label>
                    <input type="text" id="senha_hash" name="senha_hash" value="<?php echo $registro_edit ? $registro_edit['senha_vazada_hash'] : ''; ?>" required>

                    <label for="fonte">Fonte do Vazamento:</label>
                    <input type="text" id="fonte" name="fonte" value="<?php echo $registro_edit ? $registro_edit['fonte_vazamento'] : ''; ?>" required>

                    <button type="submit" name="<?php echo $action === 'add' ? 'add' : 'update'; ?>">
                        <?php echo $action === 'add' ? 'Adicionar' : 'Atualizar'; ?>
                    </button>
                </form>
            </section>
        <?php endif; ?>
    </main>

    <footer>
        <p>&copy; 2024 SOS Golpes - Segurança e Privacidade para Web</p>
    </footer>
</body>
</html>