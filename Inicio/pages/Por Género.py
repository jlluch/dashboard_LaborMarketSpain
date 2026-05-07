
import streamlit as st
import pandas as pd
import geopandas as gpd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from utils import cargar_datos, cargar_geodatos

# ---------------------------
# CONFIGURACIÓN DE PÁGINA
# ---------------------------
st.set_page_config(
    page_title="Análisis por Género",
    page_icon="👥", 
    layout="wide"
)

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

# ---------------------------
# PROCESAMIENTO DE DATOS
# ---------------------------
@st.cache_data
def procesar_datos_genero(df):
    """Preprocesa los datos para análisis de género"""
    df_processed = df.copy()
    
    df_processed["total_contratos_hombres"] = (
        df_processed["contratos_iniciales_indefinidos_hombres"] +
        df_processed["contratos_iniciales_temporales_hombres"] +
        df_processed["contratos_convertidos_en_indefinidos_hombres"]
    )
    
    df_processed["total_contratos_mujeres"] = (
        df_processed["contratos_iniciales_indefinidos_mujeres"] +
        df_processed["contratos_iniciales_temporales_mujeres"] +
        df_processed["contratos_convertidos_en_indefinidos_mujeres"]
    )
    
    df_processed["total_dtes_hombres"] = (
        df_processed["dtes_empleo_hombre_edad_<_25"] +
        df_processed["dtes_empleo_hombre_edad_25_-45"] +
        df_processed["dtes_empleo_hombre_edad_>=45"]
    )
    
    df_processed["total_dtes_mujeres"] = (
        df_processed["dtes_empleo_mujer_edad_<_25"] +
        df_processed["dtes_empleo_mujer_edad_25_-45"] +
        df_processed["dtes_empleo_mujer_edad_>=45"]
    )
    
    df_processed["total_contratos_total"] = df_processed["total_contratos_hombres"] + df_processed["total_contratos_mujeres"]
    df_processed["brecha_relativa_contratos"] = np.where(
        df_processed["total_contratos_total"] > 0,
        (df_processed["total_contratos_hombres"] - df_processed["total_contratos_mujeres"]) / df_processed["total_contratos_total"],
        0
    )
    
    return df_processed

df = procesar_datos_genero(df)

# ---------------------------
# TÍTULO Y DESCRIPCIÓN
# ---------------------------
st.title("👥 Análisis del Mercado Laboral por Género")
st.markdown("### Período 2010-2025")

st.markdown("""
<div style="background-color: #f0f2f6; padding: 1rem; border-radius: 0.5rem; margin-bottom: 2rem;">
    <h4>🎯 Objetivos a analizar</h4>
    <ul>
        <li><strong>Evolución por género:</strong> Comparativa de contratos y demandantes entre hombres y mujeres</li>
        <li><strong>Análisis de brechas:</strong> Identificación de desigualdades en el mercado laboral</li>
        <li><strong>Tipos de contrato:</strong> Distribución de contratos indefinidos, temporales y conversiones por género</li>
        <li><strong>Visualización geográfica:</strong> Mapas de brechas de género por regiones</li>
        <li><strong>Análisis por edades:</strong> Patrones de demanda de empleo según franjas etarias</li>
    </ul>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)


# ---------------------------
# EVOLUCIÓN TEMPORAL POR GÉNERO
# ---------------------------
st.subheader("Evolución Temporal: Contratos y Demandantes por Género")

with st.spinner('Generando análisis temporal por género...'):
    df_agg = df.groupby("año").agg({
        "total_contratos_hombres": "sum",
        "total_contratos_mujeres": "sum",
        "total_dtes_hombres": "sum",
        "total_dtes_mujeres": "sum"
    }).reset_index()
    
    col_graf1, col_graf2 = st.columns(2)
    
    with col_graf1:
        fig1 = go.Figure()
        fig1.add_trace(go.Scatter(
            x=df_agg["año"], 
            y=df_agg["total_contratos_hombres"],
            mode='lines+markers', 
            name="Contratos Hombres", 
            line=dict(color="#4574A1", width=3),
            hovertemplate="<b>Contratos Hombres</b><br>Año: %{x}<br>Cantidad: %{y:,.0f}<extra></extra>"
        ))
        fig1.add_trace(go.Scatter(
            x=df_agg["año"], 
            y=df_agg["total_contratos_mujeres"],
            mode='lines+markers', 
            name="Contratos Mujeres", 
            line=dict(color="#E54923", width=3),
            hovertemplate="<b>Contratos Mujeres</b><br>Año: %{x}<br>Cantidad: %{y:,.0f}<extra></extra>"
        ))
        fig1.add_trace(go.Scatter(
            x=df_agg["año"], 
            y=df_agg["total_dtes_hombres"],
            mode='lines+markers', 
            name="Demandantes Hombres", 
            line=dict(color="#4574A1", dash="dot", width=3),
            hovertemplate="<b>Demandantes Hombres</b><br>Año: %{x}<br>Cantidad: %{y:,.0f}<extra></extra>"
        ))
        fig1.add_trace(go.Scatter(
            x=df_agg["año"], 
            y=df_agg["total_dtes_mujeres"],
            mode='lines+markers', 
            name="Demandantes Mujeres", 
            line=dict(color="#E54923", dash="dot", width=3),
            hovertemplate="<b>Demandantes Mujeres</b><br>Año: %{x}<br>Cantidad: %{y:,.0f}<extra></extra>"
        ))
        fig1.update_layout(
            title="Evolución por Género (2010-2025)",
            xaxis_title="Año", 
            yaxis_title="Número de Personas",
            hovermode='x unified',
            height=450,
            showlegend=True
        )
        st.plotly_chart(fig1, width='stretch')
    
    with col_graf2:
        fig2 = go.Figure()
        fig2.add_trace(go.Scatter(
            x=df_agg["total_dtes_hombres"], 
            y=df_agg["total_contratos_hombres"],
            mode='markers', 
            name="Hombres",
            marker=dict(color="#4574A1", size=10),
            hovertemplate="<b>Hombres</b><br>Demandantes: %{x:,.0f}<br>Contratos: %{y:,.0f}<extra></extra>"
        ))
        fig2.add_trace(go.Scatter(
            x=df_agg["total_dtes_mujeres"], 
            y=df_agg["total_contratos_mujeres"],
            mode='markers', 
            name="Mujeres",
            marker=dict(color="#E54923", size=10),
            hovertemplate="<b>Mujeres</b><br>Demandantes: %{x:,.0f}<br>Contratos: %{y:,.0f}<extra></extra>"
        ))
        
        fig2.add_hline(y=df_agg["total_contratos_hombres"].mean(), 
                      line_dash="dash", line_color="#4574A1", opacity=0.7,
                      annotation_text="Media Contratos H", annotation_position="bottom right")
        fig2.add_hline(y=df_agg["total_contratos_mujeres"].mean(), 
                      line_dash="dash", line_color="#E54923", opacity=0.7,
                      annotation_text="Media Contratos M", annotation_position="top right")
        fig2.add_vline(x=df_agg["total_dtes_hombres"].mean(),
                        line_dash="dash", line_color="#4574A1", opacity=0.7,
                        annotation_text="Media Demandantes H", annotation_position="top left")
        fig2.add_vline(x=df_agg["total_dtes_mujeres"].mean(),
                        line_dash="dash", line_color="#E54923", opacity=0.7,
                        annotation_text="Media Demandantes M", annotation_position="bottom left")
        
        fig2.update_layout(
            title="Dispersión: Contratos vs Demandantes",
            xaxis_title="Demandantes de Empleo", 
            yaxis_title="Total Contratos",
            height=450,
            showlegend=True
        )
        st.plotly_chart(fig2, width='stretch')

col_insight1, col_insight2, col_insight3, col_insight4 = st.columns(4)

with col_insight1:
    brecha_contratos_media = df_agg["total_contratos_hombres"].mean() - df_agg["total_contratos_mujeres"].mean()
    st.metric("🔄 Brecha Media Contratos", f"{brecha_contratos_media:,.0f}", "Hombres - Mujeres")

with col_insight2:
    media_contratos_hombres = df_agg["total_contratos_hombres"].mean()
    st.metric("👨 Media Contratos Hombres", f"{media_contratos_hombres:,.0f}")

with col_insight3:
    media_contratos_mujeres = df_agg["total_contratos_mujeres"].mean()
    st.metric("👩 Media Contratos Mujeres", f"{media_contratos_mujeres:,.0f}")

with col_insight4:
    ratio_genero = media_contratos_hombres / media_contratos_mujeres if media_contratos_mujeres > 0 else 0
    st.metric("⚖️ Ratio H/M", f"{ratio_genero:.2f}")

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)

# ---------------------------
# ANÁLISIS POR TIPO DE CONTRATO
# ---------------------------
st.subheader("Análisis por Tipo de Contrato y Género")

mostrar_detalle_tipo = st.checkbox("Mostrar desglose por tipo de contrato sobre esta gráfica", 
                                   help="Activa para ver la distribución entre indefinidos, temporales y conversiones")

with st.spinner('Generando análisis por tipo de contrato...'):
    if not mostrar_detalle_tipo:
        contratos_agg = df.groupby("año").agg({
            "total_contratos_hombres": "sum",
            "total_contratos_mujeres": "sum"
        }).reset_index()

        fig3 = go.Figure()
        fig3.add_trace(go.Bar(
            x=contratos_agg["año"],
            y=contratos_agg["total_contratos_hombres"],
            name="Hombres",
            marker_color="#4574A1",
            hovertemplate="<b>Contratos Hombres</b><br>Año: %{x}<br>Total: %{y:,.0f}<extra></extra>"
        ))
        fig3.add_trace(go.Bar(
            x=contratos_agg["año"],
            y=contratos_agg["total_contratos_mujeres"],
            name="Mujeres",
            marker_color="#E54923",
            hovertemplate="<b>Contratos Mujeres</b><br>Año: %{x}<br>Total: %{y:,.0f}<extra></extra>"
        ))

        fig3.update_layout(
            title="Evolución Anual de Contratos por Género (2010-2025)",
            xaxis_title="Año",
            yaxis_title="Número de Contratos",
            barmode="group",
            height=500
        )
        st.plotly_chart(fig3, width='stretch')

    else:
        # Gráfica detallada por tipo y género combinados
        contratos = df.groupby("año").agg({
            "contratos_iniciales_indefinidos_hombres": "sum",
            "contratos_iniciales_temporales_hombres": "sum",
            "contratos_convertidos_en_indefinidos_hombres": "sum",
            "contratos_iniciales_indefinidos_mujeres": "sum",
            "contratos_iniciales_temporales_mujeres": "sum",
            "contratos_convertidos_en_indefinidos_mujeres": "sum"
        }).reset_index()

        fig4 = go.Figure()

        tipos = {
            "Indefinidos": ("contratos_iniciales_indefinidos_hombres", "contratos_iniciales_indefinidos_mujeres", "#4574A1", "#E54923"),
            "Temporales": ("contratos_iniciales_temporales_hombres", "contratos_iniciales_temporales_mujeres", "lightblue", "pink"),
            "Convertidos": ("contratos_convertidos_en_indefinidos_hombres", "contratos_convertidos_en_indefinidos_mujeres", "navy", "darkred")
        }

        for tipo, (col_h, col_m, color_h, color_m) in tipos.items():
            fig4.add_trace(go.Bar(
                x=contratos["año"],
                y=contratos[col_h],
                name=f"{tipo} Hombres",
                marker_color=color_h,
                offsetgroup=0,
                hovertemplate=f"<b>{tipo} Hombres</b><br>Año: %{{x}}<br>Cantidad: %{{y:,.0f}}<extra></extra>"
            ))
            fig4.add_trace(go.Bar(
                x=contratos["año"],
                y=contratos[col_m],
                name=f"{tipo} Mujeres",
                marker_color=color_m,
                offsetgroup=1,
                base=None,
                hovertemplate=f"<b>{tipo} Mujeres</b><br>Año: %{{x}}<br>Cantidad: %{{y:,.0f}}<extra></extra>"
            ))

        # Línea vertical reforma 2021
        fig4.add_vline(
            x=2021,
            line_dash="dot",
            line_color="#FACB20",
            line_width=3,
        )
        fig4.add_annotation(
            x=2021,
            y=1.05,
            xref="x",
            yref="paper",
            text="Reforma 2021",
            showarrow=False,
            font=dict(color="#FACB20", size=12)
        )

        fig4.update_layout(
            title="Evolución de Contratos por Tipo y Género (2010-2025)",
            xaxis_title="Año",
            yaxis_title="Número de Contratos",
            barmode="stack",
            height=600
        )

        st.plotly_chart(fig4, width='stretch')



if mostrar_detalle_tipo:
    st.markdown("""
    <div style="background-color: #fff3cd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #FACB20; margin: 1rem 0;">
        <h5>⚡ Impacto de la Reforma Laboral 2021</h5>
        <p>La línea amarilla marca la entrada en vigor de la reforma laboral. Se puede observar cómo esta medida 
        ha influido en la <strong>reducción de la temporalidad</strong> y el <strong>aumento de las conversiones a indefinido</strong>, 
        afectando de manera similar a ambos géneros pero con diferencias en la magnitud del impacto.</p>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)

# ---------------------------
# ANÁLISIS DE DEMANDANTES POR EDAD
# ---------------------------
st.subheader("Evolución de Demandantes por Edad y Género")

with st.spinner('Analizando patrones por edad...'):
    df_edad = df.groupby("año").agg({
        "dtes_empleo_hombre_edad_<_25": "sum",
        "dtes_empleo_hombre_edad_25_-45": "sum", 
        "dtes_empleo_hombre_edad_>=45": "sum",
        "dtes_empleo_mujer_edad_<_25": "sum",
        "dtes_empleo_mujer_edad_25_-45": "sum",
        "dtes_empleo_mujer_edad_>=45": "sum"
    }).reset_index()
    
    col_edad1, col_edad2 = st.columns(2)
    
    with col_edad1:
        fig5 = go.Figure()
        fig5.add_trace(go.Scatter(
            x=df_edad["año"], y=df_edad["dtes_empleo_hombre_edad_<_25"],
            mode='lines+markers', name="< 25 años", line=dict(color="#1f77b4", width=2)
        ))
        fig5.add_trace(go.Scatter(
            x=df_edad["año"], y=df_edad["dtes_empleo_hombre_edad_25_-45"],
            mode='lines+markers', name="25-45 años", line=dict(color="#ff7f0e", width=2)
        ))
        fig5.add_trace(go.Scatter(
            x=df_edad["año"], y=df_edad["dtes_empleo_hombre_edad_>=45"],
            mode='lines+markers', name="≥ 45 años", line=dict(color="#2ca02c", width=2)
        ))
        fig5.update_layout(
            title="Demandantes Hombres por Edad",
            xaxis_title="Año", yaxis_title="Demandantes",
            height=400
        )
        st.plotly_chart(fig5, width='stretch')
    
    with col_edad2:
        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(
            x=df_edad["año"], y=df_edad["dtes_empleo_mujer_edad_<_25"],
            mode='lines+markers', name="< 25 años", line=dict(color="#1f77b4", width=2)
        ))
        fig6.add_trace(go.Scatter(
            x=df_edad["año"], y=df_edad["dtes_empleo_mujer_edad_25_-45"],
            mode='lines+markers', name="25-45 años", line=dict(color="#ff7f0e", width=2)
        ))
        fig6.add_trace(go.Scatter(
            x=df_edad["año"], y=df_edad["dtes_empleo_mujer_edad_>=45"],
            mode='lines+markers', name="≥ 45 años", line=dict(color="#2ca02c", width=2)
        ))
        fig6.update_layout(
            title="Demandantes Mujeres por Edad",
            xaxis_title="Año", yaxis_title="Demandantes",
            height=400
        )
        st.plotly_chart(fig6, width='stretch')

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("<div style='margin: 40px 0;'></div>", unsafe_allow_html=True)

# ---------------------------
# MAPAS DE BRECHA DE GÉNERO
# ---------------------------
st.subheader("🗺️ Análisis Geográfico: Brecha de Género en Contratos")

st.markdown("""
<div style="background-color: #e8f4fd; padding: 1rem; border-radius: 0.5rem; border-left: 4px solid #1f77b4; margin: 1rem 0;">
    <h5>¿Cómo interpretar la Brecha de Género?</h5>
    <ul>
        <li><strong>Valores positivos (azul):</strong> Más contratos de hombres que de mujeres</li>
        <li><strong>Valores negativos (rojo):</strong> Más contratos de mujeres que de hombres</li>
        <li><strong>Valor 0 (blanco):</strong> Paridad perfecta</li>
        <li><strong>Fórmula:</strong> (Contratos Hombres - Contratos Mujeres) ÷ Total Contratos</li>
    </ul>
</div>
""", unsafe_allow_html=True)

col_control1, col_control2 = st.columns([3, 2])

with col_control1:
    años_mapa = st.multiselect(
        "📅 Selecciona años para comparar:",
        sorted(df["año"].unique(), reverse=True),
        default=[2020, 2021, 2022, 2023] if all(año in df["año"].unique() for año in [2020, 2021, 2022, 2023]) else sorted(df["año"].unique(), reverse=True)[:4],
        max_selections=4,
        help="Máximo 4 años para mejor visualización"
    )

with col_control2:
    nivel_geografico = st.radio(
        "🌍 Nivel geográfico:",
        ["Comunidades Autónomas", "Provincias"]
    )

if años_mapa:
    with st.spinner('Generando mapas de brecha de género...'):
        df_mapa = df[df["año"].isin(años_mapa)].copy()
        
        if nivel_geografico == "Comunidades Autónomas":
            # Datos para CCAA
            mapa_data = []
            valores_brecha = []
            
            for año in años_mapa:
                df_año = df_mapa[df_mapa["año"] == año]
                df_grouped = df_año.groupby("comunidad_autónoma")["brecha_relativa_contratos"].mean().reset_index()
                gdf_plot = gdf_ccaa.set_index("rotulo").join(df_grouped.set_index("comunidad_autónoma")).reset_index()
                mapa_data.append((año, gdf_plot))
                valores_brecha.extend(gdf_plot["brecha_relativa_contratos"].dropna().tolist())
            
            if valores_brecha:
                absmax = max(abs(min(valores_brecha)), abs(max(valores_brecha)))
                rango_color = [-absmax, absmax]
            else:
                rango_color = [-0.1, 0.1]
            
            cols_mapa = st.columns(len(años_mapa))
            for i, (año, gdf_plot) in enumerate(mapa_data):
                with cols_mapa[i]:
                    fig_mapa = px.choropleth(
                        gdf_plot,
                        geojson=gdf_plot.geometry.__geo_interface__,
                        locations=gdf_plot.index,
                        color="brecha_relativa_contratos",
                        hover_name="rotulo",
                        color_continuous_scale="RdBu_r",
                        range_color=rango_color,
                        title=f"<b>{año}</b>"
                    )
                    fig_mapa.update_geos(fitbounds="locations", visible=False)
                    fig_mapa.update_layout(
                        height=450,
                        title_x=0.5,
                        coloraxis_showscale=(i == len(años_mapa) - 1)
                    )
                    st.plotly_chart(fig_mapa, width='stretch')
                    
        else:
            # Datos para Provincias
              st.info(
                    "⚠️ Por limitaciones de memoria RAM en Streamlit Cloud, "
                    "la visualización por provincias no está disponible en la versión desplegada. "
                    "Si ejecutas este proyecto en local, podrás ver también los mapas por provincias. " \
                    "En el vídeo demostrativo se muestra esta funcionalidad." 
                )
            # mapa_data = []
            # valores_brecha = []
            
            # for año in años_mapa:
            #     df_año = df_mapa[df_mapa["año"] == año]
            #     df_año["provincia_corr"] = df_año["provincia"].replace(equivalencias_provincias)
            #     df_grouped = df_año.groupby("provincia_corr")["brecha_relativa_contratos"].mean().reset_index()

            #     gdf_plot = gdf_prov.set_index("NAMEUNIT").join(df_grouped.set_index("provincia_corr")).reset_index()
            #     mapa_data.append((año, gdf_plot))
            #     valores_brecha.extend(gdf_plot["brecha_relativa_contratos"].dropna().tolist())
            # if valores_brecha:
            #     absmax = max(abs(min(valores_brecha)), abs(max(valores_brecha)))
            #     rango_color = [-absmax, absmax]
            # else:
            #     rango_color = [-0.1, 0.1]
            
            # cols_mapa = st.columns(len(años_mapa))
            # for i, (año, gdf_plot) in enumerate(mapa_data):
            #     with cols_mapa[i]:
            #         fig_mapa = px.choropleth(
            #             gdf_plot,
            #             geojson=gdf_plot.geometry.__geo_interface__,
            #             locations=gdf_plot.index,
            #             color="brecha_relativa_contratos",
            #             hover_name="NAMEUNIT",
            #             color_continuous_scale="RdBu_r",
            #             range_color=rango_color,
            #             title=f"<b>{año}</b>"
            #         )
            #         fig_mapa.update_geos(fitbounds="locations", visible=False)
            #         fig_mapa.update_layout(
            #             height=450,
            #             title_x=0.5,
            #             coloraxis_showscale=(i == len(años_mapa) - 1)
            #         )
            #         st.plotly_chart(fig_mapa, width='stretch')
    

st.markdown("#### 📈 Resumen Comparativo")

años_seleccionados = sorted(df["año"].unique())
if not años_mapa:
    años_seleccionados = años_seleccionados[-4:] 
else:
    años_seleccionados = sorted(años_mapa)  # Usar los años seleccionados para mapas

if len(años_seleccionados) > 4:
    st.warning("Se mostrarán los últimos 4 años seleccionados para evitar sobrecarga visual.")
    años_seleccionados = años_seleccionados[-4:]

df_comparativo = df[df["año"].isin(años_seleccionados)].groupby("año").agg({
    "total_contratos_hombres": "sum",
    "total_contratos_mujeres": "sum"
}).reset_index()

df_comparativo["total_contratos"] = df_comparativo["total_contratos_hombres"] + df_comparativo["total_contratos_mujeres"]
df_comparativo["brecha_relativa"] = np.where(
    df_comparativo["total_contratos"] > 0,
    (df_comparativo["total_contratos_hombres"] - df_comparativo["total_contratos_mujeres"]) / df_comparativo["total_contratos"],
    0
)

df_comparativo = df_comparativo.sort_values("año")
df_comparativo["cambio_brecha"] = df_comparativo["brecha_relativa"].diff()
df_comparativo["tendencia"] = df_comparativo["cambio_brecha"].apply(
    lambda x: "🔴 Aumenta" if x > 0.005 else ("🟢 Disminuye" if x < -0.005 else "🟡 Estable") if pd.notna(x) else "➖"
)

df_display = df_comparativo.copy()
df_display["brecha_absoluta"] = df_display["total_contratos_hombres"] - df_display["total_contratos_mujeres"]

df_display = df_display[[
    "año", 
    "total_contratos_hombres", 
    "total_contratos_mujeres", 
    "brecha_relativa", 
    "tendencia"
]]

df_display.columns = [
    "Año",
    "Contratos Hombres", 
    "Contratos Mujeres",
    "Brecha Relativa (%)",
    "Tendencia"
]

st.dataframe(
    df_display.style.format({
        "Contratos Hombres": "{:,.0f}",
        "Contratos Mujeres": "{:,.0f}",
        "Brecha Relativa (%)": "{:.2%}",
    }).map(
        lambda x: (
            "background-color: #ffebee" if isinstance(x, str) and "🔴" in x else
            "background-color: #e8f5e8" if isinstance(x, str) and "🟢" in x else
            "background-color: #fff3e0" if isinstance(x, str) and "🟡" in x else
            ""
        ),
        subset=["Tendencia"]
    ),
    width="stretch"
)

if len(años_seleccionados) > 1:
    brecha_inicial = df_comparativo.iloc[0]["brecha_relativa"]
    brecha_final = df_comparativo.iloc[-1]["brecha_relativa"]
    cambio_total = brecha_final - brecha_inicial
        
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label=f"Brecha en {años_seleccionados[0]}",
            value=f"{brecha_inicial:.2%}",
            delta=None
        )
    
    with col2:
        st.metric(
            label=f"Brecha en {años_seleccionados[-1]}",
            value=f"{brecha_final:.2%}",
            delta=f"{cambio_total:+.2%}"
        )
    
    with col3:
        tendencia_general = "🔴 Empeora" if cambio_total > 0.01 else ("🟢 Mejora" if cambio_total < -0.01 else "🟡 Estable")
        st.metric(
            label="Tendencia General",
            value=tendencia_general,
            delta=None
        )
    
    if cambio_total > 0.01:
        interpretacion = f"La brecha de género ha **aumentado** {abs(cambio_total):.2%} puntos porcentuales entre {años_seleccionados[0]} y {años_seleccionados[-1]}, lo que indica un empeoramiento de la situación."
    elif cambio_total < -0.01:
        interpretacion = f"La brecha de género ha **disminuido** {abs(cambio_total):.2%} puntos porcentuales entre {años_seleccionados[0]} y {años_seleccionados[-1]}, mostrando una mejora en la equidad."
    else:
        interpretacion = f"La brecha de género se ha mantenido **relativamente estable** entre {años_seleccionados[0]} y {años_seleccionados[-1]}."
    
    st.info(f"**Interpretación:** {interpretacion}")

if len(años_seleccionados) > 1:    
    fig_evolucion = px.line(
        df_comparativo,
        x="año",
        y="brecha_relativa",
        markers=True,
        title="Evolución de la Brecha de Género por Año",
        labels={
            "año": "Año",
            "brecha_relativa": "Brecha Relativa (%)"
        }
    )
    
    fig_evolucion.update_traces(
        line=dict(width=3),
        marker=dict(size=8)
    )
    
    fig_evolucion.update_layout(
        height=400,
        yaxis_tickformat=".1%",
        hovermode='x unified'
    )

    fig_evolucion.update_xaxes(type='category')

    
    fig_evolucion.add_hline(
        y=0, 
        line_dash="dash", 
        line_color="gray",
        annotation_text="Paridad (0%)"
    )
    
    st.plotly_chart(fig_evolucion, width='stretch')


# ---------------------------
# FOOTER CON INFORMACIÓN
# ---------------------------
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 1rem;">
    <small>
    <strong>Fuente de datos:</strong> Dataset de empleo español (2010-2025)<br>
    <strong>Última actualización:</strong> Los datos se actualizan automáticamente<br>
    <strong>Rendimiento:</strong> Los datos están optimizados en caché para una carga rápida
    </small>
</div>
""", unsafe_allow_html=True)
