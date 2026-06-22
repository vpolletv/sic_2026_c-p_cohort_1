import streamlit as st
import pandas as pd
import altair as alt

def render_home(df):
    """
    Renderiza la vista principal (Inicio) con métricas, gráficos analíticos y diseño minimalista.
    """
    if df.empty:
        st.warning("El dataset está vacío o no se ha podido cargar.")
        return

    # 1. Hero Section
    st.markdown("""
<div style='text-align: center; padding: 2rem 0;'>
<h1 style='font-size: 2.8rem; color: #1a1a1a; margin-bottom: 15px; font-weight: 400; letter-spacing: -1px;'>Bienvenido a <span style='font-weight: 900;'>AutoInsight</span><span style='color: #2563eb; font-weight: 900;'>.</span></h1>
<p style='font-size: 1.15rem; color: #4a4a4a; max-width: 800px; margin: 0 auto; line-height: 1.6; text-align: center;'>
Redefiniendo la experiencia de compra automotriz. Una plataforma que integra un <b>catálogo de inventario dinámico</b> con <b>inteligencia artificial responsiva</b>.
</p>
</div>
<div style='margin: 20px 0 40px 0;'></div>
""", unsafe_allow_html=True)

    # 2. CARACTERÍSTICAS
    st.markdown("<p style='color: #2563eb; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 20px; font-weight: 700;'>Nuestra Propuesta de Valor</p>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    
    def feature_card(title, desc):
        return f"""
<div style='background-color: #f8f8f6; border: 1px solid #e8e8e4; padding: 2rem; border-radius: 4px;'>
<h3 style='color: #1a1a1a; font-size: 0.95rem; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; margin-top: 0; margin-bottom: 15px;'>{title}</h3>
<p style='color: #6b6b6b; font-size: 0.95rem; line-height: 1.6; margin-bottom: 0; text-align: justify;'>{desc}</p>
</div>
"""

    with col1:
        st.markdown(feature_card(
            "🔍 Catálogo de Alta Precisión", 
            "Navega por el inventario mediante una <b>interfaz limpia</b> y libre de ruido visual. Filtra vehículos por <b>marca, año y transmisión</b> para encontrar exactamente lo que necesitas, sin complicaciones."
        ), unsafe_allow_html=True)
    with col2:
        st.markdown(feature_card(
            "✨ Asesor Virtual con IA", 
            "Nuestro agente inteligente no solo responde dudas, sino que <b>analiza el mercado en tiempo real</b>. Te guía hacia las <b>mejores oportunidades de compra</b> con recomendaciones claras y fundamentadas."
        ), unsafe_allow_html=True)
    with col3:
        st.markdown(feature_card(
            "📈 Decisiones Basadas en Datos", 
            "Deja de adivinar. Cruzamos variables clave (como el <b>kilometraje, año y depreciación</b>) para garantizar que tomes una decisión segura y que cada peso invertido <b>maximice tu rentabilidad</b>."
        ), unsafe_allow_html=True)

    st.markdown("<div style='margin: 50px 0;'></div>", unsafe_allow_html=True)

    # 3. MÉTRICAS DINÁMICAS
    total_vehiculos = f"{len(df):,}".replace(",", ".")
    marca_popular = df['brand'].mode()[0].title()
    
    st.markdown("<p style='color: #2563eb; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 15px; font-weight: 700;'>Resumen del Inventario en Tiempo Real</p>", unsafe_allow_html=True)
    
    def metric_card(title, value):
        return f"""
<div style='text-align: center; padding: 1rem 2rem;'>
<p style='color: #6b6b6b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1.5px; margin: 0 0 5px 0;'>{title}</p>
<h2 style='color: #1a1a1a; font-size: 2.2rem; margin: 0; font-weight: 700; letter-spacing: -1px;'>{value}</h2>
</div>
"""
    
    st.markdown(f"""
<div style='display: flex; justify-content: center; gap: 80px; flex-wrap: wrap;'>
    {metric_card("Stock Total", total_vehiculos)}
    {metric_card("Marca Popular", marca_popular)}
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='margin: 50px 0;'></div>", unsafe_allow_html=True)

    # 4. GRÁFICO: VOLUMEN POR MARCA (Mejorado)
    st.markdown("<p style='color: #2563eb; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 15px; font-weight: 700;'>Marcas con mayor stock</p>", unsafe_allow_html=True)
    
    df_marcas = df['brand'].value_counts().head(8).reset_index()
    df_marcas.columns = ['brand', 'count']

    # Gráfico de barras horizontales con etiquetas
    c1 = alt.Chart(df_marcas).mark_bar(
        cornerRadiusTopRight=5, cornerRadiusBottomRight=5, color='#2563eb'
    ).encode(
        x=alt.X('count', title=None, axis=alt.Axis(format='d')),
        y=alt.Y('brand', sort='-x', title=None),
        tooltip=['brand', 'count']
    ).properties(height=380)
    text = c1.mark_text(align='left', baseline='middle', dx=3, color='#4a4a4a').encode(text='count')
    
    st.altair_chart((c1 + text), width='stretch')

    # 5. SOBRE NUESTRO MVP
    st.markdown("<div style='margin-top: 60px; padding-top: 1rem;'></div>", unsafe_allow_html=True)
    st.markdown("<p style='color: #2563eb; font-size: 1.1rem; text-transform: uppercase; letter-spacing: 1px; text-align: center; margin-bottom: 30px; font-weight: 700;'>Sobre nuestro MVP</p>", unsafe_allow_html=True)
    st.markdown("""
<div style='max-width: 850px; margin: 0 auto;'>
<div style='margin-bottom: 30px;'>
<p style='font-size: 0.95rem; color: #4a4a4a; line-height: 1.6; text-align: justify;'>
<strong style='color: #1a1a1a;'>AutoInsight</strong> nace de un análisis de mercado que demostró que la depreciación de los vehículos usados está dictada drásticamente por la combinación de <b>año, kilometraje y transmisión</b>. Para que los usuarios no tengan que calcular manualmente el impacto de estas variables, construimos este MVP de catálogo con <b>Inteligencia Artificial integrada</b>, donde un asistente procesa estos datos y guía hacia compras rentables y seguras. Para probar la viabilidad y escalabilidad de esta arquitectura a nivel local, el sistema fue validado utilizando un robusto dataset de la India, cuyos precios fueron convertidos a pesos chilenos (CLP).
</p>
</div>

<div>
<p style='font-size: 0.95rem; color: #4a4a4a; line-height: 1.6; text-align: justify;'>
<strong style='color: #1a1a1a;'>Dataset:</strong> <a href='https://www.kaggle.com/datasets/mohitkumar282/used-car-dataset' target='_blank' style='color: #1a1a1a; text-decoration: underline;'>Kaggle (14.993 registros)</a><br>
<strong style='color: #1a1a1a;'>Repositorio:</strong> <a href='https://github.com/frankezu/autoinsight-app' target='_blank' style='color: #1a1a1a; text-decoration: underline;'>GitHub</a>
</p>
</div>
</div>
""", unsafe_allow_html=True)