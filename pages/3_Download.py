from __future__ import annotations

import json
import time
import streamlit as st

try:
    from streamlit_javascript import st_javascript
except Exception:
    st_javascript = None

try:
    from streamlit_autorefresh import st_autorefresh
except Exception:
    st_autorefresh = None


st.set_page_config(page_title="Download", layout="wide")
st.title("Download por Chave (via Extensão)")

def so_digitos(s: str) -> str:
    return "".join(c for c in (s or "") if c.isdigit())

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

def post_to_extension(payload: dict):
    st_javascript(f"window.parent.postMessage({json.dumps(payload)}, '*');")


if not st_javascript:
    st.error("Falta o pacote streamlit-javascript no servidor. (python -m pip install streamlit-javascript)")
    st.stop()

# --- status vindo da extensão ---
ext_info = read_ls("xsist_extension_info")
conn_status = read_ls("xsist_connector_status")

colA, colB = st.columns(2)
with colA:
    st.subheader("Extensão")
    if ext_info:
        st.success("Extensão detectada nesta página.")
        st.json(ext_info)
    else:
        st.error("Extensão NÃO detectada. Recarregue a extensão em chrome://extensions e dê F5 aqui.")

with colB:
    st.subheader("Conector local")
    if not conn_status:
        st.warning("Sem status do conector ainda. Clique em 'Atualizar status do conector'.")
    else:
        if conn_status.get("ok"):
            st.success("Conector respondeu.")
        else:
            st.error("Conector não respondeu (OFF).")
        st.json(conn_status)

st.divider()

# Botão para pedir atualização de status (extensão -> conector)
if st.button("Atualizar status do conector", type="primary", use_container_width=True):
    post_to_extension({"type": "XSIST_REFRESH_STATUS"})
    st.info("Pedido enviado. Aguarde 1s e clique novamente se precisar.")

# --- aviso grande quando faltar A1 ---
missing_a1 = False
if isinstance(conn_status, dict) and conn_status.get("ok") and isinstance(conn_status.get("data"), dict):
    data = conn_status["data"]
    if not (data.get("has_cert") and data.get("has_password") and data.get("has_cnpj")):
        missing_a1 = True
        st.error(
            "Certificado A1 NÃO configurado no conector.\n\n"
            "Abra o popup da extensão (ícone na barra do Chrome) e configure:\n"
            "- arquivo .pfx/.p12\n"
            "- senha\n"
            "- CNPJ (14 dígitos)\n\n"
            "Depois volte aqui e clique em 'Atualizar status do conector'."
        )

st.divider()

tipo = st.selectbox("Tipo", ["NFE", "CTE"], index=0)
chave = st.text_input("Chave (44 dígitos)")

# Depois de clicar, vamos ficar “escutando” o último retorno por alguns segundos
if "wait_last" not in st.session_state:
    st.session_state["wait_last"] = False
if "wait_until" not in st.session_state:
    st.session_state["wait_until"] = 0

if st.button("Baixar 1 XML via Extensão", use_container_width=True):
    ch = so_digitos(chave)
    if len(ch) != 44:
        st.error("Chave inválida (precisa 44 dígitos).")
        st.stop()

    # envia comando para a extensão
    post_to_extension({"type": "XSIST_DOWNLOAD", "tipo": tipo, "chave": ch})
    st.success("Comando enviado para a extensão.")

    # inicia espera do retorno
    st.session_state["wait_last"] = True
    st.session_state["wait_until"] = time.time() + 8  # 8 segundos

# auto refresh curto pra tentar mostrar o último retorno
if st_autorefresh and st.session_state["wait_last"] and time.time() < st.session_state["wait_until"]:
    st_autorefresh(interval=1000, key="wait_last_refresh")

last = read_ls("xsist_last")

st.subheader("Último retorno (debug)")
if last:
    st.json(last)
else:
    st.info("Ainda não recebi retorno. (Se a extensão não estiver ativa nesta página, não chega nada.)")