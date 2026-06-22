import streamlit as st

st.set_page_config(
page_title="Simulador de Incendios Forestales",
page_icon="🔥",
layout="wide"
)

pg = st.navigation([
st.Page("app.py", title="Simulador", icon="🔥"),
st.Page("contexto.py", title="Contexto", icon="📚"),
st.Page("vegetacion.py", title="Vegetación", icon="🌲"),
])

pg.run()
