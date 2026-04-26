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

                const tdFonte = document.createElement('td');
                tdFonte.textContent = reg.fonte_vazamento;

                const tdAcao = document.createElement('td');
                const btn = document.createElement('button');
                btn.textContent = 'Deletar';
                btn.addEventListener('click', () => deletarRegistro(reg.id_leak));
                tdAcao.appendChild(btn);

                tr.append(tdId, tdHash, tdFonte, tdAcao);
                tbody.appendChild(tr);
            });
        })
        .catch(error => {
            console.error('Erro ao carregar lista de vazamentos:', error);
        });
}

document.getElementById('formAddLeak').addEventListener('submit', function(e) {
    e.preventDefault();
    const payload = {
        action: 'add',
        senha_hash: document.getElementById('senha_hash').value,
        fonte: document.getElementById('fonte').value
    };

    fetch('/api/admin_crud', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
    }).then(() => {
        document.getElementById('formAddLeak').reset();
        carregarLista();
    }).catch(error => {
        console.error('Erro ao adicionar registro:', error);
    });
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