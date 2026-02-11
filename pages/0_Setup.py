import json
import streamlit as st

try:
    from streamlit_javascript import st_javascript
except Exception:
    st_javascript = None

st.set_page_config(page_title="Setup", layout="wide")
st.title("Setup (igual FSist): Extensão + Conector")

if not st_javascript:
    st.error("Instale no terminal:  python -m pip install streamlit-javascript")
    st.stop()


def read_ls(key: str):
    val = st_javascript(f"window.parent.localStorage.getItem({json.dumps(key)});")
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return val


st.caption("Este site depende da Extensão do Chrome + Conector local (127.0.0.1:8765).")

col1, col2 = st.columns(2)

with col1:
    st.subheader("1) Extensão")
    ext = read_ls("xsist_extension_info")
    if not ext:
        st.error("Extensão NÃO detectada nesta página.")
        st.write("Checklist:")
        st.write("- A extensão XSist Connector está instalada?")
        st.write("- Você está abrindo o site em http://localhost:8501 (não em outro domínio)?")
        st.write("- Recarregue a extensão em chrome://extensions e dê F5 no site.")
    else:
        st.success("Extensão detectada.")
        st.json(ext)

with col2:
    st.subheader("2) Conector local")
    conn = read_ls("xsist_connector_status")
    if not conn:
        st.warning("Ainda sem status. Clique em 'Atualizar status'.")
    else:
        if conn.get("ok"):
            st.success("Conector respondeu /status.")
            st.json(conn.get("data", conn))
        else:
            st.error("Conector NÃO respondeu (provavelmente desligado).")
            st.json(conn)

st.divider()

st.subheader("Ações rápidas")

c1, c2, c3 = st.columns(3)

with c1:
    if st.button("Atualizar status", type="primary", use_container_width=True):
        st_javascript("window.parent.postMessage({type:'XSIST_REFRESH_STATUS'}, '*');")
        st.info("Pedido enviado. Aguarde 1 segundo e clique novamente se precisar.")

with c2:
    if st.button("Abrir /ping do conector", use_container_width=True):
        st_javascript("window.open('http://127.0.0.1:8765/ping', '_blank');")

with c3:
    if st.button("Abrir /status do conector", use_container_width=True):
        st_javascript("window.open('http://127.0.0.1:8765/status', '_blank');")

st.divider()
st.subheader("Se o conector estiver OFF: baixe e execute o arquivo")

# Serve tanto pra você quanto pra um usuário final (fica bem estilo tutorial)
bat_conector = r"""@echo off
cd /d %~dp0\..

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
cd /d %~dp0\..

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

st.info(
    "Como usar:\n"
    "1) Baixe o .bat\n"
    "2) Mova o .bat para dentro da pasta do projeto (onde está o app.py)\n"
    "3) Dê duplo clique nele\n"
    "4) Volte no site e clique em 'Atualizar status'"
)