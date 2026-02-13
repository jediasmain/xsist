from __future__ import annotations

import json
import zipfile
from io import BytesIO
from pathlib import Path

import streamlit as st

try:
    from streamlit_javascript import st_javascript
except Exception:
    st_javascript = None

# >>>> ATENÇÃO: se você mudar a versão do release, atualize esta URL:
CONNECTOR_ZIP_URL = "https://github.com/jediasmain/xsist/releases/download/v0.1.0/XSistConnector.zip"


st.set_page_config(page_title="Ajuda - XSist", layout="wide")
st.title("Ajuda / Como usar (XSist)")
st.caption("Modelo FSist: Site (internet) + Extensão Chrome + Conector local (127.0.0.1:8765).")


# ----------------------------
# Helpers
# ----------------------------
def read_ls(key: str):
    if not st_javascript:
        return None
    val = st_javascript(f"window.parent.localStorage.getItem({json.dumps(key)});")
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return val


def open_url(url: str):
    if st_javascript:
        st_javascript(f"window.open({json.dumps(url)}, '_blank');")


def build_extension_zip() -> bytes:
    """Gera um ZIP da pasta chrome_ext/ para o usuário baixar."""
    repo_root = Path(__file__).resolve().parents[1]  # raiz do projeto (um nível acima de /pages)
    ext_dir = repo_root / "chrome_ext"

    if not ext_dir.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {ext_dir}")

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in ext_dir.rglob("*"):
            if p.is_file():
                z.write(p, arcname=f"chrome_ext/{p.relative_to(ext_dir)}")

    return buf.getvalue()


# ----------------------------
# Downloads rápidos (igual Setup)
# ----------------------------
st.header("Downloads (Extensão + Conector)")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Extensão do Chrome")
    try:
        st.download_button(
            "Baixar Extensão (ZIP)",
            data=build_extension_zip(),
            file_name="xsist_connector_chrome_ext.zip",
            mime="application/zip",
            use_container_width=True,
        )
    except Exception as e:
        st.error(f"Não consegui gerar o ZIP da extensão: {e}")

    st.info(
        "Instalar (Chrome):\n"
        "1) Descompacte o ZIP (vai ter uma pasta `chrome_ext`)\n"
        "2) Abra `chrome://extensions`\n"
        "3) Ative Modo do desenvolvedor\n"
        "4) Carregar sem compactação\n"
        "5) Selecione a pasta `chrome_ext`\n"
    )

with col2:
    st.subheader("Conector (Windows)")
    st.link_button("Baixar Conector (ZIP)", CONNECTOR_ZIP_URL, use_container_width=True)
    st.info(
        "Usar:\n"
        "1) Baixe o ZIP\n"
        "2) Extraia\n"
        "3) Execute `XSistConnector.exe`\n"
        "4) Teste: http://127.0.0.1:8765/ping\n"
    )

st.divider()


# ----------------------------
# Diagnóstico rápido
# ----------------------------
st.header("Diagnóstico rápido")

if not st_javascript:
    st.warning("Para diagnóstico automático, instale: `python -m pip install streamlit-javascript`")
else:
    ext = read_ls("xsist_extension_info")
    conn = read_ls("xsist_connector_status")

    ext_ok = bool(ext)
    conn_ok = isinstance(conn, dict) and conn.get("ok") is True
    cert_ok = False
    if conn_ok and isinstance(conn.get("data"), dict):
        d = conn["data"]
        cert_ok = bool(d.get("has_cert") and d.get("has_password") and d.get("has_cnpj"))

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Extensão", "OK" if ext_ok else "NÃO detectada")
    with c2:
        st.metric("Conector", "OK" if conn_ok else "OFF")
    with c3:
        st.metric("Certificado A1", "OK" if cert_ok else "NÃO configurado")

    with st.expander("Ver detalhes (JSON)", expanded=False):
        st.write("xsist_extension_info:")
        st.json(ext)
        st.write("xsist_connector_status:")
        st.json(conn)

st.divider()


# ----------------------------
# Atalhos
# ----------------------------
st.header("Ações rápidas (atalhos)")
a1, a2, a3 = st.columns(3)

with a1:
    if st.button("Abrir /ping do conector", use_container_width=True):
        open_url("http://127.0.0.1:8765/ping")

with a2:
    if st.button("Abrir /status do conector", use_container_width=True):
        open_url("http://127.0.0.1:8765/status")

with a3:
    if st.button("Abrir chrome://extensions (manual)", use_container_width=True):
        st.info("O Chrome bloqueia abrir chrome://extensions via botão. Digite na barra do navegador.")

st.divider()


# ----------------------------
# Passo a passo
# ----------------------------
st.header("Passo a passo")

st.subheader("1) Instalar a Extensão do Chrome")
st.write(
    "1) Baixe o ZIP da extensão aqui em cima\n"
    "2) Descompacte (pasta `chrome_ext`)\n"
    "3) Abra `chrome://extensions`\n"
    "4) Ative **Modo do desenvolvedor**\n"
    "5) Clique **Carregar sem compactação**\n"
    "6) Selecione a pasta `chrome_ext`\n"
    "7) Fixe o ícone da extensão na barra do Chrome\n"
)
st.info(
    "Se o seletor de pastas mostrar a pasta 'vazia', é normal. "
    "Se dentro tiver `manifest.json`, clique em **Selecionar pasta**."
)

st.subheader("2) Rodar o Conector (Windows)")
st.write(
    "1) Baixe o Conector (ZIP) aqui em cima\n"
    "2) Extraia\n"
    "3) Execute `XSistConnector.exe`\n"
    "4) Deixe a janela aberta\n"
)

st.subheader("3) Configurar Certificado A1 (para baixar da SEFAZ)")
st.warning(
    "Sem A1 (.pfx/.p12) não dá para baixar XML oficial da SEFAZ. "
    "Precisa também ter permissão/autXML para o documento."
)
st.write(
    "1) Clique no ícone da extensão **XSist Connector**\n"
    "2) Selecione o `.pfx/.p12`\n"
    "3) Digite a senha\n"
    "4) Digite o CNPJ (14 dígitos)\n"
    "5) Clique **Salvar certificado no conector**\n"
)

st.subheader("4) Baixar XML")
st.write(
    "1) Vá na página **Download**\n"
    "2) Selecione NFE/CTE\n"
    "3) Cole a chave (44 dígitos)\n"
    "4) Clique baixar\n"
)

st.divider()

st.header("Problemas comuns")
st.write(
    "- **Conector não responde / Failed to fetch**: o conector (EXE) não está rodando.\n"
    "- **Extensão não detectada**: recarregue a extensão em `chrome://extensions` e dê F5 no site.\n"
    "- **Não baixa da SEFAZ**: falta A1 ou não tem permissão/autXML.\n"
    "- **Chave inválida**: precisa ter 44 dígitos.\n"
)