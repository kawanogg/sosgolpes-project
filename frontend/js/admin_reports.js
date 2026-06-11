let allReports = {
    'Pendente': [],
    'Analisando': [],
    'Confirmado': [],
    'Falso Positivo': []
};
let currentReportId = null;

function sanitizeInput(input) {
    if (!input) return '';
    return String(input)
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
        .replace(/'/g, '&#x27;')
        .replace(/\//g, '&#x2F;');
}

function showAlert(message, type = 'success') {
    const alertDiv = document.getElementById(`alert-${type}`);
    alertDiv.textContent = message;
    alertDiv.classList.add('show');
    setTimeout(() => {
        alertDiv.classList.remove('show');
    }, 5000);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('pt-BR', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit'
    });
}

async function loadAllReports() {
    if (localStorage.getItem('is_logged_in') !== 'true') {
        window.location.href = '/login';
        return;
    }

    document.getElementById('loading').style.display = 'block';

    try {
        const response = await fetch('/api/reports/all', {
            method: 'GET'
        });

        if (response.status === 401) {
            localStorage.removeItem('is_logged_in');
            window.location.href = '/login';
            return;
        }

        if (response.status === 403) {
            showAlert('Acesso restrito! Apenas administradores podem acessar.', 'error');
            window.location.href = '/';
            return;
        }

        if (!response.ok) throw new Error('Erro ao carregar relatórios');

        const data = await response.json();
        allReports = data.por_status;

        updateStats(data);
        displayAllReports();
    } catch (error) {
        console.error('Erro:', error);
        showAlert(`❌ Erro ao carregar denúncias: ${error.message}`, 'error');
    } finally {
        document.getElementById('loading').style.display = 'none';
    }
}

function updateStats(data) {
    const statsDiv = document.getElementById('stats');
    const porStatus = data.por_status;

    let html = `
        <div class="stat-card">
            <h3>Total de Denúncias</h3>
            <div class="number">${data.total}</div>
        </div>
        <div class="stat-card">
            <h3>Pendentes</h3>
            <div class="number">${porStatus['Pendente'].length}</div>
        </div>
        <div class="stat-card">
            <h3>Analisando</h3>
            <div class="number">${porStatus['Analisando'].length}</div>
        </div>
        <div class="stat-card">
            <h3>Confirmados</h3>
            <div class="number">${porStatus['Confirmado'].length}</div>
        </div>
        <div class="stat-card">
            <h3>Falsos Positivos</h3>
            <div class="number">${porStatus['Falso Positivo'].length}</div>
        </div>
    `;

    statsDiv.innerHTML = html;
}

function displayAllReports() {
    let todos = [];
    Object.values(allReports).forEach(arr => {
        todos = todos.concat(arr);
    });
    displayReports(todos);
}

function displayReports(reports) {
    const container = document.getElementById('reports-container');

    if (reports.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <p>📭 Nenhuma denúncia encontrada</p>
            </div>
        `;
        return;
    }

    let html = '';
    reports.forEach(report => {
        const statusClass = `status-${report.status.toLowerCase().replace(/ /g, '-')}`;
        const dataFormatada = formatDate(report.data_denuncia);

        html += `
            <div class="report-card">
                <div class="report-header">
                    <div class="report-link">
                        <strong>Link Denunciado:</strong>
                        <code>${sanitizeInput(report.link_denunciado)}</code>
                    </div>
                    <span class="status-badge ${statusClass}">${report.status}</span>
                </div>

                <div class="report-meta">
                    <span>📌 <strong>Tipo:</strong> ${sanitizeInput(report.tipo_golpe)}</span>
                    <span>👤 <strong>Denunciante:</strong> ${sanitizeInput(report.email_denunciante)}</span>
                    <span>📅 <strong>Data:</strong> ${dataFormatada}</span>
                    <span>🌐 <strong>IP:</strong> ${sanitizeInput(report.endereco_ip)}</span>
                </div>

                ${report.comentarios ? `
                    <div class="report-comments">
                        <strong>Comentários:</strong>
                        <p>${sanitizeInput(report.comentarios)}</p>
                    </div>
                ` : ''}

                <div class="report-actions">
                    <button class="btn btn-sm btn-info" onclick="openStatusModal(${report.id_denuncia})">
                        Atualizar Status
                    </button>
                    <button class="btn btn-sm btn-danger" onclick="deleteReport(${report.id_denuncia})">
                        Deletar
                    </button>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
}

function filterReports() {
    const statusFilter = document.getElementById('filterStatus').value;
    const searchBox = document.getElementById('searchBox').value.toLowerCase();

    let reportsToFilter = [];

    if (statusFilter) {
        reportsToFilter = allReports[statusFilter] || [];
    } else {
        Object.values(allReports).forEach(arr => {
            reportsToFilter = reportsToFilter.concat(arr);
        });
    }

    if (searchBox) {
        reportsToFilter = reportsToFilter.filter(report =>
            report.link_denunciado.toLowerCase().includes(searchBox) ||
            (report.email_denunciante || '').toLowerCase().includes(searchBox) ||
            report.tipo_golpe.toLowerCase().includes(searchBox)
        );
    }

    displayReports(reportsToFilter);
}

function openStatusModal(reportId) {
    currentReportId = reportId;
    document.getElementById('statusModal').classList.add('show');
}

function closeModal() {
    document.getElementById('statusModal').classList.remove('show');
    currentReportId = null;
}

async function updateReportStatus() {
    const newStatus = document.getElementById('newStatus').value;

    try {
        const response = await fetch(`/api/reports/${currentReportId}/status`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ status: newStatus })
        });

        if (response.status === 401) {
            localStorage.removeItem('is_logged_in');
            window.location.href = '/login';
            return;
        }

        if (!response.ok) throw new Error('Erro ao atualizar status');

        showAlert('✅ Status atualizado com sucesso!', 'success');
        closeModal();
        loadAllReports();
    } catch (error) {
        showAlert(`❌ Erro: ${error.message}`, 'error');
    }
}

async function deleteReport(reportId) {
    if (!confirm('Tem certeza que quer deletar esta denúncia?')) return;

    try {
        const response = await fetch(`/api/reports/${reportId}`, {
            method: 'DELETE'
        });

        if (response.status === 401) {
            localStorage.removeItem('is_logged_in');
            window.location.href = '/login';
            return;
        }

        if (!response.ok) throw new Error('Erro ao deletar denúncia');

        showAlert('✅ Denúncia removida!', 'success');
        loadAllReports();
    } catch (error) {
        showAlert(`❌ Erro: ${error.message}`, 'error');
    }
}

function reloadReports() {
    loadAllReports();
}

document.addEventListener('DOMContentLoaded', () => {
    loadAllReports();
});

window.onclick = function(event) {
    const modal = document.getElementById('statusModal');
    if (event.target === modal) {
        closeModal();
    }
};
