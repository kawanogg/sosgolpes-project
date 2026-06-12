document.addEventListener('DOMContentLoaded', function() {
    const isLoggedIn = localStorage.getItem('is_logged_in');

    if (isLoggedIn === 'true') {
        window.location.href = "/"
    }
});

let sessaoAtual = null;
let emailAtual = null;

const formLogin = document.getElementById('formularioLogin');
const formNovaSenha = document.getElementById('formularioNovaSenha');
const formSetupMFA = document.getElementById('formularioSetupMFA');
const formVerificaMFA = document.getElementById('formularioVerificaMFA');

formLogin.addEventListener('submit', async function(e) {
    e.preventDefault();

    const email = document.getElementById('emailInput').value.trim();
    const senha = document.getElementById('passwordInput').value.trim();

    if (email && senha) login(email, senha);
});

formNovaSenha.addEventListener('submit', async function(e) {
    e.preventDefault();

    const nome = document.getElementById('nomeInput').value.trim();
    const novaSenha = document.getElementById('novaSenhaInput').value.trim();
    const confirmaSenha = document.getElementById('confirmaSenhaInput').value.trim();
    
    if (nome && novaSenha && confirmaSenha) {
        if (novaSenha == confirmaSenha) enviarNovaSenha(nome, novaSenha);
        else alert("As senhas não coincidem");
    }
});

formSetupMFA.addEventListener('submit', async function(e) {
    e.preventDefault();
    const codigoMFA = document.getElementById('codigoSetupInput').value.trim();

    if (codigoMFA) setupMFA(codigoMFA);
});

formVerificaMFA.addEventListener('submit', async function(e) {
    e.preventDefault();
    const codigoMFA = document.getElementById('codigoVerificaInput').value.trim();

    if (codigoMFA) verificaMFA(codigoMFA);
});

document.querySelectorAll('.cancelar-fluxo').forEach(btn => {
    btn.addEventListener('click', resetarFluxo);
});

function processarResposta(dados) {
    if (dados.status === 'sucesso') {
        sessaoAtual = null;
        emailAtual = null;
        localStorage.setItem('is_logged_in', 'true');
        window.location.href = "/";
        
    } else if (dados.status === 'desafio_nova_senha') {
        sessaoAtual = dados.session;
        emailAtual = dados.email;
        esconderTodosFormularios();
        formNovaSenha.style.display = 'block';
        
    } else if (dados.status === 'setup_mfa') {
        sessaoAtual = dados.session;
        emailAtual = dados.email;
        esconderTodosFormularios();
        formSetupMFA.style.display = 'block';
        
        document.getElementById('textoCodigoSecreto').innerText = dados.totp_secret;
        
        const otpAuthUrl = `otpauth://totp/SOSGolpes:${emailAtual}?secret=${dados.totp_secret}&issuer=SOSGolpes`;
        document.getElementById('qrcode-container').innerHTML = '';
        new QRCode(document.getElementById("qrcode-container"), {
            text: otpAuthUrl,
            width: 150,
            height: 150
        });
        
    } else if (dados.status === 'desafio_mfa') {
        sessaoAtual = dados.session;
        emailAtual = dados.email;
        esconderTodosFormularios();
        formVerificaMFA.style.display = 'block';
        
    } else {
        alert(dados.mensagem || "Ocorreu um erro desconhecido.");
        resetarFluxo();
    }
}

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

        if (resp.ok) {
            processarResposta(dados)
        } else {
            alert("Erro ao fazer login, verifique suas credenciais");
        }
    } catch (err) {
        console.log("Erro ao conectar com a API")
        console.log(err)
        alert("Erro ao conectar com a API");
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

        if (resp.ok) {
            processarResposta(dados);
        } else {
            alert("Erro ao atualizar a senha. Tente novamente.");
        }
    } catch (err) {
        console.log("Erro ao conectar com a API");
    }
}

async function setupMFA(codigoMFA) {
    try {
        const resp = await fetch('/api/auth/setup-mfa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({
                email: emailAtual,
                codigo_mfa: codigoMFA,
                session: sessaoAtual
            })
        });

        const dados = await resp.json();
        if (resp.ok) {
            processarResposta(dados);
        } else {
            alert("Código MFA inválido. Tente novamente.");
        }
    } catch (err) {
        alert("Erro ao conectar com a API");
    }
}

async function verificaMFA(codigoMFA) {
    try {
        const resp = await fetch('/api/auth/verificar-mfa', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({
                email: emailAtual,
                codigo_mfa: codigoMFA,
                session: sessaoAtual
            })
        });

        const dados = await resp.json();
        if (resp.ok) {
            processarResposta(dados);
        } else {
            alert(dados.detail || "Código MFA inválido ou expirado.");
        }
    } catch (err) {
        alert("Erro ao conectar com a API");
    }
}

function esconderTodosFormularios() {
    formLogin.style.display = 'none';
    formNovaSenha.style.display = 'none';
    formSetupMFA.style.display = 'none';
    formVerificaMFA.style.display = 'none';
}

function resetarFluxo() {
    esconderTodosFormularios();
    formLogin.style.display = 'block';
    sessaoAtual = null;
    emailAtual = null;
    
    document.getElementById('passwordInput').value = '';
    document.getElementById('novaSenhaInput').value = '';
    document.getElementById('confirmaSenhaInput').value = '';
    document.getElementById('codigoSetupInput').value = '';
    document.getElementById('codigoVerificaInput').value = '';
    document.getElementById('qrcode-container').innerHTML = ''; 
}