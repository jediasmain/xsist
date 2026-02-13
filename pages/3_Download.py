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


def open_url(url: str):
    st_javascript(f"window.open({json.dumps(url)}, '_blank');")


if not st_javascript:
    st.error("Falta o pacote streamlit-javascript no servidor.")
    st.stop()


# --- status vindo da extensão ---
ext_info = read_ls("xsist_extension_info")
conn_status = read_ls("xsist_connector_status")

st.subheader("Checklist (antes de baixar)")

ext_ok = bool(ext_info)
conn_ok = isinstance(conn_status, dict) and conn_status.get("ok") is True
cert_ok = False
if conn_ok and isinstance(conn_status.get("data"), dict):
    d = conn_status["data"]
    cert_ok = bool(d.get("has_cert") and d.get("has_password") and d.get("has_cnpj"))

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Extensão instalada", "OK" if ext_ok else "FALTA")
with col2:
    st.metric("Conector ligado", "OK" if conn_ok else "OFF")
with col3:
    st.metric("Certificado A1", "OK" if cert_ok else "NÃO CONFIG.")

cA, cB, cC = st.columns(3)
with cA:
    if st.button("Atualizar status", type="primary", use_container_width=True):
        post_to_extension({"type": "XSIST_REFRESH_STATUS"})
        st.info("Pedido enviado. Aguarde 1s e clique novamente se precisar.")
with cB:
    if st.button("Abrir /status do conector", use_container_width=True):
        open_url("http://127.0.0.1:8765/status")
with cC:
    if st.button("Abrir /ping do conector", use_container_width=True):
        open_url("http://127.0.0.1:8765/ping")

with st.expander("Como configurar o A1 (se estiver faltando)", expanded=not cert_ok):
    st.write(
        "1) Clique no ícone da extensão **XSist Connector** (no topo do Chrome)\n"
        "2) Em **Configurar Certificado A1** selecione o arquivo `.pfx/.p12`\n"
        "3) Digite a senha\n"
        "4) Digite o CNPJ (14 dígitos)\n"
        "5) Clique **Salvar certificado no conector**\n"
        "6) Volte aqui e clique **Atualizar status**"
    )

st.divider()

# --- Download UI ---
tipo = st.selectbox("Tipo", ["NFE", "CTE"], index=0)
chave = st.text_input("Chave (44 dígitos)")

if st.button("Baixar 1 XML via Extensão", use_container_width=True):
    ch = so_digitos(chave)
    if len(ch) != 44:
        st.error("Chave inválida (precisa 44 dígitos).")
        st.stop()

    if not ext_ok:
        st.error("A extensão não foi detectada nesta página. Instale/recarregue a extensão e dê F5.")
        st.stop()

    if not conn_ok:
        st.error("O conector parece estar desligado. Abra /ping e ligue o conector.")
        st.stop()

    if not cert_ok:
        st.error("Certificado A1 não está configurado. Configure no popup da extensão.")
        st.stop()

    post_to_extension({"type": "XSIST_DOWNLOAD", "tipo": tipo, "chave": ch})
    st.success("Comando enviado para a extensão. Confira a pasta Downloads.")

    st.session_state["wait_last"] = True
    st.session_state["wait_until"] = time.time() + 8

# auto refresh curto pra tentar mostrar o último retorno
if st_autorefresh and st.session_state.get("wait_last") and time.time() < st.session_state.get("wait_until", 0):
    st_autorefresh(interval=1000, key="wait_last_refresh")

last = read_ls("xsist_last")
st.subheader("Último retorno (debug)")
if last:
    st.json(last)
else:
    st.info("Sem retorno ainda.")