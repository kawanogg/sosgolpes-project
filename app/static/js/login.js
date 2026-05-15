document.getElementById('formularioLogin').addEventListener('submit', async function(e) {
    e.preventDefault();

    const chave = await crypto.subtle.generateKey(
        { name: "AES-GCM", length: 256},
        true,
        ["encrypt", "decrypt"]
    );

    const email = document.getElementById('emailInput').value.trim();
    const senha = await window.crypto.subtle.encrypt(
        { name: "AES-GCM", iv: window.crypto.getRandomValues(new Uint8Array(12)) },
        chave,
        new TextEncoder().encode(document.getElementById('passwordInput').value.trim())
    );
})

async function recebeChave() {
    return;
}