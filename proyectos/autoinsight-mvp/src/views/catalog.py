import streamlit as st
from src.components.filters import render_filters, apply_filters
from src.components.pagination import get_pagination_info, render_pagination_controls
from src.components.vehicle_card import render_vehicle_card

def render_catalog(df):
    """
    Renderiza la vista del catálogo o buscador de vehículos.
    """
    if df.empty:
        st.warning("El dataset está vacío. Por favor, verifica la carga de datos.")
        return

    # 1. Renderizar filtros y obtener selecciones
    filters = render_filters(df)
    
    # 2. Aplicar filtros al dataframe
    filtered_df = apply_filters(df, filters)
        
    total_results = len(filtered_df)
    
    if total_results == 0:
        st.info("No se han encontrado vehículos que coincidan con los criterios de búsqueda especificados.")
    else:
        # 3. Configuración de paginación
        page, total_pages, start_idx, end_idx = get_pagination_info(total_results)
        
        # Controles superiores: Resultados y Ordenamiento
        col_res, col_sort = st.columns([3, 1])
        with col_res:
            st.write(f"**Mostrando resultados {start_idx + 1} al {min(end_idx, total_results)} de {total_results}:**")
        with col_sort:
            sort_order = st.selectbox(
                "Orden", 
                ["Sin orden", "Precio: Menor a Mayor", "Precio: Mayor a Menor"], 
                label_visibility="collapsed"
            )
            
        # Aplicar ordenamiento al dataframe ANTES de paginar
        if sort_order == "Precio: Menor a Mayor":
            filtered_df = filtered_df.sort_values(by="askprice", ascending=True)
        elif sort_order == "Precio: Mayor a Menor":
            filtered_df = filtered_df.sort_values(by="askprice", ascending=False)
            
        # 4. Renderizar paginación superior
        render_pagination_controls("top", total_pages)
        st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid rgba(128, 128, 128, 0.2);'>", unsafe_allow_html=True)
        
        # 5. Renderizar resultados
        resultados = filtered_df.iloc[start_idx:end_idx]
        
        for _, row in resultados.iterrows():
            render_vehicle_card(row)
                
        # 6. Renderizar paginación inferior
        render_pagination_controls("bottom", total_pages)
