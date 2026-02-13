import streamlit as st

from data.db import init_db
from data.repo import list_xml_docs, get_xml_doc
from services.danfe_simplificado import nfe_xml_to_danfe_pdf_bytes, extract_nfe_for_danfe

st.set_page_config(page_title="DANFE Simplificado", layout="wide")
init_db()

st.title("DANFE Simplificado (NF-e)")

st.caption("Gera um PDF estilo DANFE a partir do XML. (MVP / não oficial)")

tab1, tab2 = st.tabs(["Upload de XML", "Usar XML salvo no banco"])

with tab1:
    up = st.file_uploader("Envie um XML de NF-e", type=["xml"])
    if up:
        raw = up.read()
        try:
            xml_text = raw.decode("utf-8")
        except UnicodeDecodeError:
            xml_text = raw.decode("latin-1")

        info = extract_nfe_for_danfe(xml_text)
        st.write("Detectado:")
        st.json({k: v for k, v in info.items() if k != "itens"})
        st.write(f"Itens: {len(info['itens'])}")

        pdf_bytes = nfe_xml_to_danfe_pdf_bytes(xml_text)
        fname = f"DANFE_{info['chave'] or 'NFE'}.pdf"

        st.download_button(
            "Baixar DANFE (PDF)",
            data=pdf_bytes,
            file_name=fname,
            mime="application/pdf",
            use_container_width=True,
        )

with tab2:
    docs = list_xml_docs(200)
    if not docs:
        st.info("Nenhum XML salvo ainda. Vá em XMLs e salve algum XML.")
    else:
        doc_id = st.selectbox("Escolha um XML salvo (ID)", [d["id"] for d in docs])
        doc = get_xml_doc(int(doc_id))
        if doc:
            xml_text = doc["xml_text"]
            info = extract_nfe_for_danfe(xml_text)
            st.write("Detectado:")
            st.json({k: v for k, v in info.items() if k != "itens"})
            st.write(f"Itens: {len(info['itens'])}")

            pdf_bytes = nfe_xml_to_danfe_pdf_bytes(xml_text)
            fname = f"DANFE_{info['chave'] or doc_id}.pdf"

            st.download_button(
                "Baixar DANFE (PDF)",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True,
            )