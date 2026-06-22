import streamlit as st
import pandas as pd

def render_filters(df):
    """
    Renderiza los filtros en el expansor y retorna un diccionario
    con los valores seleccionados.
    """
    filters = {}
    
    with st.expander("Filtros de Búsqueda", expanded=True):
        st.markdown("<h5 style='color: #1a1a1a; font-weight: 700; margin-bottom: 15px;'>Parámetros Numéricos</h5>", unsafe_allow_html=True)
        col_s1, col_s2, col_s3 = st.columns(3)
        with col_s1:
            min_year = int(df['year'].min())
            max_year = int(df['year'].max())
            filters['years'] = st.slider("Rango de Años", min_value=min_year, max_value=max_year, value=(min_year, max_year))
        with col_s2:
            max_km = int(df['kmdriven'].max())
            filters['km'] = st.slider("Rango de Kilometraje", min_value=0, max_value=max_km, value=(0, max_km), step=5000, format="%,d km")
        with col_s3:
            max_price = int(df['askprice'].max())
            filters['price'] = st.slider("Rango de Precio (CLP)", min_value=0, max_value=max_price, value=(0, max_price), step=500000, format="$%,d CLP")
            
        st.divider()
        
        st.markdown("<h5 style='color: #1a1a1a; font-weight: 700; margin-bottom: 15px;'>Especificaciones Técnicas</h5>", unsafe_allow_html=True)
        col_c1, col_c2, col_c3, col_c4, col_c5 = st.columns(5)
        with col_c1:
            marcas = df['brand'].dropna().unique()
            filters['brand'] = st.selectbox("Marca", options=["Todas"] + sorted(list(marcas)))
        with col_c2:
            if filters['brand'] != "Todas":
                modelos = df[df['brand'] == filters['brand']]['model'].dropna().unique()
            else:
                modelos = df['model'].dropna().unique()
            filters['model'] = st.selectbox("Modelo", options=["Todos"] + sorted(list(modelos)))
        with col_c3:
            transmisiones = df['transmission'].dropna().unique()
            filters['trans'] = st.selectbox("Transmisión", options=["Todas"] + list(transmisiones))
        with col_c4:
            combustibles = df['fueltype'].dropna().unique()
            filters['fuel'] = st.selectbox("Combustible", options=["Todos"] + list(combustibles))
        with col_c5:
            dueños = df['owner'].dropna().unique()
            owner_map = {
                'first owner': 'Único Dueño', 'first': 'Único Dueño', '1st owner': 'Único Dueño',
                'second owner': 'Segundo Dueño', 'second': 'Segundo Dueño', '2nd owner': 'Segundo Dueño',
                'third owner': 'Tercer Dueño', 'third': 'Tercer Dueño', '3rd owner': 'Tercer Dueño',
                'fourth & above owner': 'Múltiples Dueños', 'fourth & above': 'Múltiples Dueños', '4th owner': 'Múltiples Dueños',
                'test drive car': 'Vehículo de Prueba'
            }
            
            # Traducimos limpiando y en minúscula para evitar fallos de case
            dueños_traducidos = []
            for d in dueños:
                val_clean = str(d).strip().lower()
                trans = owner_map.get(val_clean, str(d).title())
                dueños_traducidos.append(trans)
                
            # Evitar duplicados (ej: 'first' y 'first owner' mapean a lo mismo)
            dueños_traducidos = sorted(list(set(dueños_traducidos)))
            
            selected_translated = st.selectbox("Historial", options=["Todos"] + dueños_traducidos)
            
            # Guardamos la selección traducida
            filters['owner_selected'] = selected_translated

    return filters

def apply_filters(df, filters):
    """
    Aplica los filtros al dataframe y lo retorna.
    """
    filtered_df = df.copy()
    
    if filters['brand'] != "Todas":
        filtered_df = filtered_df[filtered_df['brand'] == filters['brand']]
    if filters['model'] != "Todos":
        filtered_df = filtered_df[filtered_df['model'] == filters['model']]
        
    filtered_df = filtered_df[
        (filtered_df['year'] >= filters['years'][0]) & 
        (filtered_df['year'] <= filters['years'][1])
    ]
    
    filtered_df = filtered_df[
        (filtered_df['kmdriven'] >= filters['km'][0]) &
        (filtered_df['kmdriven'] <= filters['km'][1])
    ]
    filtered_df = filtered_df[
        (filtered_df['askprice'] >= filters['price'][0]) &
        (filtered_df['askprice'] <= filters['price'][1])
    ]
    
    if filters['trans'] != "Todas":
        filtered_df = filtered_df[filtered_df['transmission'] == filters['trans']]
    if filters['fuel'] != "Todos":
        filtered_df = filtered_df[filtered_df['fueltype'] == filters['fuel']]
    if filters.get('owner_selected', 'Todos') != "Todos":
        # Mapeo inverso robusto: buscar todas las claves originales que corresponden a la traducción
        owner_map = {
            'first owner': 'Único Dueño', 'first': 'Único Dueño', '1st owner': 'Único Dueño',
            'second owner': 'Segundo Dueño', 'second': 'Segundo Dueño', '2nd owner': 'Segundo Dueño',
            'third owner': 'Tercer Dueño', 'third': 'Tercer Dueño', '3rd owner': 'Tercer Dueño',
            'fourth & above owner': 'Múltiples Dueños', 'fourth & above': 'Múltiples Dueños', '4th owner': 'Múltiples Dueños',
            'test drive car': 'Vehículo de Prueba'
        }
        
        # Encontramos cuáles valores reales en el df corresponden a la traducción
        valid_originals = []
        for d in df['owner'].dropna().unique():
            val_clean = str(d).strip().lower()
            trans = owner_map.get(val_clean, str(d).title())
            if trans == filters['owner_selected']:
                valid_originals.append(d)
                
        if not valid_originals:
            valid_originals = [filters['owner_selected']]
            
        filtered_df = filtered_df[filtered_df['owner'].isin(valid_originals)]
        
    return filtered_df
