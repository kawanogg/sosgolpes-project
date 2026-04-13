document.getElementById('formularioAuditoriaSenha').addEventListener('submit', async function(evento) {
    const inputSenha = document.getElementById('senha');
    const senhaClara = inputSenha.value;
    const pemChavePublica = document.getElementById('chavePublica').value;

    try {
        const senhaCriptografada = await criptografarRSA(senhaClara, pemChavePublica);
        document.getElementById('carga_criptografada').value = senhaCriptografada;
        
        const dados = {
            carga_criptografada: senhaCriptografada
        };

        const resposta = await fetch('/processar_senha.php', {
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
        console.error("Erro na rotina de criptografia:", erro);
        alert("Falha na camada de segurança. Por favor, recarregue a página.");
    }
});

async function criptografarRSA(texto, pem) {
    const cabecalho = "-----BEGIN PUBLIC KEY-----";
    const rodape = "-----END PUBLIC KEY-----";
    const conteudoPem = pem.substring(cabecalho.length, pem.length - rodape.length).replace(/\s/g, '');
    
    const stringBinaria = window.atob(conteudoPem);
    const bytesBinarios = new Uint8Array(stringBinaria.length);
    for (let i = 0; i < stringBinaria.length; i++) {
        bytesBinarios[i] = stringBinaria.charCodeAt(i);
    }

    const chavePublica = await window.crypto.subtle.importKey(
        "spki",
        bytesBinarios.buffer,
        { name: "RSA-OAEP", hash: "SHA-256" },
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