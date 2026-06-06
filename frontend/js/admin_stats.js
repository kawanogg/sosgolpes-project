fetch('/api/admin/admin_stats', { credentials: 'include' })
    .then(res => {
        if (res.status === 401) {
            window.location.href = '/login';
            return null;
        }
        return res.json();
    })
    .then(data => {
        if (!data) return;
        if(data.status === 'sucesso') {
            document.getElementById('stat-usuarios').textContent = data.stats.usuarios;
            document.getElementById('stat-analises').textContent = data.stats.analises;
            document.getElementById('stat-leaks').textContent = data.stats.leaks;
            document.getElementById('stat-logs').textContent = data.stats.logs;

            const threatCounts = {
                Seguro: 0,
                Suspeito: 0,
                Malicioso: 0,
            };

            if (Array.isArray(data.perigo_stats)) {
                data.perigo_stats.forEach(stat => {
                    if (threatCounts.hasOwnProperty(stat.nivel_perigo)) {
                        threatCounts[stat.nivel_perigo] = stat.count;
                    }
                });
            }

            // Preencher contadores de tipos de testes
            if (data.teste_tipos) {
                document.getElementById('stat-testes-senhas').textContent = data.teste_tipos.senhas + ' testes';
                document.getElementById('stat-testes-links').textContent = data.teste_tipos.links + ' testes';
                document.getElementById('stat-testes-qr').textContent = data.teste_tipos.qr_codes + ' testes';
            }

            // Preencher status de senhas
            if (data.senha_status) {
                document.getElementById('stat-senhas-seguras').textContent = data.senha_status.seguras + ' senhas';
                document.getElementById('stat-senhas-vazadas').textContent = data.senha_status.vazadas + ' senhas';
            }

            document.getElementById('stat-resultado-seguro').textContent = threatCounts.Seguro + ' análises';
            document.getElementById('stat-resultado-suspeito').textContent = threatCounts.Suspeito + ' análises';
            document.getElementById('stat-resultado-malicioso').textContent = threatCounts.Malicioso + ' análises';

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