import streamlit as st
import pandas as pd
import altair as alt

def render_analysis(df):
    """
    Renderiza la vista de Análisis, respondiendo la pregunta principal y 
    mostrando múltiples visualizaciones de los datos.
    """
    if df.empty:
        st.warning("El dataset está vacío. Por favor, verifica la carga de datos.")
        return



    # Pregunta y Respuesta
    st.markdown("<div style='margin-top: 20px; padding-top: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='color: #2563eb; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 30px; font-weight: 700;'>¿Qué debes saber antes de comprar?</p>", unsafe_allow_html=True)
    st.markdown("""
<div style='padding: 0 15%;'>
<div style='margin-bottom: 30px;'>
<p style='font-size: 1.3rem; color: #1a1a1a; line-height: 1.6; text-align: center; font-weight: 600;'>
¿Cuáles son realmente los factores ocultos que determinan si estás pagando un precio justo o si el vehículo perderá su valor rápidamente al salir del concesionario?
</p>
</div>
<div style='margin-bottom: 50px;'>
<p style='font-size: 0.95rem; color: #4a4a4a; line-height: 1.6; text-align: justify;'>
Comprar un auto usado puede ser abrumador. En AutoInsight nos preguntamos esto y, al analizar los más de 14.000 autos que tenemos actualmente en venta en nuestro catálogo, confirmamos que el precio de mercado no se define al azar: está dictado estrictamente por la combinación de <b>año, kilometraje y transmisión</b>. Por ejemplo, los vehículos automáticos mantienen su valor de reventa mucho mejor que los manuales con el paso del tiempo.
<br><br>
Para que puedas tomar tu propia decisión con total transparencia, <b>ponemos a tu disposición los siguientes gráficos interactivos</b> que reflejan la realidad de nuestro inventario. Además, no olvides que hemos integrado un <b>Asistente de Inteligencia Artificial</b> en la plataforma, el cual cruza todos estos datos en tiempo real para recomendarte de forma automática las oportunidades más inteligentes y rentables.
</p>
</div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 40px; padding-top: 1rem;'></div>", unsafe_allow_html=True)

    # Paleta y config global de Altair para mantener minimalismo
    primary_color = '#2563eb'
    secondary_color = '#93c5fd'

    # --- Gráfico 1: Precio Promedio por Año (Línea de Depreciación) ---
    st.markdown("<p style='color: #2563eb; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 15px; font-weight: 700;'>Curva de Depreciación</p>", unsafe_allow_html=True)
    df_year = df.groupby('year')['askprice'].mean().reset_index()
    # Filtramos años muy atípicos si los hay para mejor visualización (ej > 2000)
    df_year = df_year[df_year['year'] >= 2005]
    
    chart_year = alt.Chart(df_year).mark_line(color=primary_color, strokeWidth=4, point=alt.OverlayMarkDef(color=primary_color, size=60)).encode(
        x=alt.X('year:O', title='Año de Fabricación', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('askprice:Q', title='Precio Promedio (CLP)', axis=alt.Axis(format='~s')),
        tooltip=[alt.Tooltip('year', title='Año'), alt.Tooltip('askprice', title='Precio Promedio', format=',.0f')]
    ).properties(height=600)
    st.altair_chart(chart_year, width='stretch')
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

    # --- Gráficos en la misma línea: Transmisión y Combustible ---
    c1, c2 = st.columns(2)
    
    with c1:
        st.markdown("<p style='color: #2563eb; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 15px; font-weight: 700;'>Impacto de la Transmisión</p>", unsafe_allow_html=True)
        df_trans = df.groupby('transmission')['askprice'].mean().reset_index()
        
        chart_trans = alt.Chart(df_trans).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color=primary_color).encode(
            x=alt.X('transmission:N', title='', sort='-y', axis=alt.Axis(labelAngle=0, labelFontSize=12)),
            y=alt.Y('askprice:Q', title='Precio Promedio (CLP)'),
            tooltip=[alt.Tooltip('transmission', title='Transmisión'), alt.Tooltip('askprice', title='Precio Promedio', format=',.0f')]
        ).properties(height=350)
        st.altair_chart(chart_trans, width='stretch')
        
    with c2:
        st.markdown("<p style='color: #2563eb; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 15px; font-weight: 700;'>Volumen por Combustible</p>", unsafe_allow_html=True)
        df_fuel = df['fueltype'].value_counts().reset_index()
        df_fuel.columns = ['fueltype', 'count']
        
        chart_fuel = alt.Chart(df_fuel).mark_arc(innerRadius=50).encode(
            theta=alt.Theta(field="count", type="quantitative"),
            color=alt.Color(field="fueltype", type="nominal", title="Combustible", scale=alt.Scale(scheme='blues')),
            tooltip=[alt.Tooltip('fueltype', title='Combustible'), alt.Tooltip('count', title='Cantidad')]
        ).properties(height=350) # Matching height with chart_trans
        st.altair_chart(chart_fuel, width='stretch')

    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

    # --- Gráfico 3: Relación Kilometraje vs Precio ---
    st.markdown("<p style='color: #2563eb; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 15px; font-weight: 700;'>Desgaste por Kilometraje</p>", unsafe_allow_html=True)
    # Para evitar un scatterplot muy denso que ralentice la app, agrupamos por rangos de km
    df['km_bin'] = pd.cut(df['kmdriven'], bins=range(0, 200000, 20000), labels=[f"{i}k-{i+20}k" for i in range(0, 180, 20)])
    df_km = df.groupby('km_bin')['askprice'].mean().reset_index()
    
    chart_km = alt.Chart(df_km).mark_bar(color=secondary_color, cornerRadiusTopLeft=5, cornerRadiusTopRight=5).encode(
        x=alt.X('km_bin:O', title='Rango de Kilometraje', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('askprice:Q', title='Precio Promedio (CLP)'),
        tooltip=[alt.Tooltip('km_bin', title='Rango Km'), alt.Tooltip('askprice', title='Precio', format=',.0f')]
    ).properties(height=350)
    st.altair_chart(chart_km, width='stretch')
    st.markdown("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

    # --- Gráfico 5: Marcas Más Caras (Promedio) ---
    st.markdown("<p style='color: #2563eb; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 15px; font-weight: 700;'>Top 10 Marcas por Precio Promedio</p>", unsafe_allow_html=True)
    # Solo consideramos marcas con al menos 20 autos para no sesgar con exóticos de 1 sola unidad
    marcas_validas = df['brand'].value_counts()[df['brand'].value_counts() > 20].index
    df_brand_price = df[df['brand'].isin(marcas_validas)].groupby('brand')['askprice'].mean().sort_values(ascending=False).head(10).reset_index()
    
    chart_brand_price = alt.Chart(df_brand_price).mark_bar(cornerRadiusTopLeft=5, cornerRadiusTopRight=5, color=primary_color).encode(
        x=alt.X('brand:N', title='', sort='-y', axis=alt.Axis(labelAngle=-45)),
        y=alt.Y('askprice:Q', title='Precio Promedio (CLP)', axis=alt.Axis(format='~s')),
        tooltip=[alt.Tooltip('brand', title='Marca'), alt.Tooltip('askprice', title='Precio Promedio', format=',.0f')]
    ).properties(height=450)
    st.altair_chart(chart_brand_price, width='stretch')


