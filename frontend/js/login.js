document.addEventListener('DOMContentLoaded', () => {
    const token = localStorage.getItem('access_token');

    if (token) {
        window.location.href = "http://localhost:8080/"
    }
});

document.getElementById('formularioLogin').addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('emailInput').value.trim();
    const senha = document.getElementById('passwordInput').value.trim();

    if (email && senha) login(email, senha);
});

async function login(email, senha) {
    try {
        const resp = await fetch('/api/auth/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({
                email: email,
                senha: senha
            })
        })

        const dados = await resp.json();

        if (resp.ok && dados.status === 'sucesso') {
            localStorage.setItem('access_token', dados.tokens.access_token);
            localStorage.setItem('id_token', dados.tokens.id_token);

            window.location.href = "http://localhost:8080/"
        }

    } catch (err) {
        console.log("Erro ao conectar com a API")
    }
    
}