import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# Configuración de la página
st.set_page_config(
    page_title="Supply Chain Resilience Platform",
    page_icon="🚢",
    layout="wide"
)

# Función para generar datos sintéticos
@st.cache_data
def generate_supply_chain_data(num_shipments=50):
    """Genera datos sintéticos de envíos y rutas logísticas"""
    
    # Puertos de origen (Asia)
    origin_ports = [
        {"name": "Ningbo, China", "lat": 29.8683, "lon": 121.5440},
        {"name": "Shanghai, China", "lat": 31.2304, "lon": 121.4737},
        {"name": "Busan, Corea del Sur", "lat": 35.1796, "lon": 129.0756},
        {"name": "Singapur", "lat": 1.3521, "lon": 103.8198}
    ]
    
    # Puertos de destino (Latinoamérica)
    destination_ports = [
        {"name": "Puerto Caucedo, RD", "lat": 18.4264, "lon": -69.6618},
        {"name": "Puerto de Balboa, Panamá", "lat": 8.9517, "lon": -79.5671},
        {"name": "Puerto de Colón, Panamá", "lat": 9.3592, "lon": -79.9009}
    ]
    
    shipments = []
    
    for i in range(num_shipments):
        origin = random.choice(origin_ports)
        destination = random.choice(destination_ports)
        
        # Tiempo de tránsito base (días)
        base_transit = random.randint(25, 40)
        
        # Factores de riesgo (0-100)
        climate_risk = random.randint(0, 100)
        port_congestion = random.randint(0, 100)
        social_stability = random.randint(0, 100)
        
        # Calcular score de riesgo (promedio ponderado)
        risk_score = (climate_risk * 0.3 + port_congestion * 0.5 + social_stability * 0.2)
        
        # Retraso adicional basado en riesgo
        delay = int((risk_score / 100) * 15)  # Máximo 15 días de retraso
        
        # Nivel de inventario actual
        current_inventory = random.randint(50, 500)
        
        # Consumo diario (unidades/día)
        daily_consumption = random.randint(5, 25)
        
        # Días hasta stock cero
        days_to_zero = current_inventory / daily_consumption
        
        # Fecha estimada de llegada
        eta = datetime.now() + timedelta(days=base_transit + delay)
        
        # Estado del envío
        if days_to_zero < (base_transit + delay):
            status = "CRÍTICO"
        elif risk_score > 70:
            status = "ALTO RIESGO"
        elif risk_score > 40:
            status = "RIESGO MEDIO"
        else:
            status = "NORMAL"
        
        shipment = {
            "ID": f"SHP-{1000+i}",
            "Origen": origin["name"],
            "Destino": destination["name"],
            "Origin_Lat": origin["lat"],
            "Origin_Lon": origin["lon"],
            "Dest_Lat": destination["lat"],
            "Dest_Lon": destination["lon"],
            "Tránsito_Base": base_transit,
            "Retraso": delay,
            "Tránsito_Total": base_transit + delay,
            "ETA": eta.strftime("%Y-%m-%d"),
            "Inventario_Actual": current_inventory,
            "Consumo_Diario": daily_consumption,
            "Días_Stock_Cero": round(days_to_zero, 1),
            "Riesgo_Clima": climate_risk,
            "Congestión_Puerto": port_congestion,
            "Estabilidad_Social": social_stability,
            "Score_Riesgo": round(risk_score, 1),
            "Estado": status
        }
        
        shipments.append(shipment)
    
    return pd.DataFrame(shipments)

# Función de predicción de riesgo de desabasto
def predict_stockout_risk(inventory, daily_consumption, transit_days, threshold_days=5):
    """
    Predice si habrá desabasto antes de la llegada del envío
    Usa una lógica de umbrales simple
    """
    days_to_stockout = inventory / daily_consumption
    buffer = days_to_stockout - transit_days
    
    if buffer < 0:
        return "DESABASTO INMINENTE", "🔴"
    elif buffer < threshold_days:
        return "RIESGO ALTO", "🟡"
    else:
        return "NORMAL", "🟢"

# Función para crear mapa de rutas
def create_route_map(df, selected_status):
    """Crea un mapa interactivo con las rutas logísticas"""
    
    # Filtrar datos según status
    if selected_status != "Todos":
        df_filtered = df[df["Estado"] == selected_status]
    else:
        df_filtered = df
    
    fig = go.Figure()
    
    # Colores según estado
    color_map = {
        "CRÍTICO": "red",
        "ALTO RIESGO": "orange",
        "RIESGO MEDIO": "yellow",
        "NORMAL": "green"
    }
    
    # Agregar rutas
    for _, row in df_filtered.iterrows():
        color = color_map.get(row["Estado"], "blue")
        
        # Línea de ruta
        fig.add_trace(go.Scattergeo(
            lon=[row["Origin_Lon"], row["Dest_Lon"]],
            lat=[row["Origin_Lat"], row["Dest_Lat"]],
            mode='lines',
            line=dict(width=2, color=color),
            opacity=0.6,
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Marcador de origen
        fig.add_trace(go.Scattergeo(
            lon=[row["Origin_Lon"]],
            lat=[row["Origin_Lat"]],
            mode='markers',
            marker=dict(size=8, color='blue', symbol='circle'),
            text=row["Origen"],
            hovertemplate=f"<b>Origen:</b> {row['Origen']}<br><b>ID:</b> {row['ID']}<extra></extra>",
            showlegend=False
        ))
        
        # Marcador de destino
        fig.add_trace(go.Scattergeo(
            lon=[row["Dest_Lon"]],
            lat=[row["Dest_Lat"]],
            mode='markers',
            marker=dict(size=10, color=color, symbol='square'),
            text=row["Destino"],
            hovertemplate=f"<b>Destino:</b> {row['Destino']}<br><b>Estado:</b> {row['Estado']}<br><b>Riesgo:</b> {row['Score_Riesgo']}<extra></extra>",
            showlegend=False
        ))
    
    fig.update_layout(
        title="Mapa de Rutas Logísticas",
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='rgb(243, 243, 243)',
            coastlinecolor='rgb(204, 204, 204)',
            showcountries=True,
            countrycolor='rgb(204, 204, 204)',
            showocean=True,
            oceancolor='rgb(230, 245, 255)',
            center=dict(lat=15, lon=-50),
            projection_scale=1.5
        ),
        height=500,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

# Header
st.title("🚢 Supply Chain Resilience Platform")
st.markdown("**Monitoreo en tiempo real y predicción de riesgos en cadena de suministro**")

# Sidebar para parámetros
with st.sidebar:
    st.header("⚙️ Configuración")
    
    num_shipments = st.slider(
        "Número de envíos a simular",
        min_value=20,
        max_value=100,
        value=50,
        step=10
    )
    
    risk_threshold = st.slider(
        "Umbral de riesgo crítico",
        min_value=50,
        max_value=90,
        value=70,
        step=5,
        help="Score de riesgo por encima del cual se considera crítico"
    )
    
    stockout_buffer = st.slider(
        "Días de buffer antes de desabasto",
        min_value=3,
        max_value=10,
        value=5,
        step=1,
        help="Días de margen de seguridad antes de quedarse sin inventario"
    )
    
    status_filter = st.selectbox(
        "Filtrar por estado",
        ["Todos", "CRÍTICO", "ALTO RIESGO", "RIESGO MEDIO", "NORMAL"]
    )
    
    st.markdown("---")
    st.markdown("### 📊 Leyenda de Riesgo")
    st.markdown("🔴 **Crítico**: Desabasto inminente")
    st.markdown("🟡 **Alto**: Riesgo de desabasto")
    st.markdown("🟢 **Normal**: Inventario suficiente")

# Generar datos
df = generate_supply_chain_data(num_shipments)

# Agregar predicción de desabasto
df["Predicción_Desabasto"], df["Indicador"] = zip(*df.apply(
    lambda row: predict_stockout_risk(
        row["Inventario_Actual"],
        row["Consumo_Diario"],
        row["Tránsito_Total"],
        stockout_buffer
    ), axis=1
))

# Métricas principales
col1, col2, col3, col4 = st.columns(4)

with col1:
    critical_count = len(df[df["Estado"] == "CRÍTICO"])
    st.metric("Envíos Críticos", critical_count, delta=None if critical_count == 0 else f"-{critical_count}")

with col2:
    avg_risk = df["Score_Riesgo"].mean()
    st.metric("Score Riesgo Promedio", f"{avg_risk:.1f}", delta=f"{avg_risk-50:.1f}")

with col3:
    high_risk = len(df[df["Score_Riesgo"] > risk_threshold])
    st.metric("Envíos Alto Riesgo", high_risk)

with col4:
    avg_delay = df["Retraso"].mean()
    st.metric("Retraso Promedio", f"{avg_delay:.1f} días")

st.markdown("---")

# Mapa de rutas
st.subheader("🗺️ Visualización de Rutas Logísticas")
route_map = create_route_map(df, status_filter)
st.plotly_chart(route_map, use_container_width=True)

st.markdown("---")

# Tabla de envíos con alertas
st.subheader("📦 Tabla de Envíos y Alertas")

# Filtrar por estado si es necesario
if status_filter != "Todos":
    df_display = df[df["Estado"] == status_filter]
else:
    df_display = df

# Ordenar por criticidad
df_display = df_display.sort_values("Score_Riesgo", ascending=False)

# Seleccionar columnas relevantes
display_cols = [
    "Indicador", "ID", "Origen", "Destino", "Estado",
    "Tránsito_Total", "ETA", "Inventario_Actual",
    "Días_Stock_Cero", "Score_Riesgo", "Predicción_Desabasto"
]

# Función para colorear filas
def highlight_risk(row):
    if row["Estado"] == "CRÍTICO":
        return ['background-color: #ffcccc'] * len(row)
    elif row["Estado"] == "ALTO RIESGO":
        return ['background-color: #ffe6cc'] * len(row)
    elif row["Estado"] == "RIESGO MEDIO":
        return ['background-color: #ffffcc'] * len(row)
    else:
        return [''] * len(row)

st.dataframe(
    df_display[display_cols].style.apply(highlight_risk, axis=1),
    use_container_width=True,
    height=400
)

# Gráficos de análisis
st.markdown("---")
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Distribución de Riesgo")
    fig_risk = px.histogram(
        df,
        x="Score_Riesgo",
        nbins=20,
        color="Estado",
        color_discrete_map={
            "CRÍTICO": "red",
            "ALTO RIESGO": "orange",
            "RIESGO MEDIO": "yellow",
            "NORMAL": "green"
        },
        labels={"Score_Riesgo": "Score de Riesgo", "count": "Número de Envíos"}
    )
    st.plotly_chart(fig_risk, use_container_width=True)

with col2:
    st.subheader("⏱️ Análisis de Retrasos")
    fig_delay = px.scatter(
        df,
        x="Tránsito_Base",
        y="Retraso",
        color="Score_Riesgo",
        size="Score_Riesgo",
        hover_data=["ID", "Estado"],
        labels={
            "Tránsito_Base": "Días de Tránsito Base",
            "Retraso": "Días de Retraso",
            "Score_Riesgo": "Score de Riesgo"
        },
        color_continuous_scale="reds"
    )
    st.plotly_chart(fig_delay, use_container_width=True)

# Análisis de factores de riesgo
st.markdown("---")
st.subheader("🔍 Análisis de Factores de Riesgo")

col1, col2, col3 = st.columns(3)

with col1:
    avg_climate = df["Riesgo_Clima"].mean()
    st.metric("Riesgo Climático Promedio", f"{avg_climate:.1f}")
    st.progress(avg_climate / 100)

with col2:
    avg_congestion = df["Congestión_Puerto"].mean()
    st.metric("Congestión Portuaria Promedio", f"{avg_congestion:.1f}")
    st.progress(avg_congestion / 100)

with col3:
    avg_stability = df["Estabilidad_Social"].mean()
    st.metric("Inestabilidad Social Promedio", f"{avg_stability:.1f}")
    st.progress(avg_stability / 100)

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
        <p>Supply Chain Resilience Platform v1.0 | Powered by Streamlit & Plotly</p>
        <p>Datos sintéticos generados para demostración</p>
    </div>
    """,
    unsafe_allow_html=True
)
