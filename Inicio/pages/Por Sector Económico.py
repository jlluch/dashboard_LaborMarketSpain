import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import geopandas as gpd
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import cargar_datos, cargar_geodatos

st.set_page_config(
    page_title="Análisis por Sector Económico",
    page_icon="🏭", 
    layout="wide"
)


st.title("🏭 Análisis del Mercado Laboral por Sector Económico")

st.markdown("### Período 2010-2025")

st.markdown("""
<div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
    <h4>🎯 Objetivos a analizar</h4>
    <ul>
        <li><strong>Evolución sectorial:</strong> Comparativa de la evolución de contratos entre Servicios, Industria, Construcción y Agricultura</li>
        <li><strong>Análisis de participación:</strong> Peso relativo de cada sector en el mercado laboral español</li>
        <li><strong>Contratos vs Demanda:</strong> Ratio de eficiencia entre contratos generados y demandantes de empleo por sector</li>
        <li><strong>Tendencias temporales:</strong> Identificación de patrones estacionales y cambios estructurales</li>
        <li><strong>Distribución geográfica:</strong> Análisis de la concentración sectorial por regiones</li>
    </ul>
</div>
""", unsafe_allow_html=True)


st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)


# ---------------------------
# CARGA DE DATOS CON INDICADOR
# ---------------------------
df = cargar_datos()
gdf_ccaa = cargar_geodatos()

# ---------------------------
# EQUIVALENCIAS DE PROVINCIAS
# ---------------------------
equivalencias_provincias = {
    'Almería': 'Almería', 'Cádiz': 'Cádiz', 'Córdoba': 'Córdoba', 'Granada': 'Granada',
    'Huelva': 'Huelva', 'Jaén': 'Jaén', 'Málaga': 'Málaga', 'Sevilla': 'Sevilla',
    'Huesca': 'Huesca', 'Teruel': 'Teruel', 'Zaragoza': 'Zaragoza', 'Asturias': 'Asturias',
    'Balears, Illes': 'Illes Balears', 'Palmas, Las': 'Las Palmas',
    'Santa Cruz de Tenerife': 'Santa Cruz de Tenerife', 'Cantabria': 'Cantabria',
    'Ávila': 'Ávila', 'Burgos': 'Burgos', 'León': 'León', 'Palencia': 'Palencia',
    'Salamanca': 'Salamanca', 'Segovia': 'Segovia', 'Soria': 'Soria', 'Valladolid': 'Valladolid',
    'Zamora': 'Zamora', 'Albacete': 'Albacete', 'Ciudad Real': 'Ciudad Real', 'Cuenca': 'Cuenca',
    'Guadalajara': 'Guadalajara', 'Toledo': 'Toledo', 'Barcelona': 'Barcelona',
    'Girona': 'Girona', 'Lleida': 'Lleida', 'Tarragona': 'Tarragona',
    'Alicante/Alacant': 'Alacant/Alicante', 'Castellón/Castelló': 'Castelló/Castellón',
    'Valencia/Valéncia': 'València/Valencia', 'Badajoz': 'Badajoz', 'Cáceres': 'Cáceres',
    'Coruña, A': 'A Coruña', 'Lugo': 'Lugo', 'Ourense': 'Ourense', 'Pontevedra': 'Pontevedra',
    'Madrid': 'Madrid', 'Murcia': 'Murcia', 'Navarra': 'Navarra', 'Araba/Álava': 'Araba/Álava',
    'Gipuzkoa': 'Gipuzkoa', 'Bizkaia': 'Bizkaia', 'Rioja, La': 'La Rioja',
    'Ceuta': 'Ceuta', 'Melilla': 'Melilla'
}

# Configuración de sectores y colores
sectores_config = {
    'Servicios': {
        'columna': 'contratos__servicios',
        'demandantes': 'dtes_empleo_servicios',
        'color': '#1f77b4',
        'icon': '💼'
    },
    'Agricultura': {
        'columna': 'contratos__agricultura',
        'demandantes': 'dtes_empleoagricultura',
        'color': '#2ca02c',
        'icon': '🌾'
    },
    'Industria': {
        'columna': 'contratos__industria',
        'demandantes': 'dtes_empleo_industria',
        'color': '#ff7f0e',
        'icon': '🏭'
    },
    'Construcción': {
        'columna': 'contratos_construcción',
        'demandantes': 'dtes_empleo_construcción',
        'color': '#d62728',
        'icon': '🏗️'
    }
}


st.subheader("Evolución Anual de Contratos por Sector")

col1, col2 = st.columns([2, 1])
with col1:
    años_seleccionados = st.slider(
        "🗓️ Selecciona el rango de años",
        min_value=int(df['año'].min()),
        max_value=int(df['año'].max()),
        value=(2015, int(df['año'].max())),
        step=1
    )
with col2:
    vista_tipo = st.radio("🔍 Tipo de visualización", ["Absolutos", "Porcentajes"], index=0)

df_evolucion = df[df['año'].between(años_seleccionados[0], años_seleccionados[1])].groupby("año").agg({
    config['columna']: 'sum' for config in sectores_config.values()
}).reset_index()

for sector, config in sectores_config.items():
    df_evolucion[sector] = df_evolucion[config['columna']]

if vista_tipo == "Absolutos":
    fig_evolucion = go.Figure()
    for sector, config in sectores_config.items():
        fig_evolucion.add_trace(go.Scatter(
            x=df_evolucion['año'],
            y=df_evolucion[sector],
            mode='lines+markers',
            name=f"{config['icon']} {sector}",
            line=dict(color=config['color'], width=3),
            marker=dict(size=8)
        ))
    fig_evolucion.update_layout(
        title="Evolución Anual de Contratos por Sector",
        xaxis_title="Año",
        yaxis_title="Número de Contratos",
        height=500,
        hovermode='x unified'
    )

elif vista_tipo == "Porcentajes":
    sectores_cols = list(sectores_config.keys())
    df_evolucion['total'] = df_evolucion[sectores_cols].sum(axis=1)
    for sector in sectores_cols:
        df_evolucion[f'{sector}_pct'] = (df_evolucion[sector] / df_evolucion['total']) * 100
    
    fig_evolucion = go.Figure()
    for sector, config in sectores_config.items():
        fig_evolucion.add_trace(go.Scatter(
            x=df_evolucion['año'],
            y=df_evolucion[f'{sector}_pct'],
            mode='lines+markers',
            name=f"{config['icon']} {sector}",
            line=dict(color=config['color'], width=3),
            marker=dict(size=8)
        ))
    fig_evolucion.update_layout(
        title="Evolución del Peso Relativo por Sector (%)",
        xaxis_title="Año",
        yaxis_title="Porcentaje del Total",
        height=500,
        hovermode='x unified'
    )

st.plotly_chart(fig_evolucion, width='stretch')

df_actual = df[df['año'].between(años_seleccionados[0], años_seleccionados[1])]


col1, col2, col3, col4 = st.columns(4)

total_contratos = {
    sector: df_actual[config['columna']].sum() / len(df_actual['año'].unique())
    for sector, config in sectores_config.items()
}

total_general = sum(total_contratos.values())

with col1:
    st.metric(
        label=f"{sectores_config['Servicios']['icon']} Servicios",
        value=f"{total_contratos['Servicios']:,.0f}",
        delta=f"{(total_contratos['Servicios']/total_general*100):.1f}%"
    )

with col2:
    st.metric(
        label=f"{sectores_config['Construcción']['icon']} Construcción",
        value=f"{total_contratos['Construcción']:,.0f}",
        delta=f"{(total_contratos['Construcción']/total_general*100):.1f}%"
    )

with col3:
    st.metric(
        label=f"{sectores_config['Industria']['icon']} Industria",
        value=f"{total_contratos['Industria']:,.0f}",
        delta=f"{(total_contratos['Industria']/total_general*100):.1f}%"
    )

with col4:
    st.metric(
        label=f"{sectores_config['Agricultura']['icon']} Agricultura",
        value=f"{total_contratos['Agricultura']:,.0f}",
        delta=f"{(total_contratos['Agricultura']/total_general*100):.1f}%"
    )


st.markdown("<div style='margin: 60px 0;'></div>", unsafe_allow_html=True)


# ========= SECCIÓN 3: ANÁLISIS CONTRATOS VS DEMANDANTES =========
st.subheader("Análisis Contratos vs Demandantes de Empleo")

col1, col2 = st.columns([1, 2])
with col1:
    año_analisis = st.selectbox(
        "🔍 Selecciona el año para análisis",
        options=sorted(df['año'].unique()),
        index=len(df['año'].unique())-1
    )

df_año = df[df['año'] == año_analisis].copy()

for sector, config in sectores_config.items():
    df_año[config['columna']] = pd.to_numeric(df_año[config['columna']], errors='coerce').fillna(0)
    df_año[config['demandantes']] = pd.to_numeric(df_año[config['demandantes']], errors='coerce').fillna(0)

datos_comparativa = []

for sector, config in sectores_config.items():
    contratos = df_año[config['columna']].sum()
    demandantes = df_año[config['demandantes']].sum()
    
    try:
        contratos = float(contratos)
        demandantes = float(demandantes)
        ratio = contratos / demandantes if demandantes != 0 else np.nan
    except (ValueError, TypeError):
        ratio = np.nan

    datos_comparativa.append({
        'Sector': sector,
        'Contratos': contratos,
        'Demandantes': demandantes,
        'Ratio': ratio,
        'Color': config['color'],
        'Icon': config['icon']
    })

df_comparativa = pd.DataFrame(datos_comparativa)

col_grafico, col_tabla = st.columns([2, 1])

with col_grafico:
    max_y = max(df_comparativa[['Contratos', 'Demandantes']].max()) * 1.1 

    fig_comp = go.Figure()
    fig_comp.add_trace(go.Bar(
        name='Demandantes',
        x=df_comparativa['Sector'],
        y=df_comparativa['Demandantes'],
        marker_color='lightgray',
        opacity=0.7
    ))
    fig_comp.add_trace(go.Bar(
        name='Contratos',
        x=df_comparativa['Sector'],
        y=df_comparativa['Contratos'],
        marker_color=df_comparativa['Color']
    ))

    fig_comp.update_layout(
        title=f"Comparativa Contratos vs Demandantes ({año_analisis})",
        xaxis_title="Sector",
        yaxis_title="Cantidad",
        barmode='group',
        height=400,
        yaxis=dict(
            range=[0, max_y],
            tickformat=",~s" 
        )
    )

    st.plotly_chart(fig_comp, width='stretch')

with col_tabla:
    df_display = df_comparativa[['Sector', 'Contratos', 'Demandantes', 'Ratio']].copy()
    df_display['Eficiencia'] = df_display['Ratio'].apply(
        lambda x: "🟢 Alta" if x > 0.8 else ("🟡 Media" if x > 0.5 else "🔴 Baja")
    )

    st.dataframe(
        df_display.style.format({
            'Contratos': '{:,.0f}',
            'Demandantes': '{:,.0f}',
            'Ratio': '{:.2f}'
        }),
        width='stretch'
    )


st.markdown("<div style='margin: 60px 0;'></div>", unsafe_allow_html=True)

# ========= SECCIÓN 4: ANÁLISIS ESTACIONAL =========
st.subheader("Patrones Estacionales por Sector")

df['mes'] = df['fecha'].dt.month
df['nombre_mes'] = df['fecha'].dt.strftime('%B')

sectores_estacional = st.multiselect(
    "Selecciona sectores para análisis estacional",
    options=list(sectores_config.keys()),
    default=['Agricultura', 'Construcción', 'Servicios', 'Industria']
)

if sectores_estacional:
    df_estacional = df.groupby(['mes', 'nombre_mes']).agg({
        sectores_config[sector]['columna']: 'mean' for sector in sectores_estacional
    }).reset_index()
    
    fig_estacional = go.Figure()
    for sector in sectores_estacional:
        config = sectores_config[sector]
        fig_estacional.add_trace(go.Scatter(
            x=df_estacional['nombre_mes'],
            y=df_estacional[config['columna']],
            mode='lines+markers',
            name=f"{config['icon']} {sector}",
            line=dict(color=config['color'], width=3),
            marker=dict(size=8)
        ))
    
    fig_estacional.update_layout(
        title="Patrones Estacionales por Sector (Promedio Mensual)",
        xaxis_title="Mes",
        yaxis_title="Contratos Promedio",
        height=400
    )
    
    st.plotly_chart(fig_estacional, width='stretch')
    
    cols_stats = st.columns(len(sectores_estacional))
    for i, sector in enumerate(sectores_estacional):
        config = sectores_config[sector]
        sector_data = df_estacional[config['columna']]
        
        # Encontrar pico y valle
        max_mes = df_estacional.loc[sector_data.idxmax(), 'nombre_mes']
        min_mes = df_estacional.loc[sector_data.idxmin(), 'nombre_mes']
        variabilidad = ((sector_data.max() - sector_data.min()) / sector_data.mean()) * 100
        
        with cols_stats[i]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {config['color']}22, {config['color']}11); 
                        padding: 15px; border-radius: 10px; border-left: 4px solid {config['color']};">
                <h5 style="color: {config['color']}; margin: 0;">{config['icon']} {sector}</h5>
                <p style="margin: 5px 0;"><strong>Pico:</strong> {max_mes}</p>
                <p style="margin: 5px 0;"><strong>Valle:</strong> {min_mes}</p>
            </div>
            """, unsafe_allow_html=True)


st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("<div style='margin: 80px 0;'></div>", unsafe_allow_html=True)

# ========= SECCIÓN 5: ANÁLISIS GEOGRÁFICO  =========
st.subheader("🗺️ Análisis Geográfico por Sectores")

st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)

# === DISTRIBUCIÓN POR SECTOR ===
st.markdown("####  Distribución de Sectores a nivel de Comunidad Autónoma")

año = st.selectbox(
    "🗓️ Selecciona el año para el análisis de distribución",
    options=sorted(df['año'].unique(), reverse=True),
    index=0,
    key="dist_sector_year"
)

gdf = gdf_ccaa
key_col = 'comunidad_autónoma'
merge_col = 'rotulo'
hover_col = 'rotulo'

sectores = {
    'Servicios': 'contratos__servicios',
    'Agricultura': 'contratos__agricultura',
    'Industria': 'contratos__industria',
    'Construcción': 'contratos_construcción'
}

df_anio = df[df['año'] == año].copy()

columnas = st.columns(4)
stats_sectores = {}

for i, (sector, columna) in enumerate(sectores.items()):
    df_grouped = df_anio.groupby(key_col)[columna].sum().reset_index()

    vmin = df_grouped[columna].min()
    vmax = df_grouped[columna].max()

    stats_sectores[sector] = {
        'total': df_grouped[columna].sum(),
        'max_region': df_grouped.loc[df_grouped[columna].idxmax(), key_col],
        'max_value': vmax,
        'promedio': df_grouped[columna].mean()
    }

    gdf_merged = gdf.merge(df_grouped, left_on=merge_col, right_on=key_col, how='left')

    fig = px.choropleth(
        gdf_merged,
        geojson=gdf_merged.geometry.__geo_interface__,
        locations=gdf_merged.index,
        color=columna,
        hover_name=hover_col,
        color_continuous_scale='YlGnBu',
        range_color=(vmin, vmax),
        title=f"{sector}",
    )
    fig.update_geos(fitbounds="locations", visible=False)
    fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))

    with columnas[i]:
        st.plotly_chart(fig, width='stretch')


st.markdown("**🏆 Regiones Líderes por Sector:**")
for sector, stats in stats_sectores.items():
    color = sectores_config[sector]['color']
    icon = sectores_config[sector]['icon']
    st.markdown(f"""
    <div style="background: {color}22; padding: 8px; margin: 5px 0; border-radius: 5px; border-left: 3px solid {color};">
        <strong>{icon} {sector}:</strong> {stats['max_region']} ({stats['max_value']:,.0f} contratos)
    </div>
    """, unsafe_allow_html=True)


st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)

# === SECTOR PREDOMINANTE ===
st.markdown("#### Evolución de Sectores Dominantes")

col1, col2 = st.columns(2)
with col1:
    nivel_geografico = st.selectbox(
        "🔍 Nivel geográfico",
        ["Comunidades Autónomas", "Provincias"]
    )
with col2:
    años_mapa = st.multiselect(
        "🧭 Años para comparación (máx. 4)",
        options=sorted(df['año'].unique(), reverse=True),
        default=[sorted(df['año'].unique(), reverse=True)[0]],
        key="mapa_years"
    )
    if len(años_mapa) > 4:
        st.warning("Selecciona como máximo 4 años.")
        st.stop()

columnas = st.columns(len(años_mapa))
dominancia_stats = {}

if nivel_geografico == "Provincias":
    st.info(
        "⚠️ Por limitaciones de memoria RAM en Streamlit Cloud, "
        "la visualización por provincias no está disponible en la versión desplegada. "
        "Si ejecutas este proyecto en local, podrás ver también los mapas por provincias. " \
        "En el vídeo demostrativo se muestra esta funcionalidad." 
    )

    st.stop()
  

for i, año in enumerate(sorted(años_mapa, reverse=True)):
    df_geo = df[df['año'] == año].copy()
    
    if nivel_geografico == "Comunidades Autónomas":
        df_mapa = df_geo.groupby('comunidad_autónoma').agg({
            config['columna']: 'sum' for config in sectores_config.values()
        }).reset_index()
        key_col = 'comunidad_autónoma'
        merge_col = 'rotulo'
        gdf = gdf_ccaa
        hover_col = 'rotulo'
        unidad_geografica = "CC.AA."
    # else: 
    #     df_mapa = df_geo.groupby('provincia').agg({
    #         config['columna']: 'sum' for config in sectores_config.values()
    #     }).reset_index()
    #     key_col = 'provincia'
    #     merge_col = 'NAMEUNIT'
    #     gdf = gdf_prov
    #     hover_col = 'NAMEUNIT'
    #     unidad_geografica = "Provincias"

        gdf_mapa = gdf.merge(df_mapa, left_on=merge_col, right_on=key_col, how='left')

        sectores_cols = [config['columna'] for config in sectores_config.values()]
        for col in sectores_cols:
            if col in gdf_mapa.columns:
                media_col = gdf_mapa[col].mean(skipna=True)
                gdf_mapa[col] = gdf_mapa[col].fillna(media_col)

        gdf_mapa['sector_dominante'] = gdf_mapa[sectores_cols].idxmax(axis=1)
        gdf_mapa['sector_dominante'] = gdf_mapa['sector_dominante'].map({
            config['columna']: sector for sector, config in sectores_config.items()
        })

        dominancia_count = gdf_mapa['sector_dominante'].value_counts()
        dominancia_stats[año] = {
            'counts': dominancia_count,
            'unidad': unidad_geografica
        }

        color_map = {sector: config['color'] for sector, config in sectores_config.items()}

        fig = px.choropleth(
            gdf_mapa,
            geojson=gdf_mapa.geometry.__geo_interface__,
            locations=gdf_mapa.index,
            color='sector_dominante',
            hover_name=hover_col,
            color_discrete_map=color_map,
            title=f"{año}"
        )
        fig.update_geos(fitbounds="locations", visible=False)
        fig.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0))

        with columnas[i]:
            st.plotly_chart(fig, width='stretch')


# ---------------------------
# FOOTER CON INFORMACIÓN
# ---------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <small>
    <strong>Fuente de datos:</strong> Dataset de empleo español por sectores económicos (2010-2025)<br>
    <strong>Metodología:</strong> Análisis basado en datos del SEPE y clasificación CNAE<br>
    <strong>Última actualización:</strong> Los datos se actualizan automáticamente
    </small>
</div>
""", unsafe_allow_html=True)
