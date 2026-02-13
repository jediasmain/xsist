import streamlit as st

from data.db import init_db
from data.repo import list_xml_docs, get_xml_doc
from services.dacte_simplificado import cte_xml_to_dacte_pdf_bytes, extract_cte_for_dacte

st.set_page_config(page_title="DACTE Simplificado", layout="wide")
init_db()

st.title("DACTE Simplificado (CT-e)")
st.caption("Gera um PDF estilo DACTE a partir do XML. (MVP / não oficial)")

tab1, tab2 = st.tabs(["Upload de XML", "Usar XML salvo no banco"])

with tab1:
    up = st.file_uploader("Envie um XML de CT-e", type=["xml"])
    if up:
        raw = up.read()
        try:
            xml_text = raw.decode("utf-8")
        except UnicodeDecodeError:
            xml_text = raw.decode("latin-1")

        info = extract_cte_for_dacte(xml_text)
        st.write("Detectado:")
        st.json({k: v for k, v in info.items() if k != "comps"})
        st.write(f"Componentes: {len(info['comps'])}")

        pdf_bytes = cte_xml_to_dacte_pdf_bytes(xml_text)
        fname = f"DACTE_{info['chave'] or 'CTE'}.pdf"

        st.download_button(
            "Baixar DACTE (PDF)",
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
            info = extract_cte_for_dacte(xml_text)
            st.write("Detectado:")
            st.json({k: v for k, v in info.items() if k != "comps"})
            st.write(f"Componentes: {len(info['comps'])}")

            pdf_bytes = cte_xml_to_dacte_pdf_bytes(xml_text)
            fname = f"DACTE_{info['chave'] or doc_id}.pdf"

            st.download_button(
                "Baixar DACTE (PDF)",
                data=pdf_bytes,
                file_name=fname,
                mime="application/pdf",
                use_container_width=True,
            )