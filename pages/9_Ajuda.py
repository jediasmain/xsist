from __future__ import annotations

import json
import os
import zipfile
from io import BytesIO
from pathlib import Path

import streamlit as st

try:
    from streamlit_javascript import st_javascript
except Exception:
    st_javascript = None

from services.github_release import get_latest_release_asset_url


# >>> CONFIG DO SEU REPO/ASSET <<<
GITHUB_OWNER = "jediasmain"
GITHUB_REPO = "xsist"
CONNECTOR_ASSET_NAME = "XSistConnector.zip"


st.set_page_config(page_title="Ajuda - XSist", layout="wide")
st.title("Ajuda / Como usar (XSist)")
st.caption("Modelo FSist: Site (internet) + Extensão Chrome + Conector local (127.0.0.1:8765).")


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
    repo_root = Path(__file__).resolve().parents[1]
    ext_dir = repo_root / "chrome_ext"

    if not ext_dir.exists():
        raise FileNotFoundError(f"Pasta não encontrada: {ext_dir}")

    buf = BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for p in ext_dir.rglob("*"):
            if p.is_file():
                z.write(p, arcname=f"chrome_ext/{p.relative_to(ext_dir)}")

    return buf.getvalue()


@st.cache_data(ttl=3600)
def get_connector_zip_url() -> str | None:
    token = None
    try:
        token = st.secrets.get("GITHUB_TOKEN", None)
    except Exception:
        token = os.getenv("GITHUB_TOKEN")

    return get_latest_release_asset_url(
        owner=GITHUB_OWNER,
        repo=GITHUB_REPO,
        asset_name=CONNECTOR_ASSET_NAME,
        token=token,
    )


# ----------------------------
# Downloads
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
        "1) Descompacte (pasta `chrome_ext`)\n"
        "2) Abra `chrome://extensions`\n"
        "3) Ative Modo do desenvolvedor\n"
        "4) Carregar sem compactação\n"
        "5) Selecione a pasta `chrome_ext`\n"
    )

with col2:
    st.subheader("Conector (Windows)")
    url = get_connector_zip_url()
    if url:
        st.link_button("Baixar Conector (ZIP) - latest", url, use_container_width=True)
    else:
        st.error("Não achei XSistConnector.zip no GitHub Releases (latest).")

    st.info(
        "Usar:\n"
        "1) Baixe o ZIP\n"
        "2) Extraia\n"
        "3) Execute `XSistConnector.exe`\n"
        "4) Teste: http://127.0.0.1:8765/ping\n"
    )

st.divider()

# ----------------------------
# Diagnóstico
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

st.header("Atalhos")
a1, a2 = st.columns(2)
with a1:
    if st.button("Abrir /ping do conector", use_container_width=True):
        open_url("http://127.0.0.1:8765/ping")
with a2:
    if st.button("Abrir /status do conector", use_container_width=True):
        open_url("http://127.0.0.1:8765/status")

st.divider()

st.header("Passo a passo resumido")
st.write(
    "1) Instale a extensão\n"
    "2) Rode o conector\n"
    "3) (Opcional) Configure o certificado A1 no popup da extensão\n"
    "4) Vá em Download e baixe por chave\n"
)

st.warning(
    "Sem certificado A1 (.pfx/.p12), não dá para baixar XML oficial da SEFAZ. "
    "Além disso, o certificado precisa ter permissão/autXML para o documento."
)