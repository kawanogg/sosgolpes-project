document.getElementById('formularioAuditoriaSenha').addEventListener('submit', async function(evento) {
    evento.preventDefault();

    const inputSenha = document.getElementById('senha');
    const senhaClara = inputSenha.value;

    try {
        let respostaChave = await fetch('/api/threats/chave_publica');        

        if (!respostaChave.ok && respostaChave.status === 404) {
            respostaChave = await fetch('/api/threats/chave_publica');
        }

        if (!respostaChave.ok) {
            throw new Error('Não foi possível obter a chave pública.');
        }
        const pemChavePublica = await respostaChave.text();

        const criptografia = new JSEncrypt();
        criptografia.setPublicKey(pemChavePublica);
        const senhaCriptografada = criptografia.encrypt(senhaClara);
        
        if (!senhaCriptografada) {
            throw new Error('Falha ao criptografar a senha.');
        }

        document.getElementById('carga_criptografada')
        
        const dados = {
            dadosCriptografados: senhaCriptografada
        };

        let resposta = await fetch('/api/threats/processar_senha', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', 
            },
            body: JSON.stringify(dados)
        });

        if (!resposta.ok && resposta.status === 404) {
            resposta = await fetch('/api/threats/processar_senha', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json', 
                },
                body: JSON.stringify(dados)
            });
        }

        const resultadoJson = await resposta.json();
        const divResultado = document.getElementById('resultadoAuditoria');

        divResultado.className = 'caixa-resultado';
        divResultado.textContent = resultadoJson.mensagem;
        divResultado.classList.remove('oculto');

        if (resultadoJson.status === 'seguro') {
            divResultado.classList.add('resultado-seguro');
        } else {
            divResultado.classList.add('resultado-perigo');
        }

        inputSenha.value = '';

    } catch (erro) {
        console.error("Erro de criptografia:", erro);
        alert("Falha na camada de segurança. Por favor, recarregue a página.");
    }
}); 