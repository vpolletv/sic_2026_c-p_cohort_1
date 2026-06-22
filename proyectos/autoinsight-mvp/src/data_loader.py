import streamlit as st
import pandas as pd
import os

@st.cache_data
def get_cleaned_data():
    """
    Carga el dataset limpio. Usa @st.cache_data para evitar 
    recargar el archivo en cada interacción del usuario.
    """
    file_path = os.path.join("data", "used_cars_dataset_v2_clean.csv")
    if not os.path.exists(file_path):
        st.error(f"No se encontró el dataset en: {file_path}")
        return pd.DataFrame()
    return pd.read_csv(file_path)
