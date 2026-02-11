import streamlit as st
import pandas as pd
from data.db import init_db
from data.repo import list_events

st.set_page_config(page_title="Histórico", layout="wide")
init_db()

st.title("Histórico")
df = pd.DataFrame(list_events(300))
st.dataframe(df, use_container_width=True, hide_index=True)