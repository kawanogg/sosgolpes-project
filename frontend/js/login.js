document.addEventListener('DOMContentLoaded', function() {
    const isLoggedIn = localStorage.getItem('is_logged_in');

    if (isLoggedIn === 'true') {
        window.location.href = "/"
    }
});

let sessaoAtual = null;
let emailAtual = null;

document.getElementById('formularioLogin').addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('emailInput').value.trim();
    const senha = document.getElementById('passwordInput').value.trim();

    if (email && senha) login(email, senha);
});

document.getElementById('formularioNovaSenha').addEventListener('submit', async function(e) {
    e.preventDefault();

    const nome = document.getElementById('nomeInput').value.trim();
    const novaSenha = document.getElementById('novaSenhaInput').value.trim();
    const confirmaSenha = document.getElementById('confirmaSenhaInput').value.trim();
    
    if (nome && novaSenha && confirmaSenha) {
        if (novaSenha == confirmaSenha) enviarNovaSenha(nome, novaSenha);
        else alert("As senhas não coincidem");
    }
});

document.getElementById('btnCancelarNovaSenha').addEventListener('click', function() {
    document.getElementById('formularioNovaSenha').style.display = 'none';
    document.getElementById('formularioLogin').style.display = 'block';

    sessaoAtual = null;
    emailAtual = null;
    document.getElementById('nomeInput').value = '';
    document.getElementById('novaSenhaInput').value = '';
    document.getElementById('confirmaSenhaInput').value = '';
    
})

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
        } else if (resp.ok && dados.status === 'desafio'){
            sessaoAtual = dados.session;
            emailAtual = dados.email;

            document.getElementById('formularioLogin').style.display = 'none';
            document.getElementById('formularioNovaSenha').style.display = 'block';
            alert("Como este é seu primeiro acesso, defina uma nova senha definitiva.");
        } else {
            alert("Erro ao fazer login, verifique suas credenciais");
        }

    } catch (err) {
        console.log("Erro ao conectar com a API")
    }
    
}

async function enviarNovaSenha(nome, novaSenha) {
    try {
        const resp = await fetch('/api/auth/nova_senha', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({
                email: emailAtual,
                nome: nome,
                nova_senha: novaSenha,
                session: sessaoAtual
            })
        });

        const dados = await resp.json();

        if (resp.ok && dados.status === 'sucesso') {
            sessaoAtual = null;
            emailAtual = null;
            
            localStorage.setItem('is_logged_in', 'true');
            window.location.href = "/";
        } else {
            alert("Erro ao atualizar a senha. Tente novamente.");
        }
    } catch (err) {
        console.log("Erro ao conectar com a API");
    }
}