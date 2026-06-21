import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os

# ==============================================================================
# 1. CONFIGURACIÓN DE LA INTERFAZ
# ==============================================================================
st.set_page_config(
    page_title="Sistema de Gestión de Crisis - Biobío",
    page_icon="🚨",
    layout="wide"
)

st.title("🚨 Sistema Integrado de Alertas, Mitigación y Planes de Evacuación")
st.markdown("### Centro de Operaciones de Emergencia (COE) | SIC 2026 - Grupo 5")

albergues_biobio = {
    "Concepción": "Gimnasio Municipal (Av. Collao 525) - Abierto 24/7",
    "Los Ángeles": "Liceo Comercial (Ricardo Vicuña 310) - Zona de Resguardo",
    "Talcahuano": "Coliseo La Tortuga (Blanco Encalada 450) - Centro de Acopio",
    "Coronel": "Escuela Básica Manuel Montt - Habilitado como Refugio",
    "Hualpén": "Liceo Pedro del Río Zañartu - Zona Segura de Evacuación",
    "Chiguayante": "Gimnasio Machasa - Punto de Encuentro Familiar",
    "San Pedro de la Paz": "Colegio Concepción (San Pedro) - Albergue Activo",
    "Penco": "Escuela Patricio Lynch - Zona de Resguardo Temporal",
    "Tomé": "Internado Bellavista - Centro de Atención de Emergencias",
    "Lota": "Liceo Carlos Cousiño - Zona de Seguridad Civil"
}

# ==============================================================================
# 2. CARGA ULTRA-ROBUSTA DE DATOS (MÉTODOS DE RESPALDO MÚLTIPLES)
# ==============================================================================
@st.cache_data
def inicializar_sistema():
    base_path = os.path.dirname(os.path.abspath(__file__))
    
    archivo_comunas = "Latitud - Longitud Chile.csv"
    archivo_bosques = "biobio_limpio.csv"
    
    rutas_comunas_posibles = [
        os.path.join(base_path, "data", archivo_comunas),
        os.path.join(base_path, archivo_comunas),
        archivo_comunas
    ]
    
    rutas_bosques_posibles = [
        os.path.join(base_path, "data", archivo_bosques),
        os.path.join(base_path, archivo_bosques),
        archivo_bosques
    ]
    
    df_c = None
    for r in rutas_comunas_posibles:
        if os.path.exists(r):
            df_c = pd.read_csv(r)
            break
            
    df_b = None
    for r in rutas_bosques_posibles:
        if os.path.exists(r):
            try:
                df_b = pd.read_csv(r, sep=';')
                if df_b.shape[1] <= 1:
                    df_b = pd.read_csv(r, sep=',')
            except:
                df_b = pd.read_csv(r, sep=',')
            break

    if df_c is None:
        df_c = pd.DataFrame({
            'Comuna': ['Concepción', 'Los Ángeles', 'Talcahuano', 'Coronel', 'Hualpén', 'Chiguayante', 'San Pedro de la Paz', 'Penco', 'Tomé', 'Lota'],
            'Región': ['Biobío'] * 10,
            'Provincia': ['Concepción', 'Biobío', 'Concepción', 'Concepción', 'Concepción', 'Concepción', 'Concepción', 'Concepción', 'Concepción', 'Concepción'],
            'Población Año 2017': ['223.574', '202.331', '151.749', '116.262', '91.773', '85.938', '131.808', '47.367', '54.537', '43.535'],
            'Latitud (Decimal)': [-36.8150, -37.4697, -36.7358, -36.9819, -36.7932, -36.9089, -36.8639, -36.7419, -36.6167, -37.0889],
            'Longitud (decimal)': [-73.0289, -72.3508, -73.1050, -73.1569, -73.1678, -73.0278, -73.1078, -72.9978, -72.9500, -73.1550]
        })

    if df_b is None:
        vegetacion = {
            "plantacion_forestal_ha": 875178.4,
            "bosque_nativo_ha": 597572.7,
            "bosque_mixto_ha": 51635.9,
            "humedales_ha": 10172.8,
            "bosques_total_ha": 1524387.0
        }
    else:
        df_b.columns = [c.strip() for c in df_b.columns]
        df_b['Región'] = df_b['Región'].str.strip() if 'Región' in df_b.columns else df_b.iloc[:,0].str.strip()
        
        def limpiar_numero_chileno(val):
            if pd.isna(val): return 0.0
            return float(str(val).strip().replace('.', '').replace(',', '.'))
        
        row_biobio = df_b[df_b['Región'].astype(str).str.contains('Bio')].iloc[0]
        
        p_for = row_biobio['Plantación Forestal'] if 'Plantación Forestal' in df_b.columns else 875178.4
        b_nat = row_biobio['Bosque Nativo'] if 'Bosque Nativo' in df_b.columns else (row_biobio['Bosque Native'] if 'Bosque Native' in df_b.columns else 597572.7)
        b_mix = row_biobio['Bosque Mixto'] if 'Bosque Mixto' in df_b.columns else 51635.9
        b_tot = row_biobio['Total'] if 'Total' in df_b.columns else 1524387.0
        
        vegetacion = {
            "plantacion_forestal_ha": limpiar_numero_chileno(p_for),
            "bosque_nativo_ha": limpiar_numero_chileno(b_nat),
            "bosque_mixto_ha": limpiar_numero_chileno(b_mix),
            "humedales_ha": 10172.8,
            "bosques_total_ha": limpiar_numero_chileno(b_tot)
        }

    df_c['Región_Clean'] = df_c['Región'].astype(str).str.lower()
    df_comunas_biobio = df_c[df_c['Región_Clean'].str.contains('bio', na=False)].copy()
    
    df_comunas_biobio['comuna'] = df_comunas_biobio['Comuna'].str.strip()
    df_comunas_biobio['latitud_decimal'] = pd.to_numeric(df_comunas_biobio['Latitud (Decimal)'], errors='coerce')
    df_comunas_biobio['longitud_decimal'] = pd.to_numeric(df_comunas_biobio['Longitud (decimal)'], errors='coerce')
    
    df_comunas_biobio['poblacion_2017'] = df_comunas_biobio['Población Año 2017'].astype(str).str.replace(',', '').str.replace('.', '').astype(int)
    df_comunas_biobio = df_comunas_biobio.dropna(subset=['latitud_decimal', 'longitud_decimal'])
    
    return df_comunas_biobio, vegetacion

df_comunas, datos_biobio = inicializar_sistema()

# ==============================================================================
# 3. PANEL LATERAL: CONTROLES DE CRISIS
# ==============================================================================
st.sidebar.header("🕹️ Panel de Control del Incidente")
comuna_origen = st.sidebar.selectbox("📍 Comuna del Foco Inicial", sorted(df_comunas['comuna'].unique()))

st.sidebar.markdown("---")
st.sidebar.header("🧭 Variables Atmosféricas")
dir_viento = st.sidebar.selectbox("💨 Dirección hacia donde sopla el Viento", 
                                  ["Norte", "Sur", "Este", "Oeste", "Omnidireccional (Sin control)"])
viento = st.sidebar.slider("💨 Velocidad del Viento (km/h)", 0, 120, 35)
temperatura = st.sidebar.slider("🌡️ Temperatura Ambiente (°C)", 10, 45, 34)
humedad = st.sidebar.slider("💧 Humedad Relativa (%)", 0, 100, 18)
pendiente = st.sidebar.slider("⛰️ Pendiente media del Terreno (%)", 0, 100, 12)
horas_ev = st.sidebar.slider("⏳ Ventana de Simulación (Horas)", 1, 72, 4)

# ==============================================================================
# 4. ALGORITMO MATEMÁTICO DE PROPAGACIÓN
# ==============================================================================
combustible = (
    (datos_biobio["plantacion_forestal_ha"] * 1.0) +
    (datos_biobio["bosque_mixto_ha"] * 0.8) +
    (datos_biobio["bosque_nativo_ha"] * 0.6)
) / datos_biobio["bosques_total_ha"] * 100

sequedad = 100 - humedad
ip = (0.30 * viento) + (0.30 * combustible) + (0.20 * temperatura) + (0.10 * sequedad) + (0.10 * pendiente)
ip = min(max(ip, 0), 100)

velocidad_fuego = 0.5 + ((ip / 100) * 4.0) + ((viento / 100) * 3.0)
alcance_km = velocidad_fuego * horas_ev

origen_fila = df_comunas[df_comunas['comuna'] == comuna_origen].iloc[0]
lat_o, lon_o = origen_fila['latitud_decimal'], origen_fila['longitud_decimal']

df_comunas['distancia_foco_km'] = np.sqrt((df_comunas['latitud_decimal'] - lat_o)**2 + (df_comunas['longitud_decimal'] - lon_o)**2) * 111.12
df_comunas['dif_lat'] = df_comunas['latitud_decimal'] - lat_o
df_comunas['dif_lon'] = df_comunas['longitud_decimal'] - lon_o

def evaluar_trayectoria(row):
    if row['comuna'] == comuna_origen: 
        return True
    if dir_viento == "Norte" and row['dif_lat'] >= -0.05: return True
    if dir_viento == "Sur" and row['dif_lat'] <= 0.05: return True
    if dir_viento == "Este" and row['dif_lon'] >= -0.05: return True
    if dir_viento == "Oeste" and row['dif_lon'] <= 0.05: return True
    if dir_viento == "Omnidireccional (Sin control)": return True
    return False

df_comunas['En_Trayectoria'] = df_comunas.apply(evaluar_trayectoria, axis=1)

def calcular_probabilidad_y_rango(row):
    if row['comuna'] == comuna_origen:
        return 100.0, "🔴 Alerta Roja (Extremo)"
    
    if row['En_Trayectoria']:
        alcance_real = max(alcance_km, 15.0) 
        if row['distancia_foco_km'] <= alcance_real:
            prob = 100 - ((row['distancia_foco_km'] / alcance_real) * 100)
            factor_climatico = (temperatura * 0.4) + (viento * 0.3) - (humedad * 0.2)
            prob = prob + (factor_climatico * 0.2)
            prob = min(max(prob, 5.0), 99.0)
        else:
            prob = max(10.0 - (row['distancia_foco_km'] * 0.05), 0.0)
    else:
        prob = 0.0

    if prob >= 75: return float(prob), "🔴 Alerta Roja (Extremo)"
    elif prob >= 50: return float(prob), "🟠 Alerta Amarilla (Alto)"
    elif prob >= 25: return float(prob), "🟡 Alerta Temprana Preventiva (Medio)"
    else: return float(prob), "🟢 Alerta Verde (Bajo)"

resultados = df_comunas.apply(calcular_probabilidad_y_rango, axis=1)
df_comunas['Probabilidad (%)'] = [round(r[0], 1) for r in resultados]
df_comunas['Clasificacion_Riesgo'] = [r[1] for r in resultados]

# ==============================================================================
# 5. DISEÑO DE PESTAÑAS INTERACTIVAS (MÓDULOS UX PROFESIONALES)
# ==============================================================================
tab_mapa, tab_tabla, tab_datos, tab_contexto, tab_prevencion = st.tabs([
    "🖥️ Simulador y Mapa de Crisis", 
    "📊 Propagación Estimada entre Comunas", 
    "💾 Descargar Resultado (CSV)",
    "🧪 Contexto Científico y Límites",
    "🌲 Plan Maestro Comunitario y Prevención"
])

# ------------------------------------------------------------------------------
# PESTAÑA 1: MAPA Y CONTROLES OPERATIVOS
# ------------------------------------------------------------------------------
with tab_mapa:
    comunas_afectadas = df_comunas[df_comunas['Probabilidad (%)'] >= 25]
    poblacion_afectada = comunas_afectadas['poblacion_2017'].sum()
    vividendas_afectadas = poblacion_afectada / 3.2

    m1, m2, m3, m4 = st.columns(4)
    with m1: st.metric("Índice de Gravedad (IP)", f"{ip:.1f} %")
    with m2: st.metric("Velocidad de Avance Frontal", f"{velocidad_fuego:.2f} km/h")
    with m3: st.metric("Población Civil en Riesgo", f"{poblacion_afectada:,.0f} hab")
    with m4: st.metric("Estimación de Viviendas en Riesgo", f"{vividendas_afectadas:,.0f} casas")

    st.markdown("---")
    col_mapa, col_graficos = st.columns([2, 1])

    with col_mapa:
        st.subheader("🗺️ Mapeo de Threat Territorial y Vector de Viento")
        fig_mapa = px.scatter_mapbox(
            df_comunas, lat="latitud_decimal", lon="longitud_decimal",
            color="Clasificacion_Riesgo", size="poblacion_2017",
            color_discrete_map={
                "🔴 Alerta Roja (Extremo)": "#D32F2F", "🟠 Alerta Amarilla (Alto)": "#F57C00", 
                "🟡 Alerta Temprana Preventiva (Medio)": "#FBC02D", "🟢 Alerta Verde (Bajo)": "#388E3C"
            },
            category_orders={"Clasificacion_Riesgo": ["🔴 Alerta Roja (Extremo)", "🟠 Alerta Amarilla (Alto)", "🟡 Alerta Temprana Preventiva (Medio)", "🟢 Alerta Verde (Bajo)"]},
            hover_name="comuna",
            hover_data={"Clasificacion_Riesgo": True, "distancia_foco_km": ":.2f Km", "Probabilidad (%)": True},
            zoom=7.5, center=dict(lat=lat_o, lon=lon_o),
            mapbox_style="open-street-map", height=480
        )
        fig_mapa.update_traces(hovertemplate="<b>%{hovertext}</b><br><br>Riesgo: %{customdata[0]}<br>Distancia: %{customdata[1]}<br>Probabilidad: %{customdata[2]}<br><b>Viento:</b> " + f"{viento} km/h hacia el {dir_viento}<br>")
        fig_mapa.update_layout(margin={"r":0,"t":0,"l":0,"b":0}, legend=dict(title_text="Riesgo SENAPRED", y=0.99, x=0.01, bgcolor="rgba(255, 255, 255, 0.8)"))
        st.plotly_chart(fig_mapa, use_container_width=True)

    with col_graficos:
        st.subheader("🌲 Datos forestales usados para el cálculo")
        df_veg = pd.DataFrame({
            'Tipo Cobertura': ['Plantación Forestal', 'Bosque Nativo', 'Bosque Mixto', 'Humedales'],
            'Hectáreas': [datos_biobio["plantacion_forestal_ha"], datos_biobio["bosque_nativo_ha"], datos_biobio["bosque_mixto_ha"], datos_biobio["humedales_ha"]]
        })
        fig_bar = px.bar(
            df_veg, x='Hectáreas', y='Tipo Cobertura', orientation='h',
            color='Tipo Cobertura', color_discrete_sequence=['#A12312', '#345922', '#6E8131', '#417392'],
            text='Hectáreas', height=230
        )
        fig_bar.update_traces(texttemplate='%{text:,.1f} ha', textposition='outside')
        fig_bar.update_layout(showlegend=False, xaxis_title="Superficie en Hectáreas", yaxis_title="", margin={"r":30,"t":10,"l":10,"b":10})
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")
        st.subheader("📊 Distribución Porcentual del Combustible")
        fig_pie = px.pie(
            df_veg, values='Hectáreas', names='Tipo Cobertura', color='Tipo Cobertura',
            color_discrete_sequence=['#A12312', '#345922', '#6E8131', '#417392'], height=230
        )
        fig_pie.update_layout(margin={"r":10,"t":10,"l":10,"b":10}, showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.subheader("📋 Logística Operativa y Plan de Evacuación Civil")
    col_izq, col_der = st.columns(2)
    with col_izq:
        st.markdown("### 🏃‍♂️ Rutas de Evacuación y Refugios")
        comunas_peligrosas = df_comunas[df_comunas['Probabilidad (%)'] >= 50]
        if not comunas_peligrosas.empty:
            for com in comunas_peligrosas['comuna'].unique():
                ruta_sugerida = "Eje Vial Ruta 160 Sur" if dir_viento == "Norte" else "Eje Vial Ruta 5 Sur / Autopista del Itata"
                st.markdown(f"* **{com}:** Evacuar preventivamente vía **{ruta_sugerida}**.")
                if com in albergues_biobio:
                    st.caption(f"🏠 **Albergue de Referencia:** {albergues_biobio[com]}")
        else: st.success("✓ Todos los caminos y conectividades se encuentran estables.")
    with col_der:
        st.markdown("### 🚨 Central de Comunicaciones de Emergencia")
        df_telefonos = pd.DataFrame({"Organismo": ["CONAF", "Bomberos", "SAMU", "Carabineros"], "Línea": ["130", "132", "131", "133"]})
        st.table(df_telefonos)

# ------------------------------------------------------------------------------
# PESTAÑA 2: TABLA Y ANÁLISIS DE PROPAGACIÓN INTERACTIVA
# ------------------------------------------------------------------------------
with tab_tabla:
    st.subheader("📊 Análisis Avanzado de Propagación Intercomunal")
    st.write("Visualiza la relación crítica entre la distancia geográfica y el nivel de riesgo de impacto calculado:")

    c_roja = len(df_comunas[df_comunas['Clasificacion_Riesgo'] == "🔴 Alerta Roja (Extremo)"])
    c_amarilla = len(df_comunas[df_comunas['Clasificacion_Riesgo'] == "🟠 Alerta Amarilla (Alto)"])
    c_preventiva = len(df_comunas[df_comunas['Clasificacion_Riesgo'] == "🟡 Alerta Temprana Preventiva (Medio)"])
    
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1: st.metric("🔴 Comunas en Alerta Roja", f"{c_roja} localidades")
    with kpi2: st.metric("🟠 Comunas en Alerta Amarilla", f"{c_amarilla} localidades")
    with kpi3: st.metric("🟡 Comunas en Alerta Temprana", f"{c_preventiva} localidades")
    
    st.markdown("---")
    col_tab_izq, col_tab_der = st.columns([1, 1])
    
    df_tabla_limpia = df_comunas[['comuna', 'Provincia', 'poblacion_2017', 'distancia_foco_km', 'Probabilidad (%)', 'Clasificacion_Riesgo']].sort_values(by='Probabilidad (%)', ascending=False)
    df_tabla_limpia.columns = ['Comuna', 'Provincia', 'Población (Censo)', 'Distancia al Foco (Km)', 'Probabilidad de Impacto', 'Nivel de Riesgo']

    with col_tab_izq:
        st.markdown("#### 📈 Matriz Analítica: Distancia vs Probabilidad")
        fig_scatter = px.scatter(
            df_tabla_limpia, x="Distancia al Foco (Km)", y="Probabilidad de Impacto",
            color="Nivel de Riesgo", size="Población (Censo)",
            color_discrete_map={
                "🔴 Alerta Roja (Extremo)": "#D32F2F", "🟠 Alerta Amarilla (Alto)": "#F57C00",
                "🟡 Alerta Temprana Preventiva (Medio)": "#FBC02D", "🟢 Alerta Verde (Bajo)": "#388E3C"
            },
            hover_name="Comuna", height=420
        )
        fig_scatter.update_layout(xaxis_title="Distancia Geodésica al Foco (Km)", yaxis_title="Probabilidad de Afectación (%)", margin={"t":10,"b":10})
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_tab_der:
        st.markdown("#### 📋 Registro Detallado Territorial (Filtro Activo)")
        st.dataframe(df_tabla_limpia, use_container_width=True, hide_index=True, height=420)

with tab_datos:
    st.subheader("💾 Exportación de Reportes Técnicos para Autoridades")
    csv_data = df_tabla_limpia.to_csv(index=False, sep=';').encode('utf-8-sig')
    st.download_button(
        label="📥 Descargar resultado en formato CSV para Excel",
        data=csv_data,
        file_name=f"simulacion_incendio_{comuna_origen}.csv",
        mime="text/csv"
    )

# ------------------------------------------------------------------------------
# PESTAÑA 4: CONTEXTO CIENTÍFICO
# ------------------------------------------------------------------------------
with tab_contexto:
    st.subheader("🧪 Fundamentos del Simulador Técnico")
    st.info("💡 **Marco de Referencia:** Este ecosistema digital modela el comportamiento del fuego cruzando factores meteorológicos cinéticos con la biomasa de la Región del Biobío para asistir la toma de decisiones del COE.")
    
    st.markdown("### 🗺️ Contexto Regional: Biobío en Cifras")
    met1, met2, met3, met4 = st.columns(4)
    with met1: st.metric("🔥 Plantación Forestal", "875.178 ha", help="Combustible de mayor riesgo por continuidad vertical y horizontal.")
    with met2: st.metric("🌿 Bosque Nativo", "597.572 ha", help="Ponderación media de combustible forestal.")
    with met3: st.metric("🌱 Bosque Mixto", "51.635 ha", help="Riesgo intermedio entre nativo y plantaciones.")
    with met4: st.metric("💧 Humedales", "10.172 ha", help="Barreras naturales de baja combustibilidad.")
    
    st.caption("🔍 **Superficie total bajo análisis:** 2.399.067 ha | **Entidades modeladas:** 33 Comunas con coordenadas geodésicas y densidades del INE.")

    st.markdown("---")
    st.markdown("### 🔬 Base Científica: Ecuación Estándar de Rothermel (1972)")
    st.latex(r"R = \frac{I_R \cdot \xi \cdot (1 + \Phi_w + \Phi_s)}{\rho_b \cdot \epsilon \cdot Q_{ig}}")
    
    exp1, exp2 = st.columns(2)
    with exp1:
        st.markdown(r"""
        * **$R$:** Velocidad de propagación frontal.
        * **$I_R$:** Intensidad de reacción química.
        * **$\xi$:** Eficiencia de propagación.
        * **$\Phi_w$:** Factor de empuje por Viento.
        """)
    with exp2:
        st.markdown(r"""
        * **$\Phi_s$:** Factor de empuje por Pendiente del terreno.
        * **$\rho_b$:** Densidad aparente del combustible.
        * **$\epsilon$:** Factor de calentamiento efectivo.
        * **$Q_{ig}$:** Energía de ignición (pirolisis vegetal).
        """)

    st.markdown("---")
    col_analisis_1, col_analisis_2 = st.columns(2)
    with col_analisis_1:
        st.success(r"""### ✓ Implementación del Simulador
* **Optimización en Tiempo Real:** Simplificamos los fluidos moleculares a un sistema matricial ponderado de fácil lectura.
* **Visualización Ágil:** Interfaz interactiva instantánea sin requerir parámetros de laboratorio complejos.
* **Escalabilidad:** Diseñado para conectarse directamente con APIs de estaciones meteorológicas.""")
    with col_analisis_2:
        st.error(r"""### ✗ Limitaciones del Modelo
* **Propagación Uniforme:** El alcance asume una forma radial uniforme sin considerar corredores microclimáticos locales.
* **Falta de Pack:** No incluye la densidad de empaquetamiento ni la humedad foliar fina del material vegetal muerto.
* **Sin Mitigación Dinámica:** No considera el impacto de bomberos, brigadas terrestres ni aeronaves de combate.""")

# ------------------------------------------------------------------------------
# PESTAÑA 5: PLAN DE PREVENCIÓN
# ------------------------------------------------------------------------------
with tab_prevencion:
    st.subheader("🌲 Institucionalidad y Escala de Alertas SENAPRED / CONAF")
    st.write("El sistema clasifica automáticamente el riesgo territorial utilizando los colores oficiales de emergencia de Chile:")
    
    st.error(r"""### 🔴 Alerta Roja (Impacto: 75% - 100%) — Estado Extremo
**Condición:** Amenaza inminente a vidas humanas, viviendas e infraestructura crítica. El viento $\ge 20\text{ km/h}$ y humedad $< 20\%$ gatillan el **'Botón Rojo'** de CONAF.
**Acción COE:** Evacuación obligatoria inmediata vía mensajería SAE y despliegue total de recursos aéreos y terrestres.""")
             
    st.warning(r"""### 🟠 Alerta Amarilla (Impacto: 50% - 74%) — Estado Alto
**Condición:** Siniestro con alta tasa de crecimiento que amenaza superar la capacidad local de control.
**Acción COE:** Alistamiento preventivo de brigadas de relevo y preparación de apoyo logístico interprovincial.""")
               
    st.info(r"""### 🟡 Alerta Temprana Preventiva (Impacto: 25% - 49%) — Estado Medio
**Condición:** Estado de anticipación coordinada ante alertas meteorológicas extremas.
**Acción COE:** Refuerzo de monitoreo continuo, patrullajes de vigías forestales y prohibición de uso de herramientas térmicas.""")
             
    st.success(r"""### 🟢 Alerta Verde (Impacto: 0% - 24%) — Estado Bajo
**Condición:** Escenario bajo control técnico o zona fuera del cono geométrico del vector del viento.
**Acción COE:** Monitoreo estándar de turnos rutinarios.""")

    st.markdown("---")
    st.markdown("### 🎛️ Manual Interactivo: Las 6 Variables Críticas de Control")
    
    with st.expander("💨 Velocidad del Viento (Peso: 0.30)"):
        st.markdown(r"""
        **Comportamiento Físico:** Factor cinético principal. Aporta oxígeno a la combustión, deseca la vegetación y genera *spotting* (brasas transportadas a distancia que crean focos secundarios).
        * 🟢 **0 – 20 km/h:** Controlable por brigadas terrestres.
        * 🟡 **20 – 60 km/h:** Avance moderado, requiere combate combinado.
        * 🔴 **60+ km/h:** Frente autónomo incontrolable.
        """)
        
    with st.expander("🌡️ Temperatura Ambiente (Peso: 0.20)"):
        st.markdown(r"""
        **Comportamiento Físico:** Activa la pirolisis celular del material vegetal. Por cada 10 °C adicionales, la velocidad de avance del frente se incrementa hasta un 40%.
        * 🟢 **10 – 22 °C:** Riesgo bajo.
        * 🟡 **22 – 35 °C:** Riesgo moderado.
        * 🔴 **35+ °C:** Ignición acelerada de vegetación fina.
        """)
        
    with st.expander("💧 Humedad Relativa (Peso: 0.10 Inverso)"):
        st.markdown(r"""
        **Comportamiento Físico:** Modulado en el código como $\text{Sequedad} = 100 - \text{HR}$. Bajo el 25% la biomasa pierde su resistencia térmica molecular.
        * 🔴 **0 – 25 %:** Riesgo Extremo (Arde incluso material verde).
        * 🟡 **25 – 50 %:** Riesgo Moderado.
        * 🟢 **50+ %:** Riesgo Bajo.
        """)
        
    with st.expander("⛰️ Pendiente del Terreno (Peso: 0.10)"):
        st.markdown(r"""
        **Comportamiento Físico:** Emula el factor $\Phi_s$ de Rothermel. En laderas pronunciadas, las llamas calientan la vegetación superior por radiación directa, haciendo que el fuego ascienda hasta **4 veces más rápido**.
        * 🟢 **0 – 30 %:** Terreno Accesible.
        * 🟡 **30 – 65 %:** Terreno Difícil.
        * 🔴 **65+ %:** Inaccesible para brigadas terrestres.
        """)

    with st.expander("⏳ Tiempo de propagación (Ventana de Simulación)"):
        st.markdown(r"""
        **Ecuación Lineal Directa:** Multiplica el alcance geodésico total: $\text{Alcance (km)} = \text{Velocidad} \times \text{Tiempo}$.
        * 🟢 **1 – 6 h:** Ventana inicial crítica para contención rápida.
        * 🟡 **6 – 24 h:** Incendio activo con propagación entre comunas.
        * 🔴 **24+ h:** Siniestro masivo de escala provincial.
        """)

    with st.expander("📍 Comuna de origen y Enfoque Geográfico"):
        st.markdown(r"""
        **Comportamiento:** Define el epicentro geográfico. El simulador calcula el cono basándose en distancias euclidianas. Las zonas costeras como *Arauco* o *Lebu* tienen mayor recurrencia histórica debido a la fuerte densidad e influencia de vientos marinos.
        """)

    with st.expander("🌲 Carga de Combustible y Biomasa Forestal (Peso: 0.30)"):
        st.markdown(r"""
        **Comportamiento Físico:** Representa la continuidad de la biomasa disponible para arder. Las plantaciones de monocultivo (pino/eucalipto) tienen mayor continuidad vertical y horizontal, acelerando la propagación frente al bosque nativo o los humedales que actúan como barreras húmedas.
        * 🔴 **Plantaciones Forestales:** Combustión de alta intensidad y rápida propagación.
        * 🟡 **Bosque Mixto / Nativo:** Combustión moderada dependiente del estrés hídrico.
        * 🟢 **Humedales:** Zonas de amortiguación natural con baja susceptibilidad de ignición.
        """)
