import streamlit as st
from data.db import init_db
from data.repo import add_event

st.set_page_config(page_title="XSist", layout="wide")
init_db()

st.title("XSist - Portal XML (MVP)")
chave = st.text_input("Chave (44 dígitos)")
tipo = st.selectbox("Tipo", ["NFE", "CTE"])

def so_digitos(s): 
    return "".join(c for c in s if c.isdigit())

if st.button("Salvar no histórico"):
    ch = so_digitos(chave)
    if len(ch) != 44:
        st.error("A chave precisa ter 44 dígitos.")
        add_event(ch, tipo, "ERRO", "Chave inválida")
    else:
        st.success("Salvo no Postgres!")
        add_event(ch, tipo, "OK", "MVP: salvo no Postgres")