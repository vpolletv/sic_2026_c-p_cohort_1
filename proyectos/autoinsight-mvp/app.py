import streamlit as st

st.set_page_config(
    page_title="AutoInsight",
    layout="wide"
)

from src.styles import apply_custom_styles
from src.data_loader import get_cleaned_data
from src.views.home import render_home
from src.views.analysis import render_analysis
from src.views.catalog import render_catalog
from src.views.chatbot import render_chatbot

apply_custom_styles()
df = get_cleaned_data()

st.markdown(
    """
    <div style='font-family: "Inter", sans-serif; font-size: 54px; font-weight: 900; letter-spacing: -2px; color: #111827; margin-top: -25px; margin-bottom: 10px;'>
        AutoInsight<span style='color: #2563eb;'>.</span>
    </div>
    """,
    unsafe_allow_html=True
)

tab1, tab2, tab3, tab4 = st.tabs(["Inicio", "Análisis", "Catálogo", "Asistente"])

with tab1:
    render_home(df)

with tab2:
    render_analysis(df)

with tab3:
    render_catalog(df)

with tab4:
    render_chatbot(df)

st.markdown("""
<div style='text-align: center; margin-top: 50px; padding-top: 20px; border-top: 1px solid #e8e8e4;'>
<p style='color: #8a8a8a; font-size: 0.8rem; margin: 0;'>
&copy; 2026 AutoInsight. Creado por <a href='https://github.com/Ariel-Leiva' target='_blank' style='color: #8a8a8a; text-decoration: underline;'>Ariel Leiva</a> y <a href='https://github.com/frankezu' target='_blank' style='color: #8a8a8a; text-decoration: underline;'>Franco Bernal</a> para <a href='https://innovationcampus.cl/' target='_blank' style='color: #8a8a8a; text-decoration: underline; font-weight: 700;'>Samsung Innovation Campus</a>.
</p>
</div>
""", unsafe_allow_html=True)
