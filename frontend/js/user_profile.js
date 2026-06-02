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
                const pNome = document.createElement("p");
                pNome.innerHTML = "<strong>Nome: </strong>";
                pNome.appendChild(document.createTextNode(dados.nome));

                const pEmail = document.createElement("p");
                pEmail.innerHTML = "<strong>Email: </strong>";
                pEmail.appendChild(document.createTextNode(dados.email));

                perfil.appendChild(pNome);
                perfil.appendChild(pEmail);
            } else {
                alert("Erro ao carregar o perfil do usuário.");
            }
        } catch (erro) {
            console.error("Erro ao conectar com a API:", erro);
        }
    }
});