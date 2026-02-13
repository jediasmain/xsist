import streamlit as st
import pandas as pd

from services.sped_utils import extract_chaves

st.set_page_config(page_title="Extrair Chaves do SPED", layout="wide")
st.title("Extrair Chaves do SPED (44 dígitos)")

st.caption("Envie um arquivo SPED (.txt) e eu extraio todas as chaves de 44 dígitos encontradas.")

up = st.file_uploader("Envie o arquivo SPED (TXT)", type=["txt", "sped", "csv", "log"])

if up:
    raw = up.read()

    # tenta decodificar (SPED às vezes vem latin-1)
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        text = raw.decode("latin-1", errors="replace")

    chaves = extract_chaves(text)

    st.success(f"Encontradas {len(chaves)} chaves únicas.")

    if chaves:
        df = pd.DataFrame({"chave": chaves})
        st.dataframe(df, use_container_width=True, hide_index=True)

        st.download_button(
            "Baixar lista (TXT)",
            data="\n".join(chaves),
            file_name="chaves_extraidas.txt",
            mime="text/plain",
            use_container_width=True,
        )

        st.download_button(
            "Baixar lista (CSV)",
            data=df.to_csv(index=False).encode("utf-8"),
            file_name="chaves_extraidas.csv",
            mime="text/csv",
            use_container_width=True,
        )
else:
    st.info("Envie um arquivo para começar.")