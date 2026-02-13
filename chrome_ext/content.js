window.addEventListener("message", (event) => {
  if (event.origin !== window.location.origin) return;

  const msg = event.data;
  if (!msg) return;

  if (msg.type === "XSIST_DOWNLOAD") {
    chrome.runtime.sendMessage(
      { type: "XSIST_DOWNLOAD", tipo: msg.tipo, chave: msg.chave },
      (resp) => {
        // sempre mostra mensagem quando falhar
        if (!resp || resp.ok !== true) {
          const m = (resp && resp.msg) ? resp.msg : "Falha (sem resposta do conector).";
          alert("XSist: " + m);
        }
      }
    );
    return;
  }

  if (msg.type === "XSIST_DOWNLOAD_BATCH") {
    chrome.runtime.sendMessage(
      { type: "XSIST_DOWNLOAD_BATCH", tipo: msg.tipo, chaves: msg.chaves, batchId: msg.batchId },
      (resp) => {
        if (!resp || resp.ok !== true) {
          const m = (resp && resp.msg) ? resp.msg : "Falha no lote (sem resposta).";
          alert("XSist: " + m);
        }
      }
    );
  }
});