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

    try {
        const resp = await fetch('/main/php/register.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({
                email: email,
                nome: nome,
                senha: senha
            })
        });
        const dados = await resp.json();
    } catch (err) {

    }
})