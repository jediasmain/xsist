import json
import streamlit as st

try:
    from streamlit_javascript import st_javascript
except Exception:
    st_javascript = None

st.set_page_config(page_title="Ajuda - XSist", layout="wide")
st.title("Ajuda / Como usar (XSist)")

st.caption(
    "Modelo FSist: Site (internet) + Extensão Chrome + Conector local (127.0.0.1:8765)."
)

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

st.divider()

st.header("Diagnóstico rápido")

if not st_javascript:
    st.warning("Para diagnóstico automático, instale no projeto: `python -m pip install streamlit-javascript`")
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

st.header("Ações rápidas (atalhos)")
col1, col2, col3 = st.columns(3)

with col1:
    if st.button("Abrir /ping do conector", use_container_width=True):
        open_url("http://127.0.0.1:8765/ping")

with col2:
    if st.button("Abrir /status do conector", use_container_width=True):
        open_url("http://127.0.0.1:8765/status")

with col3:
    if st.button("Abrir chrome://extensions (manual)", use_container_width=True):
        st.info("O Chrome não permite abrir chrome://extensions via botão do site. Digite na barra do navegador.")

st.divider()

st.header("1) Instalar a Extensão do Chrome")
st.write(
    "1) Vá na página **Setup**\n"
    "2) Baixe o ZIP da extensão\n"
    "3) Descompacte (pasta `chrome_ext`)\n"
    "4) Abra `chrome://extensions`\n"
    "5) Ative **Modo do desenvolvedor**\n"
    "6) Clique **Carregar sem compactação**\n"
    "7) Selecione a pasta `chrome_ext`\n"
    "8) Fixe o ícone da extensão na barra do Chrome\n"
)

st.info(
    "Se ao escolher a pasta ela parecer 'vazia', é normal. "
    "O seletor de pastas do Chrome nem sempre lista arquivos. "
    "Se dentro tiver `manifest.json`, clique em **Selecionar pasta**."
)

st.divider()

st.header("2) Rodar o Conector (Windows)")
st.write(
    "1) Baixe o **XSistConnector (ZIP)** na página Setup\n"
    "2) Extraia\n"
    "3) Execute `XSistConnector.exe`\n"
    "4) Deixe a janela aberta\n"
)

st.write("Teste rápido:")
st.code("http://127.0.0.1:8765/ping", language="text")

st.divider()

st.header("3) Configurar Certificado A1 (para baixar da SEFAZ)")
st.warning(
    "Para baixar XML oficial da SEFAZ é obrigatório ter A1 (.pfx/.p12) e permissão para o documento "
    "(emitente/destinatário/autXML)."
)

st.write(
    "1) Clique no ícone da extensão **XSist Connector**\n"
    "2) Selecione o `.pfx/.p12`\n"
    "3) Digite a senha\n"
    "4) Digite o CNPJ (14 dígitos)\n"
    "5) Clique **Salvar certificado no conector**\n"
    "6) Volte no Setup e clique **Atualizar status**\n"
)

st.divider()

st.header("4) Baixar XML")
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