let editMode = false;

function carregarLista() {
    fetch('/api/admin/leaks')
        .then(res => res.json())
        .then(data => {
            const tbody = document.getElementById('tabela-leaks');
            tbody.innerHTML = '';
            data.forEach(reg => {
                const tr = document.createElement('tr');

                const tdId = document.createElement('td');
                tdId.textContent = reg.id_leak;

                const tdHash = document.createElement('td');
                tdHash.textContent = reg.senha_vazada_hash.substring(0, 20) + '...';
                tdHash.title = reg.senha_vazada_hash;

                const tdFonte = document.createElement('td');
                tdFonte.textContent = reg.fonte_vazamento;

                const tdAcao = document.createElement('td');
                const btnEdit = document.createElement('button');
                btnEdit.textContent = 'Editar';
                btnEdit.style.marginRight = '8px';
                btnEdit.addEventListener('click', () => preencherFormulario(reg));

                const btnDelete = document.createElement('button');
                btnDelete.textContent = 'Deletar';
                btnDelete.addEventListener('click', () => deletarRegistro(reg.id_leak));

                tdAcao.append(btnEdit, btnDelete);
                tr.append(tdId, tdHash, tdFonte, tdAcao);
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar lista de vazamentos:', error);
        });
}

function preencherFormulario(reg) {
    editMode = true;
    document.getElementById('id_leak').value = reg.id_leak;
    document.getElementById('senha_hash').value = reg.senha_vazada_hash;
    document.getElementById('fonte').value = reg.fonte_vazamento;
    document.getElementById('formTitulo').textContent = 'Editar Registro';
    document.getElementById('btnSubmit').textContent = 'Salvar alteração';
    document.getElementById('btnCancelEdit').style.display = 'inline-block';
}

function resetForm() {
    editMode = false;
    document.getElementById('id_leak').value = '';
    document.getElementById('formAddLeak').reset();
    document.getElementById('formTitulo').textContent = 'Adicionar Registro';
    document.getElementById('btnSubmit').textContent = 'Adicionar';
    document.getElementById('btnCancelEdit').style.display = 'none';
}

document.getElementById('formAddLeak').addEventListener('submit', function(e) {
    e.preventDefault();
    const idLeak = document.getElementById('id_leak').value;
    const payload = {
        senha_hash: document.getElementById('senha_hash').value,
        fonte: document.getElementById('fonte').value
    };

    const method = editMode ? 'PUT' : 'POST';
    const url = editMode ? `/api/admin/leaks/${idLeak}` : '/api/admin/leaks';

    fetch(url, {
        method: method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(async response => {
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Erro ao processar requisicao.');
        }
        return response.json();
    }).then(data => {
        resetForm();
        carregarLista();
        mostrarMensagem(data.mensagem || 'Operacao concluida com sucesso.');
    }).catch(error => {
        console.error('Erro ao enviar formulario:', error);
        mostrarMensagem(error.message, true);
    });
});

document.getElementById('btnCancelEdit').addEventListener('click', function() {
    resetForm();
});

function deletarRegistro(id) {
    if (confirm('Tem certeza?')) {
        fetch(`/api/admin/leaks/${id}`, {
            method: 'DELETE'
        }).then(async response => {
            if (!response.ok) {
                const error = await response.json();
                throw new Error(error.detail || 'Erro ao deletar registro.');
            }
            return response.json();
        }).then(data => {
            carregarLista();
            mostrarMensagem(data.mensagem || 'Registro deletado com sucesso.');
        }).catch(error => {
            console.error('Erro ao deletar registro:', error);
            mostrarMensagem(error.message, true);
        });
    }
}

function mostrarMensagem(texto, isError = false) {
    const mensagem = document.getElementById('mensagem');
    mensagem.textContent = texto;
    mensagem.style.color = isError ? 'red' : 'green';
    setTimeout(() => {
        mensagem.textContent = '';
    }, 5000);
}

carregarLista();