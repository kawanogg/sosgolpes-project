document.addEventListener('DOMContentLoaded', async function() {
    const menuNavegacao = document.getElementById('menuNavegacao');
    const isLoggedIn = localStorage.getItem('is_logged_in');
    const paginaAtual = window.location.pathname;

    let linksHTML = `
        <li><a href="/link_analysis" class="${paginaAtual === '/link_analysis' ? 'ativo' : ''}">Analisar Link</a></li>
        <li><a href="/password_checker" class="${paginaAtual === '/password_checker' ? 'ativo' : ''}">Auditoria de Senha</a></li>
    `;

    if (isLoggedIn === 'true') {
        linksHTML += `
            <li><a href="/user_profile" class="${paginaAtual === '/user_profile' ? 'ativo' : ''}">Meu Perfil</a></li>
            <li><a href="#" id="btnSairNav">Sair</a></li>
        `;
    } else {
        linksHTML += `
            <li><a href="/login" class="${paginaAtual === '/login' ? 'ativo' : ''}">Login</a></li>
            <li><a href="/register" class="${paginaAtual === '/register' ? 'ativo' : ''}">Cadastre-se</a></li>
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
    const isLoggedIn = localStorage.getItem('is_logged_in');
    
    if (isLoggedIn === 'true') {
        try {
            await fetch('/api/auth/logout', {
                method: 'GET',
            });
            localStorage.removeItem('is_logged_in');
        } catch (e) {
            console.warn("Não foi possível avisar o servidor, forçando logout local.");
        }
    }    
    window.location.href = '/login';
}