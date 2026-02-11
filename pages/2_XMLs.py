import streamlit as st
import pandas as pd

from data.db import init_db
from data.repo import save_xml_doc, list_xml_docs, get_xml_doc
from services.xml_utils import extract_key_and_type

st.set_page_config(page_title="XMLs", layout="wide")
init_db()

st.title("XMLs (Upload / Lista / Download)")

# 1) Inicializa "memória" dos campos (pra não dar erro)
if "tipo" not in st.session_state:
    st.session_state["tipo"] = "NFE"
if "chave" not in st.session_state:
    st.session_state["chave"] = ""

# 2) Upload primeiro
uploaded = st.file_uploader("Envie um arquivo XML", type=["xml"])

xml_text = None
tipo_found = None
key_found = None

if uploaded:
    raw = uploaded.read()
    try:
        xml_text = raw.decode("utf-8")
    except UnicodeDecodeError:
        xml_text = raw.decode("latin-1")

    # (B) AQUI acontece a mágica:
    # extrai tipo e chave do XML e joga na memória do Streamlit
    key_found, tipo_found = extract_key_and_type(xml_text)

    if tipo_found in ("NFE", "CTE"):
        st.session_state["tipo"] = tipo_found

    if key_found and key_found.isdigit() and len(key_found) == 44:
        st.session_state["chave"] = key_found

    st.info(f"Detectado no XML → tipo: {tipo_found} | chave: {key_found}")

# 3) Agora os campos já vêm preenchidos (por causa do session_state)
col1, col2 = st.columns(2)
with col1:
    st.selectbox("Tipo", ["NFE", "CTE"], key="tipo")
with col2:
    st.text_input("Chave (44 dígitos)", key="chave")

def so_digitos(s: str) -> str:
    return "".join(c for c in s if c.isdigit())

# 4) Prévia e salvar
if xml_text:
    st.text_area("Prévia do XML (somente leitura)", xml_text[:2000], height=200)

    if st.button("Salvar XML no banco", type="primary"):
        ch = so_digitos(st.session_state["chave"])
        if len(ch) != 44:
            st.error("Não consegui obter a chave (44 dígitos) desse XML. Preencha manualmente.")
        else:
            save_xml_doc(ch, st.session_state["tipo"], xml_text)
            st.success("XML salvo no Postgres.")

st.divider()

# 5) Lista e download
st.subheader("Últimos XMLs salvos")
docs = list_xml_docs(200)
df = pd.DataFrame(docs)
st.dataframe(df, use_container_width=True, hide_index=True)

if docs:
    doc_id = st.selectbox("Escolha um ID para baixar", [d["id"] for d in docs])
    doc = get_xml_doc(int(doc_id))
    if doc:
        filename = f"{doc['tipo']}_{doc['chave']}.xml"
        st.download_button(
            "Baixar XML",
            data=doc["xml_text"],
            file_name=filename,
            mime="application/xml",
        )