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

def read_local_storage(key: str):
    if not st_javascript:
        return None
    val = st_javascript(f"window.parent.localStorage.getItem({json.dumps(key)});")
    if not val:
        return None
    try:
        return json.loads(val)
    except Exception:
        return val

def clear_progress():
    if st_javascript:
        st_javascript("window.parent.localStorage.removeItem('xsist_progress');")
        st_javascript("window.parent.localStorage.removeItem('xsist_last_batch');")
        st_javascript("window.parent.localStorage.removeItem('xsist_last');")

# Avisos de dependência
if not st_javascript:
    st.warning("Instale: python -m pip install streamlit-javascript (senão não envia comando para a extensão)")
if not st_autorefresh:
    st.warning("Instale: python -m pip install streamlit-autorefresh (senão não atualiza automático)")

tipo = st.selectbox("Tipo", ["NFE", "CTE"], index=0)

st.subheader("1) Download único")
chave = st.text_input("Chave (44 dígitos)")

if st.button("Baixar 1 XML via Extensão", type="primary", use_container_width=True):
    if not st_javascript:
        st.stop()

    ch = so_digitos(chave)
    if len(ch) != 44:
        st.error("Chave inválida (precisa 44 dígitos).")
        st.stop()

    payload = {"type": "XSIST_DOWNLOAD", "tipo": tipo, "chave": ch}
    st_javascript(f"window.parent.postMessage({json.dumps(payload)}, '*');")
    st.success("Comando enviado para a extensão.")

st.divider()

st.subheader("2) Download em lote")
txt = st.text_area("Cole várias chaves (uma por linha)", height=180)

colA, colB, colC = st.columns(3)

with colA:
    if st.button("Iniciar LOTE via Extensão", use_container_width=True):
        if not st_javascript:
            st.stop()

        chaves = [so_digitos(x) for x in txt.splitlines() if so_digitos(x)]
        chaves = [c for c in chaves if len(c) == 44]

        if not chaves:
            st.error("Nenhuma chave válida (44 dígitos) encontrada.")
            st.stop()

        batch_id = str(int(time.time()))
        st.session_state["batch_id"] = batch_id
        st.session_state["auto_refresh_on"] = True

        clear_progress()

        payload = {"type": "XSIST_DOWNLOAD_BATCH", "tipo": tipo, "chaves": chaves, "batchId": batch_id}
        st_javascript(f"window.parent.postMessage({json.dumps(payload)}, '*');")
        st.success(f"Lote enviado para a extensão. Total: {len(chaves)} | batchId={batch_id}")

with colB:
    if st.button("Parar auto-atualização", use_container_width=True):
        st.session_state["auto_refresh_on"] = False

with colC:
    if st.button("Atualizar agora", use_container_width=True):
        st.rerun()

st.divider()
st.subheader("Progresso (lote)")

prog = read_local_storage("xsist_progress")

# Liga auto-refresh enquanto estiver "running"
auto_on = st.session_state.get("auto_refresh_on", False)
is_running = isinstance(prog, dict) and prog.get("mode") == "batch" and prog.get("status") == "running"

if st_autorefresh and auto_on and is_running:
    st_autorefresh(interval=1000, key="xsist_auto_refresh")  # 1 segundo

if not prog:
    st.info("Sem progresso ainda. Inicie um lote.")
else:
    st.json(prog)

    if prog.get("mode") == "batch" and prog.get("status") == "running":
        st.write(f"Processando: {prog.get('index')}/{prog.get('total')}")
        st.write(f"OK={prog.get('okCount')} | ERRO={prog.get('errCount')}")
        st.write("Chave atual:", prog.get("currentKey"))

    if prog.get("mode") == "batch" and prog.get("status") == "done":
        st.success(f"Lote finalizado: OK={prog.get('okCount')} | ERRO={prog.get('errCount')}")
        st.session_state["auto_refresh_on"] = False