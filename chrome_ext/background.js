function onlyDigits(s) {
  return String(s || "").replace(/\D/g, "");
}

function normalizeFolder(folder) {
  folder = String(folder || "").trim();
  folder = folder.replace(/^[/\\]+/, "").replace(/[/\\]+$/, "");
  return folder;
}

async function getSettings() {
  const defaults = { saveAs: true, folder: "XSist" };
  const stored = await chrome.storage.local.get(["saveAs", "folder"]);
  return {
    saveAs: typeof stored.saveAs === "boolean" ? stored.saveAs : defaults.saveAs,
    folder: stored.folder ? stored.folder : defaults.folder
  };
}

async function downloadOne(tipo, chave, cfg) {
  const payload = { tipo, chave };

  const r = await fetch("http://127.0.0.1:8765/download", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload)
  });

  const data = await r.json();

  if (!data.ok || !data.xml) {
    return { ok: false, msg: data.msg || "Falha no conector" };
  }

  const ch = onlyDigits(chave);
  const baseName = `${tipo}_${ch}.xml`;

  const folder = normalizeFolder(cfg.folder);
  const filename = folder ? `${folder}/${baseName}` : baseName;

  const blob = new Blob([data.xml], { type: "application/xml" });
  const url = URL.createObjectURL(blob);

  await new Promise((resolve) => {
    chrome.downloads.download(
      { url, filename, saveAs: cfg.saveAs },
      () => resolve()
    );
  });

  setTimeout(() => URL.revokeObjectURL(url), 5000);

  return { ok: true, msg: "Download disparado.", filename };
}

async function sendToTab(tabId, message) {
  if (!tabId) return;
  try {
    await chrome.tabs.sendMessage(tabId, message);
  } catch (e) {
    // se não tiver content script na aba, ignora
  }
}

chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  (async () => {
    try {
      const cfg = await getSettings();
      const tabId = sender && sender.tab ? sender.tab.id : null;

      // ÚNICO
      if (msg && msg.type === "XSIST_DOWNLOAD") {
        const resp = await downloadOne(msg.tipo, msg.chave, cfg);
        // manda "último resultado" pra página também
        await sendToTab(tabId, { type: "XSIST_PROGRESS", mode: "single", resp });
        sendResponse(resp);
        return;
      }

      // LOTE
      if (msg && msg.type === "XSIST_DOWNLOAD_BATCH") {
        const tipo = msg.tipo;
        const chaves = Array.isArray(msg.chaves) ? msg.chaves : [];
        const batchId = msg.batchId || String(Date.now());

        let okCount = 0;
        let errCount = 0;

        await sendToTab(tabId, {
          type: "XSIST_PROGRESS",
          mode: "batch",
          batchId,
          status: "start",
          total: chaves.length,
          okCount,
          errCount
        });

        for (let i = 0; i < chaves.length; i++) {
          const chave = chaves[i];
          const resp = await downloadOne(tipo, chave, cfg);

          if (resp.ok) okCount++;
          else errCount++;

          await sendToTab(tabId, {
            type: "XSIST_PROGRESS",
            mode: "batch",
            batchId,
            status: "running",
            total: chaves.length,
            index: i + 1,
            currentKey: chave,
            okCount,
            errCount,
            last: resp
          });

          await new Promise((r) => setTimeout(r, 350));
        }

        const finalMsg = {
          type: "XSIST_PROGRESS",
          mode: "batch",
          batchId,
          status: "done",
          total: chaves.length,
          okCount,
          errCount
        };

        await sendToTab(tabId, finalMsg);

        sendResponse({
          ok: errCount === 0,
          msg: `Lote finalizado. OK=${okCount} | ERRO=${errCount}`,
          batchId
        });
        return;
      }
    } catch (e) {
      sendResponse({ ok: false, msg: String(e) });
    }
  })();

  return true; // async
});

// ---- Status do conector (para o site mostrar "igual FSist") ----
chrome.runtime.onMessage.addListener((msg, sender, sendResponse) => {
  if (!msg || msg.type !== "XSIST_GET_CONNECTOR_STATUS") return;

  (async () => {
    try {
      const r = await fetch("http://127.0.0.1:8765/status", { method: "GET" });
      const data = await r.json();
      sendResponse({ ok: true, data });
    } catch (e) {
      sendResponse({ ok: false, msg: String(e) });
    }
  })();

  return true; // async
});