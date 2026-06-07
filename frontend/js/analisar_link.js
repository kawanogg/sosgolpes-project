document.getElementById('formularioAnaliseLink').addEventListener('submit', async function(e) {
    e.preventDefault();
    const url = document.getElementById('urlInput').value.trim();
    if (url) await executarAnalise(url);
});

async function executarAnalise(url) {
    document.getElementById('loadingOverlay').classList.remove('oculto');
    document.getElementById('painelResultado').classList.add('oculto');

    try {
        const resp = await fetch('/api/threats/analisar_link', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url }),
            credentials: 'include'
        });
        const dados = await resp.json();
        document.getElementById('loadingOverlay').classList.add('oculto');

        if (dados.status === 'erro') {
            mostrarErro(dados.mensagem);
            return;
        }
        mostrarResultado(dados);
    } catch (err) {
        document.getElementById('loadingOverlay').classList.add('oculto');
        mostrarErro('Erro ao comunicar com o servidor.');
    }
}

function mostrarResultado(dados) {
    const painel = document.getElementById('painelResultado');
    const cab = document.getElementById('cabecalhoResultado');
    const pts = Math.min(dados.pontuacao_risco, 100);

    cab.className = 'cabecalho-resultado';
    const cores = {
        'Malicioso': { classe: 'resultado-malicioso', cor: '#ef4444', titulo: 'MALICIOSO' },
        'Suspeito':  { classe: 'resultado-suspeito',  cor: '#f59e0b', titulo: 'SUSPEITO' },
        'Seguro':    { classe: 'resultado-seguro-link', cor: '#10b981', titulo: 'SEGURO' }
    };
    const cfg = cores[dados.nivel_perigo] || cores['Seguro'];

    cab.classList.add(cfg.classe);
    document.getElementById('tituloNivel').textContent = cfg.titulo;
    document.getElementById('resumoAnalise').textContent = dados.resumo;
    document.getElementById('valorRisco').textContent = pts + '/100';

    const barra = document.getElementById('barraRiscoPreenchimento');
    barra.style.width = pts + '%';
    barra.style.backgroundColor = cfg.cor;

    const detalhes = document.getElementById('detalhesAnalise');
    detalhes.innerHTML = '';

    for (const chave in dados.analises) {
        const a = dados.analises[chave];
        const div = document.createElement('div');
        div.className = 'secao-detalhe';

        const cabecalho = document.createElement('div');
        cabecalho.className = 'cabecalho-detalhe';

        const statusCor = a.status === 'ok' ? '#10b981' : '#f59e0b';

        const spanStatus = document.createElement('span');
        spanStatus.style.color = statusCor;
        spanStatus.style.fontSize = '1.2rem';
        spanStatus.innerHTML = a.status === 'ok' ? '&#10003;' : '&#9888;';

        const strong = document.createElement('strong');
        strong.textContent = a.nome;

        const spanPontuacao = document.createElement('span');
        spanPontuacao.className = 'pontuacao-detalhe';
        spanPontuacao.textContent = '+' + a.pontuacao + ' pts';

        cabecalho.append(spanStatus, document.createTextNode(' '), strong, spanPontuacao);
        div.appendChild(cabecalho);

        if (a.alertas) {
            const ul = document.createElement('ul');
            ul.className = 'lista-alertas';
            a.alertas.forEach(t => {
                const li = document.createElement('li');
                li.textContent = t;
                ul.appendChild(li);
            });
            div.appendChild(ul);
        }

        detalhes.appendChild(div);
    }

    painel.classList.remove('oculto');
    painel.scrollIntoView({ behavior: 'smooth' });
}

function mostrarErro(msg) {
    const painel = document.getElementById('painelResultado');
    document.getElementById('cabecalhoResultado').className = 'cabecalho-resultado resultado-malicioso';
    document.getElementById('tituloNivel').textContent = 'ERRO';
    document.getElementById('resumoAnalise').textContent = msg;
    document.getElementById('valorRisco').textContent = '-';
    document.getElementById('barraRiscoPreenchimento').style.width = '0%';
    document.getElementById('detalhesAnalise').innerHTML = '';
    painel.classList.remove('oculto');
}

// QR Code
const areaUpload = document.getElementById('areaUpload');
const qrFileInput = document.getElementById('qrFileInput');
let urlQR = '';

areaUpload.addEventListener('click', () => qrFileInput.click());
areaUpload.addEventListener('dragover', e => { e.preventDefault(); areaUpload.classList.add('drag-over'); });
areaUpload.addEventListener('dragleave', () => areaUpload.classList.remove('drag-over'));
areaUpload.addEventListener('drop', e => {
    e.preventDefault();
    areaUpload.classList.remove('drag-over');
    if (e.dataTransfer.files.length) processarQR(e.dataTransfer.files[0]);
});
qrFileInput.addEventListener('change', function() {
    if (this.files.length) processarQR(this.files[0]);
});

function processarQR(arquivo) {
    if (!arquivo.type.startsWith('image/')) {
        document.getElementById('resultadoQR').textContent = 'Selecione uma imagem valida.';
        document.getElementById('resultadoQR').className = 'caixa-resultado resultado-perigo';
        document.getElementById('resultadoQR').classList.remove('oculto');
        return;
    }

    const reader = new FileReader();
    reader.onload = e => {
        document.getElementById('imgPreview').src = e.target.result;
        document.getElementById('previewQR').classList.remove('oculto');
    };
    reader.readAsDataURL(arquivo);

    if (typeof Html5Qrcode === 'undefined') {
        document.getElementById('resultadoQR').textContent = 'Biblioteca QR nao carregada.';
        document.getElementById('resultadoQR').className = 'caixa-resultado resultado-perigo';
        document.getElementById('resultadoQR').classList.remove('oculto');
        return;
    }

    const qr = new Html5Qrcode("previewQR");
    qr.scanFile(arquivo, true)
        .then(texto => {
            urlQR = texto;
            const res = document.getElementById('resultadoQR');
            res.classList.remove('oculto');

            if (/^https?:\/\//i.test(texto) || /^www\./i.test(texto)) {
                res.innerHTML = '<strong>URL encontrada:</strong><br><code>' + esc(texto) + '</code>';
                res.className = 'caixa-resultado resultado-seguro';
                document.getElementById('btnAnalisarQR').classList.remove('oculto');
            } else {
                res.innerHTML = '<strong>Conteudo:</strong><br><code>' + esc(texto) + '</code><br><small>Nao e uma URL.</small>';
                res.className = 'caixa-resultado resultado-seguro';
                document.getElementById('btnAnalisarQR').classList.add('oculto');
            }
        })
        .catch(() => {
            document.getElementById('resultadoQR').textContent = 'Nao foi possivel ler o QR Code.';
            document.getElementById('resultadoQR').className = 'caixa-resultado resultado-perigo';
            document.getElementById('resultadoQR').classList.remove('oculto');
            document.getElementById('btnAnalisarQR').classList.add('oculto');
        });
}

document.getElementById('btnAnalisarQR').addEventListener('click', async () => {
    if (!urlQR) return;
    document.getElementById('urlInput').value = urlQR;
    await executarAnalise(urlQR);
});

function esc(t) {
    const d = document.createElement('div');
    d.textContent = t;
    return d.innerHTML;
}
