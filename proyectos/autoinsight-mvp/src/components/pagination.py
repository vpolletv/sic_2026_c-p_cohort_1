import streamlit as st

def get_pagination_info(total_results, page_size=20):
    """
    Retorna la página actual, el total de páginas y los índices 
    de inicio y fin para cortar el dataframe.
    """
    total_pages = (total_results // page_size) + (1 if total_results % page_size > 0 else 0)
    
    if "catalog_page" not in st.session_state:
        st.session_state.catalog_page = 1
        
    if st.session_state.catalog_page > total_pages:
        st.session_state.catalog_page = max(1, total_pages)
        
    start_idx = (st.session_state.catalog_page - 1) * page_size
    end_idx = start_idx + page_size
    
    return st.session_state.catalog_page, total_pages, start_idx, end_idx

def render_pagination_controls(key_suffix, total_pages):
    """
    Renderiza los botones de página anterior y siguiente.
    """
    if total_pages > 1:
        col_prev, col_center, col_next = st.columns([1.5, 7, 1.5])
        with col_prev:
            if st.button("Página Anterior", disabled=(st.session_state.catalog_page == 1), key=f"prev_{key_suffix}", type="primary", use_container_width=True):
                st.session_state.catalog_page -= 1
                st.rerun()
        with col_center:
            st.markdown(f"<div style='text-align: center; padding-top: 8px;'>Página <b>{st.session_state.catalog_page}</b> de {total_pages}</div>", unsafe_allow_html=True)
        with col_next:
            if st.button("Página Siguiente", disabled=(st.session_state.catalog_page == total_pages), key=f"next_{key_suffix}", type="primary", use_container_width=True):
                st.session_state.catalog_page += 1
                st.rerun()
