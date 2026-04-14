document.getElementById('formularioAuditoriaSenha').addEventListener('submit', async function(evento) {
    evento.preventDefault();

    const inputSenha = document.getElementById('senha');
    const senhaClara = inputSenha.value;

    try {
        const respostaChave = await fetch('/main/php/chave_publica.php');
        if (!respostaChave.ok) {
            throw new Error('Nao foi possivel obter a chave publica.');
        }
        const pemChavePublica = await respostaChave.text();

        const senhaCriptografada = await criptografarRSA(senhaClara, pemChavePublica);
        document.getElementById('carga_criptografada').value = senhaCriptografada;
        
        const dados = {
            carga_criptografada: senhaCriptografada
        };

        const resposta = await fetch('/main/php/processar_senha.php', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json', 
            },
            body: JSON.stringify(dados)
        });

        const resultadoJson = await resposta.json();
        const divResultado = document.getElementById('resultadoAuditoria');

        divResultado.className = 'caixa-resultado';
        divResultado.textContent = resultadoJson.mensagem;
        divResultado.classList.remove('oculto');

        if (resultadoJson.status === 'seguro') {
            divResultado.classList.add('resultado-seguro');
        } else if (resultadoJson.status === 'perigo') {
            divResultado.classList.add('resultado-perigo');
        } else {
            divResultado.classList.add('resultado-perigo');
        }

        inputSenha.value = '';

    } catch (erro) {
        console.error("Erro de criptografia:", erro);
        alert("Falha na camada de seguranca. Por favor, recarregue a pagina.");
    }
});

async function criptografarRSA(texto, pem) {
    const conteudoPem = pem
        .replace('-----BEGIN PUBLIC KEY-----', '')
        .replace('-----END PUBLIC KEY-----', '')
        .replace(/\s/g, '');
    
    const stringBinaria = window.atob(conteudoPem);
    const bytesBinarios = new Uint8Array(stringBinaria.length);
    for (let i = 0; i < stringBinaria.length; i++) {
        bytesBinarios[i] = stringBinaria.charCodeAt(i);
    }

    const chavePublica = await window.crypto.subtle.importKey(
        "spki",
        bytesBinarios.buffer,
        { name: "RSA-OAEP", hash: "SHA-1" },
        true,
        ["encrypt"]
    );

    const textoCodificado = new TextEncoder().encode(texto);
    const bufferCriptografado = await window.crypto.subtle.encrypt(
        { name: "RSA-OAEP" },
        chavePublica,
        textoCodificado
    );

    const bytesCriptografados = new Uint8Array(bufferCriptografado);
    let resultadoBase64 = "";
    for (let i = 0; i < bytesCriptografados.byteLength; i++) {
        resultadoBase64 += String.fromCharCode(bytesCriptografados[i]);
    }
    return window.btoa(resultadoBase64);
}
