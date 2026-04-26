fetch('/api/admin_stats')
    .then(res => res.json())
    .then(data => {
        if(data.status === 'sucesso') {
            document.getElementById('stat-usuarios').textContent = data.stats.usuarios;
            document.getElementById('stat-analises').textContent = data.stats.analises;
            document.getElementById('stat-leaks').textContent = data.stats.leaks;
            document.getElementById('stat-logs').textContent = data.stats.logs;

            const tbody = document.getElementById('logs-tbody');
            data.logs.forEach(log => {
                const tr = document.createElement('tr');
                tr.innerHTML = `<td>${log.data_hora}</td><td>${log.nome || 'Anônimo'}</td><td>${log.acao_realizada}</td><td>${log.endereco_ip}</td>`;
                tbody.appendChild(tr);
            });
        }
    })
    .catch(error => {
        console.error('Erro ao buscar estatísticas:', error);
    });
