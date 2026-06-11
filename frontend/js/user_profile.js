document.addEventListener('DOMContentLoaded', async function() {
    const isLoggedIn = localStorage.getItem('is_logged_in');

    if (isLoggedIn != 'true') {
        window.location.href = "/";
    } else {
        try {
            const response = await fetch("/api/user/profile", {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json'
                }
            });

            if (response.status === 401 || response.status === 403) {
                console.warn("Sessão inválida ou expirada. Refaça o login.");
                localStorage.removeItem('is_logged_in');
                return;
            }

            const dados = await response.json();
            
            if (dados.status === "sucesso") {
                const perfil = document.getElementById("perfilUser");

                const pNome = document.createElement("p");
                pNome.innerHTML = "<strong>Nome: </strong>";
                pNome.appendChild(document.createTextNode(dados.nome));

                const pEmail = document.createElement("p");
                pEmail.innerHTML = "<strong>Email: </strong>";
                pEmail.appendChild(document.createTextNode(dados.email));

                const buttonEdit = document.createElement("button");
                buttonEdit.type = "button";
                buttonEdit.classList.add("botao");
                buttonEdit.classList.add("botao-primario");
                buttonEdit.textContent = "Editar perfil";
                buttonEdit.addEventListener("click", () => {
                    document.getElementById('perfilUser').style.display = 'none';
                    document.getElementById('formularioEdicaoPerfil').style.display = 'block';
                })

                perfil.appendChild(pNome);
                perfil.appendChild(pEmail);
                perfil.appendChild(buttonEdit);
            } else {
                alert("Erro ao carregar o perfil do usuário.");
            }
        } catch (erro) {
            console.error("Erro ao conectar com a API:", erro);
        }
    }
});

document.getElementById('btnEdicaoPerfil').addEventListener('submit', async function (e) {
    e.preventDefault();

    const novoNome = document.getElementById("nomeEditInput").value.trim();
    const novoSobrenome = document.getElementById("sobrenomeEditInput").value.trim()

    if (novoNome) editaPerfil(novoNome, novoSobrenome);
});

async function editaPerfil(nome, sobrenome) {
    try {
        const resp = await fetch('api/user/editar_perfil', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json'},
            body: JSON.stringify({
                nome: nome,
                sohbrenome: sobrenome
            })
        });

        const dados = await resp.json();
    }
    catch {
        console.log("Erro ao conectar com a API");
    }
}