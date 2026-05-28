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

                const tdData = document.createElement('td');
                tdData.textContent = log.data_hora;

                const tdNome = document.createElement('td');
                tdNome.textContent = log.nome || 'Anônimo';

                const tdAcao = document.createElement('td');
                tdAcao.textContent = log.acao_realizada;

                const tdIp = document.createElement('td');
                tdIp.textContent = log.endereco_ip;

                tr.append(tdData, tdNome, tdAcao, tdIp);
                tbody.appendChild(tr);
            });
        }
    })
    .catch(error => {
        console.error('Erro ao buscar estatísticas:', error);
    });