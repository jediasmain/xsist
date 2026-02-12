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


st.set_page_config(page_title="Setup", layout="wide")
st.title("Setup (igual FSist): Extensão + Conector")
st.caption("Este site depende da Extensão do Chrome + Conector local (127.0.0.1:8765).")


# ----------------------------
# Helpers
# ----------------------------
def read_ls(key: str):
    """Lê localStorage do navegador (só funciona se streamlit-javascript estiver instalado)."""
    if not st_javascript:
        return None
    val = st_javascript(f"window.parent.localStorage.getItem({json.dumps(key)});")
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return val


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
# Seção: status
# ----------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("1) Extensão")

    if not st_javascript:
        st.warning("Para detectar a extensão aqui, instale no projeto: `python -m pip install streamlit-javascript`")

    ext = read_ls("xsist_extension_info")
    if not ext:
        st.error("Extensão NÃO detectada nesta página.")
        st.write("Checklist:")
        st.write("- A extensão XSist Connector está instalada e ATIVA?")
        st.write("- Recarregue a extensão em chrome://extensions")
        st.write("- Dê F5 nesta página")
    else:
        st.success("Extensão detectada.")
        st.json(ext)

with col2:
    st.subheader("2) Conector local")

    conn = read_ls("xsist_connector_status")
    if not conn:
        st.warning("Ainda sem status do conector. Clique em 'Atualizar status'.")
    else:
        if conn.get("ok"):
            st.success("Conector respondeu /status.")
        else:
            st.error("Conector NÃO respondeu (provavelmente desligado).")
        st.json(conn)


st.divider()

st.subheader("Ações rápidas")
c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Atualizar status", type="primary", use_container_width=True):
        if not st_javascript:
            st.error("Instale streamlit-javascript para enviar o comando ao navegador.")
        else:
            st_javascript("window.parent.postMessage({type:'XSIST_REFRESH_STATUS'}, '*');")
            st.info("Pedido enviado. Aguarde 1 segundo e clique novamente se precisar.")

with c2:
    if st.button("Abrir /ping do conector", use_container_width=True):
        if st_javascript:
            st_javascript("window.open('http://127.0.0.1:8765/ping', '_blank');")
        else:
            st.info("Abra manualmente: http://127.0.0.1:8765/ping")

with c3:
    if st.button("Abrir /status do conector", use_container_width=True):
        if st_javascript:
            st_javascript("window.open('http://127.0.0.1:8765/status', '_blank');")
        else:
            st.info("Abra manualmente: http://127.0.0.1:8765/status")

st.divider()

# ----------------------------
# Download: Extensão em ZIP
# ----------------------------
st.subheader("Instalar Extensão (download)")

try:
    st.download_button(
        "Baixar XSist Connector (ZIP)",
        data=build_extension_zip(),
        file_name="xsist_connector_chrome_ext.zip",
        mime="application/zip",
        use_container_width=True,
    )
except Exception as e:
    st.error(f"Não consegui gerar o ZIP da extensão: {e}")

st.info(
    "Como instalar a extensão (Chrome):\n"
    "1) Baixe o ZIP e descompacte\n"
    "2) Abra chrome://extensions\n"
    "3) Ative 'Modo do desenvolvedor'\n"
    "4) Clique 'Carregar sem compactação'\n"
    "5) Selecione a pasta descompactada: chrome_ext\n"
)

st.divider()

# ----------------------------
# Download: BATs para iniciar localmente
# ----------------------------
st.subheader("Se o conector estiver OFF: baixe e execute o arquivo")

bat_conector = r"""@echo off
cd /d %~dp0

call .venv\Scripts\activate

python -m uvicorn connector.main:app --host 127.0.0.1 --port 8765 --reload

pause
"""

st.download_button(
    "Baixar iniciar_conector.bat",
    data=bat_conector,
    file_name="iniciar_conector.bat",
    mime="text/plain",
    use_container_width=True,
)

bat_site = r"""@echo off
cd /d %~dp0

call .venv\Scripts\activate

python -m streamlit run app.py

pause
"""

st.download_button(
    "Baixar iniciar_site.bat",
    data=bat_site,
    file_name="iniciar_site.bat",
    mime="text/plain",
    use_container_width=True,
)

st.warning(
    "IMPORTANTE: esses .bat devem ficar na pasta do projeto (onde está o app.py).\n"
    "Depois de ligar o conector, volte aqui e clique em 'Atualizar status'."
)