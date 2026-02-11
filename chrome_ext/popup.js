const statusBox = document.getElementById("statusBox");
const cfgBox = document.getElementById("cfgBox");
const out = document.getElementById("out");

const btnStatus = document.getElementById("btnStatus");
const btnVerify = document.getElementById("btnVerify");

const saveAs = document.getElementById("saveAs");
const folder = document.getElementById("folder");
const btnSaveCfg = document.getElementById("btnSaveCfg");

const pfx = document.getElementById("pfx");
const senha = document.getElementById("senha");
const cnpj = document.getElementById("cnpj");
const tpamb = document.getElementById("tpamb");
const btnSaveCert = document.getElementById("btnSaveCert");

async function getStatus() {
  statusBox.textContent = "Consultando /status...";
  try {
    const r = await fetch("http://127.0.0.1:8765/status");
    const data = await r.json();
    statusBox.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    statusBox.textContent = "Erro: " + e;
  }
}

async function verifySavedCert() {
  out.textContent = "Testando /cert/verify...";
  try {
    const r = await fetch("http://127.0.0.1:8765/cert/verify");
    const data = await r.json();
    out.textContent = JSON.stringify(data, null, 2);
  } catch (e) {
    out.textContent = "Erro: " + e;
  }
}

function toBase64(arrayBuffer) {
  let binary = "";
  const bytes = new Uint8Array(arrayBuffer);
  for (let i = 0; i < bytes.byteLength; i++) binary += String.fromCharCode(bytes[i]);
  return btoa(binary);
}

// ----- Config download (storage)
async function loadCfg() {
  const stored = await chrome.storage.local.get(["saveAs", "folder"]);
  const cfg = {
    saveAs: typeof stored.saveAs === "boolean" ? stored.saveAs : true,
    folder: stored.folder ? stored.folder : "XSist"
  };

  saveAs.checked = cfg.saveAs;
  folder.value = cfg.folder;
  cfgBox.textContent = JSON.stringify(cfg, null, 2);
}

btnSaveCfg.addEventListener("click", async () => {
  const cfg = {
    saveAs: !!saveAs.checked,
    folder: String(folder.value || "").trim()
  };
  await chrome.storage.local.set(cfg);
  cfgBox.textContent = JSON.stringify(cfg, null, 2);
});

// ----- Cert
btnSaveCert.addEventListener("click", async () => {
  out.textContent = "Enviando certificado para o conector...";

  try {
    if (!pfx.files || pfx.files.length === 0) {
      out.textContent = "Escolha o arquivo .pfx/.p12.";
      return;
    }
    if (!senha.value) {
      out.textContent = "Digite a senha do certificado.";
      return;
    }

    const file = pfx.files[0];
    const buf = await file.arrayBuffer();
    const pfx_b64 = toBase64(buf);

    const payload = {
      pfx_b64,
      password: senha.value,
      cnpj: cnpj.value || "",
      tp_amb: Number(tpamb.value || "1")
    };

    const r = await fetch("http://127.0.0.1:8765/config/cert", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });

    const data = await r.json();
    out.textContent = JSON.stringify(data, null, 2);
    await getStatus();
  } catch (e) {
    out.textContent = "Erro: " + e;
  }
});

// botões
btnStatus.addEventListener("click", getStatus);
btnVerify.addEventListener("click", verifySavedCert);

// init
loadCfg();
getStatus();