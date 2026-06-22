import streamlit as st
import pandas as pd
import os
import base64

def render_vehicle_card(row):
    """
    Renderiza la tarjeta de un vehículo individual con su logo, 
    especificaciones y precio.
    """
    brand = row.get('brand', '')
    model = row.get('model', '')
    year = int(row.get('year', 0)) if pd.notna(row.get('year')) else ''
    price = f"${int(row.get('askprice', 0)):,}".replace(",", ".") if pd.notna(row.get('askprice')) else 'N/A'
    km = f"{int(row.get('kmdriven', 0)):,}".replace(",", ".") if pd.notna(row.get('kmdriven')) else 'N/A'
    trans = row.get('transmission', 'N/A')
    fuel = row.get('fueltype', 'N/A')
    
    owner_raw = str(row.get('owner', 'N/A'))
    owner_clean = owner_raw.strip().lower()
    owner_map = {
        'first owner': 'Único Dueño', 'first': 'Único Dueño', '1st owner': 'Único Dueño',
        'second owner': 'Segundo Dueño', 'second': 'Segundo Dueño', '2nd owner': 'Segundo Dueño',
        'third owner': 'Tercer Dueño', 'third': 'Tercer Dueño', '3rd owner': 'Tercer Dueño',
        'fourth & above owner': 'Múltiples Dueños', 'fourth & above': 'Múltiples Dueños', '4th owner': 'Múltiples Dueños',
        'test drive car': 'Vehículo de Prueba'
    }
    owner = owner_map.get(owner_clean, owner_raw.title())

    with st.container():
        # Añadimos una columna a la izquierda para el logo
        col_img, col_info, col_price = st.columns([1, 4, 1.5])
        
        with col_img:
            brand_str = str(brand).lower()
            
            # Mapeo de excepciones a los archivos reales de la carpeta logos
            brand_mapping = {
                "maruti suzuki": "suzuki",
                "land rover": "land-rover",
                "aston martin": "aston-martin",
                "force": "force-motors",
                "ambassador": "hindustan-motors",
                "ashok": "leyland",
                "toyota land": "toyota"
            }
            
            if brand_str in brand_mapping:
                logo_name = brand_mapping[brand_str]
            else:
                logo_name = brand_str.replace(" ", "-")
                
            logo_filename = f"{logo_name}.png"
            logo_path = os.path.join("assets", "logos", logo_filename)
            
            if os.path.exists(logo_path):
                with open(logo_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode()
                
                st.markdown(
                    f"<div style='display: flex; justify-content: center; align-items: center; height: 90px;'>"
                    f"<img src='data:image/png;base64,{encoded_string}' style='max-width: 100%; max-height: 100%; object-fit: contain;'>"
                    f"</div>", 
                    unsafe_allow_html=True
                )
            else:
                st.markdown("<div style='display: flex; justify-content: center; align-items: center; height: 90px;'><span style='color: gray; font-size: 12px;'>[ Logo ]</span></div>", unsafe_allow_html=True)

        with col_info:
            info_html = f"""
            <div style="font-family: 'Inter', sans-serif; padding-left: 10px;">
                <h3 style="margin: 0; padding: 0; font-weight: 600; font-size: 20px;">{brand} {model} <span style="font-size: 16px; font-weight: 400; color: gray;">{year}</span></h3>
                <div style="display: flex; flex-wrap: wrap; gap: 15px; margin-top: 8px; font-size: 14px; color: #4b5563;">
                    <div><b>Kilometraje:</b> {km} km</div>
                    <div><b>Motor:</b> {fuel}</div>
                    <div><b>Caja:</b> {trans}</div>
                    <div><b>Historial:</b> {owner}</div>
                </div>
            </div>
            """
            st.markdown(info_html, unsafe_allow_html=True)
        
        with col_price:
            price_html = f"""
            <div style="text-align: right; font-family: 'Inter', sans-serif; padding-top: 5px;">
                <div style="font-size: 11px; color: gray; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 2px;">Valor Estimado</div>
                <div style="font-size: 22px; font-weight: 700; color: #2563eb;">{price} CLP</div>
            </div>
            """
            st.markdown(price_html, unsafe_allow_html=True)
        
        st.markdown("<hr style='margin: 15px 0; border: none; border-top: 1px solid rgba(128, 128, 128, 0.2);'>", unsafe_allow_html=True)
