<!DOCTYPE html>
<html lang="pt-BR">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Painel Administrativo - SOS Golpes</title>
    <link rel="stylesheet" href="../static/css/style.css">
</head>
<body>
    <header>
        <h1>Painel Administrativo - SOS Golpes</h1>
        <nav>
            <a href="index.php">Início</a>
            <a href="admin_panel.php">Painel Admin</a>
            <a href="admin_crud_leak.php">Gerenciar Vazamentos</a>
            <a href="admin_stats.php">Estatísticas</a>
        </nav>
    </header>

    <main>
        <section>
            <h2>Bem-vindo ao Painel Administrativo</h2>
            <p>Aqui você pode gerenciar vazamentos de senhas, visualizar estatísticas e logs de acesso.</p>

            <div class="admin-options">
                <div class="option-card">
                    <h3>Gerenciar Vazamentos</h3>
                    <p>Adicionar, editar ou remover registros de senhas vazadas.</p>
                    <a href="admin_crud_leak.php" class="btn">Acessar CRUD</a>
                </div>

                <div class="option-card">
                    <h3>Estatísticas e Logs</h3>
                    <p>Visualizar estatísticas de uso e logs de acesso.</p>
                    <a href="admin_stats.php" class="btn">Ver Estatísticas</a>
                </div>
            </div>
        </section>
    </main>

    <footer>
        <p>&copy; 2026 SOS Golpes - Segurança e Privacidade para Web</p>
    </footer>
</body>
</html>