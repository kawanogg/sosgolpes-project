const TIPOS_GOLPE = [
    'Phishing',
    'Quishing',
    'Malware',
    'Ransomware',
    'Fraude',
    'Clonagem de Site',
    'Outro'
];

function isValidUrl(string) {
    try {
        new URL(string);
        return true;
    } catch (_) {
        return false;
    }
}

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

async function submitReport(event) {
    event.preventDefault();

    const link = document.getElementById('link').value.trim();
    const tipo_golpe = document.getElementById('tipo_golpe').value;
    const comentarios = document.getElementById('comentarios').value.trim();

    if (!link) {
        showAlert('Por favor, preencha o link.', 'error');
        return;
    }

    if (!isValidUrl(link)) {
        showAlert('URL inválida. Inclua http:// ou https://', 'error');
        return;
    }

    if (!tipo_golpe) {
        showAlert('Por favor, selecione um tipo de golpe.', 'error');
        return;
    }

    document.getElementById('loading').classList.add('show');

    try {
        const response = await fetch('/api/reports/create', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                link: link,
                tipo_golpe: tipo_golpe,
                comentarios: comentarios
            })
        });

        document.getElementById('loading').classList.remove('show');

        if (response.ok) {
            showAlert('✅ Denúncia enviada com sucesso! Obrigado por ajudar a comunidade.', 'success');
            document.getElementById('reportForm').reset();
        } else {
            const error = await response.json();
            showAlert(`❌ Erro: ${error.detail || 'Falha ao enviar denúncia'}`, 'error');
        }
    } catch (error) {
        document.getElementById('loading').classList.remove('show');
        showAlert(`❌ Erro de conexão: ${error.message}`, 'error');
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const myReportsSection = document.getElementById('myReportsSection');
    if (myReportsSection) {
        myReportsSection.style.display = 'none';
    }
});
