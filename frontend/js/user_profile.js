document.addEventListener('DOMContentLoaded', async function() {
    const token = localStorage.getItem('access_token');

    if (!token) {
        window.location.href = "http://localhost:8080/";
    } else {
        const perfil = document.getElementById("perfilUser");
        try {
            const response = await fetch("/api/user/profile", {
                method: 'GET',
                headers: {
                    'Authorization': `Bearer ${token}`,
                    'Content-Type': 'application/json'
                }
            });

            if (response.status === 401 || response.status === 403) {
                console.warn("Sessão inválida ou expirada. Refaça o login.");
                localStorage.removeItem('access_token');
                window.location.href = '/login';
                return;
            }

            const dados = await response.json();
            
            if (dados.status === "sucesso") {
                let user_info_html = `
                    <p><strong>Nome:</strong> ${dados.nome}</p>
                    <p><strong>Email:</strong> ${dados.email}</p>
                `;
                perfil.innerHTML += user_info_html;
            } else {
                alert("Erro ao carregar o perfil do usuário.");
            }
        } catch (erro) {
            console.error("Erro ao conectar com a API:", erro);
        }
    }
});