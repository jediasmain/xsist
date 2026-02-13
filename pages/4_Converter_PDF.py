import streamlit as st

from data.db import init_db
from data.repo import list_xml_docs, get_xml_doc
from services.pdf_utils import xml_to_pdf_bytes, extract_basic_fields

st.set_page_config(page_title="Converter XML → PDF", layout="wide")
init_db()

st.title("Converter XML → PDF (Resumo)")

st.caption("Gera um PDF simples com dados básicos do XML. (Não é DANFE oficial)")

tab1, tab2 = st.tabs(["Upload de XML", "Usar XML salvo no banco"])

with tab1:
    up = st.file_uploader("Envie um XML", type=["xml"])
    if up:
        raw = up.read()
        try:
            xml_text = raw.decode("utf-8")
        except UnicodeDecodeError:
            xml_text = raw.decode("latin-1")

        fields = extract_basic_fields(xml_text)
        st.write("Detectado:")
        st.json(fields)

        pdf_bytes = xml_to_pdf_bytes(xml_text)
        fname = f"resumo_{fields['tipo']}_{fields['chave'] or 'xml'}.pdf"

        st.download_button(
            "Baixar PDF",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
        )

with tab2:
    docs = list_xml_docs(200)
    if not docs:
        st.info("Nenhum XML salvo ainda. Vá na página XMLs e salve algum XML primeiro.")
    else:
        doc_id = st.selectbox("Escolha um XML salvo (ID)", [d["id"] for d in docs])
        doc = get_xml_doc(int(doc_id))
        if doc:
            fields = extract_basic_fields(doc["xml_text"])
            st.write("Detectado:")
            st.json(fields)

            pdf_bytes = xml_to_pdf_bytes(doc["xml_text"])
            fname = f"resumo_{fields['tipo']}_{fields['chave'] or doc_id}.pdf"

            st.download_button(
                "Baixar PDF",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True,
            )