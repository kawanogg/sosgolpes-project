document.addEventListener('DOMContentLoaded', function() {
    const isLoggedIn = localStorage.getItem('is_logged_in');

    if (isLoggedIn === 'true') {
        window.location.href = "/"
    }
});

document.getElementById('formularioCadastro').addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('emailInput').value.trim();
    const nome = document.getElementById('nameInput').value.trim();
    const senha = document.getElementById('passwordInput').value.trim();
    const confirma_senha = document.getElementById('confirmPasswordInput').value.trim();

    if (senha != confirma_senha) {
        alert('Senhas não batem');
        return;
    }

    if (email && nome && senha && confirma_senha) registrar_usuario(email, nome, senha);
    
})

async function registrar_usuario(email, nome, senha) {
    try {
            const resp = await fetch('/api/auth/registrar_usuario', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json'},
                body: JSON.stringify({
                    email: email,
                    nome: nome,
                    senha: senha
                })
            });
            const dados = await resp.json();

            if (dados.status === 'sucesso') {
                window.location.href = "/login"
            } else if (dados.status === 'erro') {
                alert(dados.mensagem)
            }
        } catch (err) { alert("Erro ao cadastrar o usuário, tente novamente em alguns minutos"); }
}