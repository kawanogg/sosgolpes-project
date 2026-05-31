let editMode = false;

function carregarLista() {
    fetch('/api/admin_crud')
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
    const payload = {
        action: editMode ? 'edit' : 'add',
        senha_hash: document.getElementById('senha_hash').value,
        fonte: document.getElementById('fonte').value
    };

    if (editMode) {
        payload.id = document.getElementById('id_leak').value;
    }

    fetch('/api/admin_crud', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(() => {
        resetForm();
        carregarLista();
    }).catch(error => {
        console.error('Erro ao enviar formulário:', error);
    });
});

document.getElementById('btnCancelEdit').addEventListener('click', function() {
    resetForm();
});

function deletarRegistro(id) {
    if(confirm('Tem certeza?')) {
        fetch('/api/admin_crud', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ action: 'delete', id: id })
        }).then(() => carregarLista())
        .catch(error => {
            console.error('Erro ao deletar registro:', error);
        });
    }
}
carregarLista();