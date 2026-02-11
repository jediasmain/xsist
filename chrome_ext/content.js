function setLS(key, valueObj) {
  try {
    localStorage.setItem(key, JSON.stringify(valueObj));
  } catch (e) {}
}

async function refreshConnectorStatus() {
  chrome.runtime.sendMessage({ type: "XSIST_GET_CONNECTOR_STATUS" }, (resp) => {
    if (resp && resp.ok) {
      setLS("xsist_connector_status", { ok: true, ts: Date.now(), data: resp.data });
    } else {
      setLS("xsist_connector_status", { ok: false, ts: Date.now(), msg: (resp && resp.msg) ? resp.msg : "Sem resposta" });
    }
  });
}

// Marca que a extensão está instalada nesta página
setLS("xsist_extension_info", { ok: true, ts: Date.now(), version: "1.0.0" });

// Ao carregar a página, já tenta atualizar status do conector
refreshConnectorStatus();

// Recebe comandos do site (postMessage) e encaminha para o background
window.addEventListener("message", (event) => {
  if (event.origin !== window.location.origin) return;

  const msg = event.data;
  if (!msg) return;

  // pedir atualização do status (botão "Atualizar" no site)
  if (msg.type === "XSIST_REFRESH_STATUS") {
    refreshConnectorStatus();
    return;
  }

  // DOWNLOAD ÚNICO
  if (msg.type === "XSIST_DOWNLOAD") {
    chrome.runtime.sendMessage(
      { type: "XSIST_DOWNLOAD", tipo: msg.tipo, chave: msg.chave },
      (resp) => {
        try { localStorage.setItem("xsist_last", JSON.stringify(resp)); } catch (e) {}
        if (!resp || resp.ok !== true) {
          alert("XSist: " + ((resp && resp.msg) ? resp.msg : "Falha (sem resposta)"));
        }
      }
    );
    return;
  }

  // DOWNLOAD EM LOTE
  if (msg.type === "XSIST_DOWNLOAD_BATCH") {
    chrome.runtime.sendMessage(
      { type: "XSIST_DOWNLOAD_BATCH", tipo: msg.tipo, chaves: msg.chaves, batchId: msg.batchId },
      (resp) => {
        try { localStorage.setItem("xsist_last_batch", JSON.stringify(resp)); } catch (e) {}
        if (!resp) alert("XSist: Falha (sem resposta do lote).");
      }
    );
  }
});

// Recebe progresso enviado pelo background e grava no localStorage
chrome.runtime.onMessage.addListener((msg) => {
  if (!msg || msg.type !== "XSIST_PROGRESS") return;

  try {
    localStorage.setItem("xsist_progress", JSON.stringify(msg));
  } catch (e) {}

  if (msg.mode === "batch" && msg.status === "done") {
    alert(`XSist: Lote finalizado. OK=${msg.okCount} | ERRO=${msg.errCount}`);
  }
});