document.addEventListener('DOMContentLoaded', function() {
    const isLoggedIn = localStorage.getItem('is_logged_in');

    if (isLoggedIn === 'true') {
        window.location.href = "/"
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
            localStorage.setItem('is_logged_in', 'true');
            window.location.href = "/"
        } else {
            alert("Erro ao fazer login, verifique suas credenciais");
        }

    } catch (err) {
        console.log("Erro ao conectar com a API")
    }
    
}