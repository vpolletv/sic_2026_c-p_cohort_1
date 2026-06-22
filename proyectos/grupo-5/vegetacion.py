import streamlit as st
import pandas as pd
import plotly.express as px

# Ejecutar en PowerShell, ejemplo:
# & "C:\Users\lobot\AppData\Local\Programs\Python\Python314\python.exe" -m streamlit run vegetacion_ocupacion.py

# =========================================================
# CONFIGURACIÓN GENERAL
# =========================================================

st.set_page_config(
    page_title="Simulador de Combustibilidad Vegetal",
    page_icon="🌲",
    layout="wide"
)

st.title("🌲 Simulador Educativo de Combustibilidad Vegetal")
st.markdown("### Análisis territorial basado en coberturas vegetales CONAF")

# =========================================================
# SIDEBAR - CARGA DE ARCHIVO
# =========================================================

st.sidebar.header("📂 Cargar archivo CONAF")

archivo = st.sidebar.file_uploader(
    "Sube el Excel con hojas regionales/comunales",
    type=["xlsx"]
)

# =========================================================
# INTRODUCCIÓN SOLO ANTES DE CARGAR ARCHIVO
# =========================================================

if archivo is None:
    st.info("Carga un archivo Excel para iniciar el análisis territorial.")

    st.markdown("""
## Introducción

Los incendios forestales dependen de la interacción entre condiciones meteorológicas, topografía, fuentes de ignición y disponibilidad de combustible vegetal. Este simulador se concentra únicamente en este último componente: la vegetación disponible en el territorio.

La herramienta utiliza superficies de coberturas vegetales asociadas a bases de datos de CONAF para estimar un **índice educativo de ocupación combustible vegetal**. Su objetivo no es predecir incendios reales, sino mostrar qué territorios poseen una mayor proporción de coberturas potencialmente combustibles dentro de su propia superficie analizada.

Esto es importante porque no basta con comparar hectáreas absolutas. Una región o comuna grande puede tener más vegetación total solo por su tamaño. Por eso, este modelo trabaja con una **ocupación relativa del territorio**, permitiendo comparar comunas o regiones de distinto tamaño de forma más justa.

## Fundamento científico

La vegetación actúa como combustible en los incendios forestales. Su comportamiento frente al fuego depende de factores como la carga de biomasa, la continuidad del combustible, la presencia de material fino seco, la humedad de la vegetación y la estructura del paisaje.

Las plantaciones forestales, matorrales y praderas pueden favorecer la propagación cuando presentan continuidad de combustible o material fino disponible. En cambio, humedales y cuerpos de agua reducen la continuidad del combustible y pueden actuar como barreras naturales.

## Alcance del modelo

El resultado debe interpretarse como un **indicador relativo de combustibilidad vegetal**, no como una probabilidad real de incendio. Para estimar riesgo real sería necesario incorporar temperatura, humedad, viento, pendiente, exposición solar, cercanía a zonas urbanas, población expuesta, historial de incendios y fuentes de ignición humana.

## Metodología general

El modelo calcula primero un índice combustible ponderado según tipo de cobertura vegetal. Luego divide ese valor por la superficie total analizada del territorio. Así se obtiene una medida proporcional, es decir, una aproximación de cuánta carga combustible existe en relación con el tamaño del propio territorio.

De esta forma, una comuna pequeña puede obtener un valor alto si gran parte de su superficie está ocupada por plantaciones, matorrales o praderas. Del mismo modo, una comuna grande puede obtener un valor menor si su cobertura combustible ocupa una proporción más reducida del territorio analizado.

## Referencias APA 7

Corporación Nacional Forestal. (2024). *Análisis nacional de riesgo de incendios forestales y zonas de interfaz*. CONAF.

Corporación Nacional Forestal. (2026). *Situación actual y pronóstico de incendios*. CONAF.

Food and Agriculture Organization. (s. f.). *Guidelines on fire management in temperate and boreal forests*. FAO.

Food and Agriculture Organization. (s. f.). *Vegetation fire management*. FAO.

Ortega, M., & Paula, S. (2018). *Inflamabilidad a escala de planta, ecosistema y paisaje*. Chile Forestal, Corporación Nacional Forestal.
""")

    st.stop()

# =========================================================
# COLUMNAS REQUERIDAS
# =========================================================

columnas_requeridas = [
    "Comuna",
    "Plantaciones_ha",
    "Bosque_Nativo_ha",
    "Bosque_Mixto_ha",
    "Matorral_ha",
    "Matorral_Arborescente_ha",
    "Matorral_Pradera_ha",
    "Praderas_ha",
    "Humedales_ha",
    "Agua_ha"
]

columnas_superficie = columnas_requeridas[1:]

# =========================================================
# FUNCIONES
# =========================================================

def cargar_excel_multihoja(archivo):
    hojas = pd.read_excel(archivo, sheet_name=None)
    lista = []

    for nombre, df_hoja in hojas.items():
        df_hoja.columns = df_hoja.columns.astype(str).str.strip()
        df_hoja = df_hoja.dropna(how="all")

        if df_hoja.empty:
            continue

        if "Región" in df_hoja.columns:
            df_hoja = df_hoja.rename(columns={"Región": "Comuna"})

        if "Comuna" in df_hoja.columns:
            lista.append(df_hoja)

    if not lista:
        return pd.DataFrame()

    df_final = pd.concat(lista, ignore_index=True)
    df_final.columns = df_final.columns.astype(str).str.strip()
    return df_final


def limpiar_numero(valor):
    if pd.isna(valor):
        return 0.0

    if isinstance(valor, (int, float)):
        return float(valor)

    valor = str(valor).strip()
    valor = valor.replace("ha", "").strip()

    if "," in valor:
        valor = valor.replace(".", "").replace(",", ".")
    else:
        valor = valor.replace(",", "")

    try:
        return float(valor)
    except Exception:
        return 0.0


def clasificar_ocupacion(valor):
    """Clasificación del índice de ocupación combustible, en escala 0 a 100."""
    if valor >= 75:
        return "🔴 Muy alto"
    elif valor >= 50:
        return "🟠 Alto"
    elif valor >= 25:
        return "🟡 Medio"
    else:
        return "🟢 Bajo"

# =========================================================
# CARGA Y VALIDACIÓN DEL EXCEL
# =========================================================

df = cargar_excel_multihoja(archivo)

if df.empty:
    st.error("No se pudo leer información válida desde el Excel.")
    st.stop()

faltantes = [c for c in columnas_requeridas if c not in df.columns]

if faltantes:
    st.error("Faltan columnas necesarias:")
    st.write(faltantes)
    st.write("Columnas detectadas:")
    st.write(df.columns.tolist())
    st.stop()

df = df[columnas_requeridas].copy()
df["Comuna"] = df["Comuna"].astype(str).str.strip()

for col in columnas_requeridas[1:]:
    df[col] = df[col].apply(limpiar_numero)

df = df.drop_duplicates(subset=["Comuna"])

# =========================================================
# CÁLCULO DEL ÍNDICE DE OCUPACIÓN COMBUSTIBLE
# =========================================================

# Índice bruto: suma ponderada de coberturas combustibles.
df["Combustible_Bruto"] = (
    df["Plantaciones_ha"] * 1.00 +
    df["Matorral_ha"] * 0.80 +
    df["Matorral_Arborescente_ha"] * 0.75 +
    df["Matorral_Pradera_ha"] * 0.65 +
    df["Praderas_ha"] * 0.50 +
    df["Bosque_Mixto_ha"] * 0.60 +
    df["Bosque_Nativo_ha"] * 0.40
)

# Humedales y agua se consideran barreras/reductores de continuidad del combustible.
df["Barreras_Naturales"] = (
    df["Humedales_ha"] * 0.90 +
    df["Agua_ha"] * 1.00
)

# Índice neto: combustible menos barreras naturales.
df["Indice_Combustible_Neto"] = df["Combustible_Bruto"] - df["Barreras_Naturales"]
df["Indice_Combustible_Neto"] = df["Indice_Combustible_Neto"].clip(lower=0)

# Superficie analizada: suma de todas las coberturas usadas en el modelo.
df["Superficie_Total_Analizada"] = df[columnas_superficie].sum(axis=1)

# Índice proporcional: evita que territorios más grandes ganen solo por tamaño.
df["Indice_Ocupacion_Combustible"] = 0.0
mask_superficie = df["Superficie_Total_Analizada"] > 0
df.loc[mask_superficie, "Indice_Ocupacion_Combustible"] = (
    df.loc[mask_superficie, "Indice_Combustible_Neto"] /
    df.loc[mask_superficie, "Superficie_Total_Analizada"]
) * 100

# Para que visualmente nunca pase de 100 en caso de datos raros.
df["Indice_Ocupacion_Combustible"] = df["Indice_Ocupacion_Combustible"].clip(lower=0, upper=100)

df["Nivel"] = df["Indice_Ocupacion_Combustible"].apply(clasificar_ocupacion)

# =========================================================
# SELECTOR DE TERRITORIO
# =========================================================

opciones = df["Comuna"].tolist()

opcion = st.sidebar.selectbox(
    "📍 Selecciona territorio",
    opciones,
    index=0
)

fila = df[df["Comuna"] == opcion].iloc[0]

# =========================================================
# RESUMEN SUPERIOR
# =========================================================

st.markdown("---")
st.subheader(f"📍 Territorio seleccionado: {opcion}")

st.caption(
    "El índice muestra la proporción de ocupación combustible del territorio seleccionado. "
    "No representa probabilidad real de incendio, sino composición vegetal potencialmente combustible."
)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric("Ocupación combustible", f"{fila['Indice_Ocupacion_Combustible']:.1f}%")

with m2:
    st.metric("Nivel estimado", fila["Nivel"])

with m3:
    st.metric("Combustible bruto", f"{fila['Combustible_Bruto']:,.1f}")

with m4:
    st.metric("Superficie analizada", f"{fila['Superficie_Total_Analizada']:,.1f} ha")

# =========================================================
# DATOS PARA GRÁFICOS
# =========================================================

datos_cobertura = pd.DataFrame({
    "Cobertura": [
        "Plantaciones",
        "Bosque Nativo",
        "Bosque Mixto",
        "Matorral",
        "Matorral Arborescente",
        "Matorral-Pradera",
        "Praderas",
        "Humedales",
        "Agua"
    ],
    "Hectáreas": [
        fila["Plantaciones_ha"],
        fila["Bosque_Nativo_ha"],
        fila["Bosque_Mixto_ha"],
        fila["Matorral_ha"],
        fila["Matorral_Arborescente_ha"],
        fila["Matorral_Pradera_ha"],
        fila["Praderas_ha"],
        fila["Humedales_ha"],
        fila["Agua_ha"]
    ]
})

# =========================================================
# PESTAÑAS
# =========================================================

tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🧪 Resumen",
    "📋 Tabla",
    "📊 Gráficos",
    "🔥 Ranking",
    "📚 Metodología",
    "💾 Descargar"
])

# =========================================================
# TAB 1 - RESUMEN
# =========================================================

with tab1:
    st.subheader(f"🧪 Interpretación técnica: {opcion}")

    if fila["Nivel"] == "🔴 Muy alto":
        st.error(f"**{opcion}** presenta una ocupación combustible vegetal muy alta dentro de su superficie analizada.")
    elif fila["Nivel"] == "🟠 Alto":
        st.warning(f"**{opcion}** presenta una ocupación combustible vegetal alta dentro de su superficie analizada.")
    elif fila["Nivel"] == "🟡 Medio":
        st.info(f"**{opcion}** presenta una ocupación combustible vegetal media dentro de su superficie analizada.")
    else:
        st.success(f"**{opcion}** presenta una ocupación combustible vegetal baja dentro de su superficie analizada.")

    st.markdown("""
El resultado no compara hectáreas brutas, porque eso favorecería automáticamente a los territorios más grandes. En esta versión, el índice combustible neto se divide por la superficie total analizada del propio territorio.

Esto permite que comunas pequeñas y grandes puedan compararse de forma más justa. Por ejemplo, una comuna con menor superficie total puede presentar un nivel alto si gran parte de su territorio está ocupado por plantaciones, matorrales o praderas.

Este resultado debe entenderse como una comparación relativa de composición vegetal, no como una predicción exacta de incendios.
""")

    st.markdown("### Fórmula utilizada")

    st.code("""
Índice combustible neto =
Plantaciones*1.00
+ Matorral*0.80
+ Matorral Arborescente*0.75
+ Matorral-Pradera*0.65
+ Praderas*0.50
+ Bosque Mixto*0.60
+ Bosque Nativo*0.40
- Humedales*0.90
- Agua*1.00

Superficie total analizada =
Plantaciones + Bosque Nativo + Bosque Mixto + Matorral
+ Matorral Arborescente + Matorral-Pradera + Praderas
+ Humedales + Agua

Índice de ocupación combustible =
(Índice combustible neto / Superficie total analizada) * 100
""")

# =========================================================
# TAB 2 - TABLA
# =========================================================

with tab2:
    st.subheader(f"📋 Tabla de coberturas: {opcion}")
    st.dataframe(datos_cobertura, use_container_width=True, hide_index=True)

    st.subheader("📋 Base completa procesada")
    columnas_mostrar = [
        "Comuna",
        "Superficie_Total_Analizada",
        "Combustible_Bruto",
        "Barreras_Naturales",
        "Indice_Combustible_Neto",
        "Indice_Ocupacion_Combustible",
        "Nivel"
    ] + columnas_superficie

    st.dataframe(df[columnas_mostrar], use_container_width=True, hide_index=True)

# =========================================================
# TAB 3 - GRÁFICOS
# =========================================================

with tab3:
    st.subheader(f"📊 Gráficos de cobertura vegetal: {opcion}")

    col1, col2 = st.columns(2)

    with col1:
        fig_pie = px.pie(
            datos_cobertura,
            names="Cobertura",
            values="Hectáreas",
            hole=0.35,
            title=f"Distribución vegetal - {opcion}"
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        fig_bar = px.bar(
            datos_cobertura.sort_values("Hectáreas"),
            x="Hectáreas",
            y="Cobertura",
            orientation="h",
            text="Hectáreas",
            title=f"Superficie por cobertura - {opcion}"
        )
        fig_bar.update_traces(texttemplate="%{text:,.1f}", textposition="outside")
        fig_bar.update_layout(height=500)
        st.plotly_chart(fig_bar, use_container_width=True)

    st.subheader("📊 Comparación de indicadores")
    indicadores = pd.DataFrame({
        "Indicador": [
            "Combustible bruto",
            "Barreras naturales",
            "Índice combustible neto",
            "Índice de ocupación combustible (%)"
        ],
        "Valor": [
            fila["Combustible_Bruto"],
            fila["Barreras_Naturales"],
            fila["Indice_Combustible_Neto"],
            fila["Indice_Ocupacion_Combustible"]
        ]
    })

    fig_ind = px.bar(
        indicadores,
        x="Indicador",
        y="Valor",
        text="Valor",
        title=f"Indicadores del modelo - {opcion}"
    )
    fig_ind.update_traces(texttemplate="%{text:,.1f}", textposition="outside")
    st.plotly_chart(fig_ind, use_container_width=True)

# =========================================================
# TAB 4 - RANKING
# =========================================================

with tab4:
    st.subheader("🔥 Ranking por ocupación combustible vegetal")

    ranking = df.sort_values("Indice_Ocupacion_Combustible", ascending=False).copy()
    ranking["Indice_Ocupacion_Combustible"] = ranking["Indice_Ocupacion_Combustible"].round(1)

    st.dataframe(
        ranking[["Comuna", "Indice_Ocupacion_Combustible", "Nivel"]],
        use_container_width=True,
        hide_index=True
    )

    fig_rank = px.bar(
        ranking.sort_values("Indice_Ocupacion_Combustible"),
        x="Indice_Ocupacion_Combustible",
        y="Comuna",
        color="Nivel",
        orientation="h",
        text="Indice_Ocupacion_Combustible",
        title="Ranking de ocupación combustible vegetal",
        color_discrete_map={
            "🔴 Muy alto": "#D32F2F",
            "🟠 Alto": "#F57C00",
            "🟡 Medio": "#FBC02D",
            "🟢 Bajo": "#388E3C"
        }
    )

    fig_rank.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig_rank.update_layout(height=900)
    st.plotly_chart(fig_rank, use_container_width=True)

# =========================================================
# TAB 5 - METODOLOGÍA
# =========================================================

with tab5:
    st.subheader("📚 Fundamento metodológico y científico")

    st.markdown("""
### ¿Qué mide este simulador?

El simulador mide la **ocupación combustible vegetal relativa** de un territorio. No se limita a sumar hectáreas, porque una región o comuna de mayor tamaño siempre tendería a obtener valores más altos. En cambio, calcula qué proporción de la superficie analizada está ocupada por coberturas vegetales con distinto potencial combustible.

Por esto, la comparación es más justa entre territorios grandes y pequeños. Una comuna pequeña puede tener un valor alto si gran parte de su superficie está cubierta por plantaciones, matorrales o praderas. Una comuna más grande puede obtener un valor menor si posee más coberturas húmedas, agua o menor proporción de combustible continuo.

### ¿Por qué se ponderan distinto las coberturas?

Las coberturas vegetales no tienen el mismo comportamiento frente al fuego. Las plantaciones, matorrales y praderas pueden presentar mayor continuidad de combustible o mayor presencia de material fino seco, lo que favorece la ignición y la propagación superficial.

El bosque nativo recibe una ponderación menor porque suele presentar mayor heterogeneidad estructural y condiciones de humedad relativamente más favorables que una plantación homogénea. Esto no significa que no pueda quemarse, sino que en este modelo se considera con una combustibilidad relativa menor.

Los humedales y cuerpos de agua reducen el índice porque actúan como barreras naturales: interrumpen la continuidad del combustible y mantienen mayores niveles de humedad.
""")

    st.markdown("### Fórmula utilizada")

    st.code("""
Índice combustible neto =
Plantaciones*1.00
+ Matorral*0.80
+ Matorral Arborescente*0.75
+ Matorral-Pradera*0.65
+ Praderas*0.50
+ Bosque Mixto*0.60
+ Bosque Nativo*0.40
- Humedales*0.90
- Agua*1.00

Superficie total analizada =
Plantaciones + Bosque Nativo + Bosque Mixto + Matorral
+ Matorral Arborescente + Matorral-Pradera + Praderas
+ Humedales + Agua

Índice de ocupación combustible =
(Índice combustible neto / Superficie total analizada) * 100
""")

    st.markdown("""
### Interpretación

El resultado se expresa en porcentaje.

- **0% a 24,9%:** baja ocupación combustible.
- **25% a 49,9%:** ocupación combustible media.
- **50% a 74,9%:** ocupación combustible alta.
- **75% a 100%:** ocupación combustible muy alta.

Un valor elevado no significa que necesariamente ocurrirá un incendio. Significa que, dentro de la superficie analizada, existe una mayor proporción de coberturas vegetales que pueden actuar como combustible bajo condiciones favorables.

### Limitaciones del modelo

Este modelo es educativo y experimental. No calcula riesgo real de incendio, ya que no incorpora variables meteorológicas, topográficas ni humanas. Para una versión más completa podrían integrarse temperatura, humedad atmosférica, humedad del combustible, viento, pendiente, exposición solar, distancia a zonas urbanas, población expuesta, historial de incendios y fuentes de ignición humana.

### Nota metodológica

Se descartó la comparación directa con la Región del Biobío como valor base, porque las comunas analizadas pueden formar parte de la misma región. En su lugar, se utiliza un índice independiente por territorio, basado en la proporción de ocupación combustible dentro de su propia superficie analizada. Esto evita confusiones como que una comuna aparezca con más de 100% respecto a la región completa.

Las ponderaciones corresponden a una escala relativa construida para fines educativos a partir de literatura sobre comportamiento del fuego y características generales de inflamabilidad de las coberturas vegetales. No corresponden a coeficientes oficiales de CONAF ni representan un modelo operacional de predicción de incendios.

### Referencias APA 7

Corporación Nacional Forestal. (2024). *Análisis nacional de riesgo de incendios forestales y zonas de interfaz*. CONAF.

Corporación Nacional Forestal. (2026). *Situación actual y pronóstico de incendios*. CONAF.

Food and Agriculture Organization. (s. f.). *Guidelines on fire management in temperate and boreal forests*. FAO.

Food and Agriculture Organization. (s. f.). *Vegetation fire management*. FAO.

Ortega, M., & Paula, S. (2018). *Inflamabilidad a escala de planta, ecosistema y paisaje*. Chile Forestal, Corporación Nacional Forestal.
""")

# =========================================================
# TAB 6 - DESCARGA
# =========================================================

with tab6:
    st.subheader("💾 Descargar datos procesados")

    csv = df.to_csv(index=False, sep=";").encode("utf-8-sig")

    st.download_button(
        label="📥 Descargar CSV procesado",
        data=csv,
        file_name="conaf_combustible_ocupacion_procesado.csv",
        mime="text/csv"
    )
