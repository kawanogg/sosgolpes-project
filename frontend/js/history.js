document.addEventListener('DOMContentLoaded', async function () {
    const container = document.getElementById('historicoContainer');
    const tabela = document.getElementById('tabelaHistorico');
    const corpo = document.getElementById('corpoTabelaHistorico');
    const carregando = document.getElementById('historicoCarregando');
    const vazio = document.getElementById('historicoVazio');

    try {
        const response = await fetch('/api/user/history', {
            method: 'GET',
            credentials: 'include'
        });

        if (response.status === 401) {
            window.location.href = '/login';
            return;
        }

        if (!response.ok) {
            throw new Error('Erro ao buscar histórico.');
        }

        const dados = await response.json();
        carregando.classList.add('oculto');

        if (!dados.historico || dados.historico.length === 0) {
            vazio.classList.remove('oculto');
            return;
        }

        tabela.classList.remove('oculto');

        dados.historico.forEach(item => {
            const tr = document.createElement('tr');

            const tdData = document.createElement('td');
            tdData.textContent = formatarData(item.data);

            const tdUrl = document.createElement('td');
            tdUrl.textContent = item.url;
            tdUrl.classList.add('celula-url');

            const tdNivel = document.createElement('td');
            const badge = document.createElement('span');
            badge.textContent = item.nivel;
            badge.classList.add('badge-nivel', `badge-${item.nivel.toLowerCase()}`);
            tdNivel.appendChild(badge);

            const tdPontuacao = document.createElement('td');
            let pontuacao = '-';
            try {
                const detalhes = JSON.parse(item.detalhes);
                pontuacao = detalhes.pontuacao_risco + '/100';
            } catch (e) { }
            tdPontuacao.textContent = pontuacao;

            tr.appendChild(tdData);
            tr.appendChild(tdUrl);
            tr.appendChild(tdNivel);
            tr.appendChild(tdPontuacao);
            corpo.appendChild(tr);
        });
    } catch (err) {
        carregando.textContent = 'Erro ao carregar histórico. Tente novamente mais tarde.';
        console.error(err);
    }
});

function formatarData(isoString) {
    if (!isoString) return '-';
    const d = new Date(isoString);
    return d.toLocaleDateString('pt-BR') + ' ' + d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' });
}
