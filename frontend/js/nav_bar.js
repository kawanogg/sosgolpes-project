document.addEventListener('DOMContentLoaded', async function() {
    const menuNavegacao = document.getElementById('menuNavegacao');
    const token = localStorage.getItem('access_token');
    const paginaAtual = window.location.pathname;

    let linksHTML = `
        <li><a href="/link_analysis" class="${paginaAtual.includes('link_analysis') ? 'ativo' : ''}">Analisar Link</a></li>
        <li><a href="/password_checker" class="${paginaAtual.includes('password_checker') ? 'ativo' : ''}">Auditoria de Senha</a></li>
    `;

    if (token) {
        linksHTML += `
            <li><a href="/user_profile" class="${paginaAtual.includes('user_profile') ? 'ativo' : ''}">Meu Perfil</a></li>
            <li><a href="#" id="btnSairNav">Sair</a></li>
        `;
    } else {
        linksHTML += `
            <li><a href="/login" class="${paginaAtual.includes('login') ? 'ativo' : ''}">Login</a></li>
            <li><a href="/register" class="${paginaAtual.includes('register') ? 'ativo' : ''}">Cadastre-se</a></li>
        `;
    }

    if (menuNavegacao) {
        menuNavegacao.innerHTML = linksHTML;
    }

    const btnSair = document.getElementById('btnSairNav');
    if (btnSair) {
        btnSair.addEventListener('click', (e) => {
            e.preventDefault(); // Evita que o link tente mudar de página
            realizarLogout();
        });
    }
})


async function realizarLogout() {
    const token = localStorage.getItem('access_token');
    
    if (token) {
        try {
            await fetch('/api/auth/logout', {
                method: 'POST',
                headers: { 'Authorization': `Bearer ${token}` }
            });
        } catch (e) {
            console.warn("Não foi possível avisar o servidor, forçando logout local.");
        }
    }

    localStorage.removeItem('access_token');
    localStorage.removeItem('id_token');
    localStorage.removeItem('refresh_token');
    
    window.location.href = '/login';
}