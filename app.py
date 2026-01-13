import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
from plotly.subplots import make_subplots

# ============================================
# CONFIGURACIÓN Y ESTILOS
# ============================================
st.set_page_config(
    page_title="Global Supply Chain Resilience",
    page_icon="🚢",
    layout="wide"
)

# Inyectar CSS personalizado para mejorar la estética
st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    div[data-testid="metric-container"] {
        background-color: #ffffff;
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        padding: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# DATOS MAESTROS
# ============================================
ORIGIN_PORTS = {
    "Ningbo, China": {"lat": 29.86, "lon": 121.54},
    "Shanghai, China": {"lat": 31.23, "lon": 121.47},
    "Singapur": {"lat": 1.35, "lon": 103.81},
    "Busan, Corea": {"lat": 35.17, "lon": 129.07}
}

DESTINATION_PORTS = {
    "Puerto Caucedo, RD": {"lat": 18.42, "lon": -69.66},
    "Puerto de Balboa, Panamá": {"lat": 8.95, "lon": -79.56},
    "Puerto de Veracruz, México": {"lat": 19.20, "lon": -96.14}
}

# ============================================
# LÓGICA DE NEGOCIO
# ============================================
if 'shipments' not in st.session_state:
    st.session_state.shipments = []

def generate_data():
    o_name, o_coords = random.choice(list(ORIGIN_PORTS.items()))
    d_name, d_coords = random.choice(list(DESTINATION_PORTS.items()))
    
    clima = random.randint(10, 95)
    puerto = random.randint(10, 95)
    social = random.randint(10, 95)
    
    risk_score = round((clima * 0.3 + puerto * 0.5 + social * 0.2), 1)
    valor = random.randint(80000, 600000)
    
    status = "CRÍTICO" if risk_score > 75 else "ALTO" if risk_score > 55 else "NORMAL"
    
    return {
        "ID": f"SHP-{random.randint(1000, 9999)}",
        "Origen": o_name, "Destino": d_name,
        "Lat_O": o_coords["lat"], "Lon_O": o_coords["lon"],
        "Lat_D": d_coords["lat"], "Lon_D": d_coords["lon"],
        "Riesgo": risk_score, "Estado": status,
        "Valor_USD": valor, "Clima": clima, "Puerto": puerto
    }

# ============================================
# INTERFAZ DE USUARIO (UI)
# ============================================
st.title("🚢 Supply Chain Resilience Platform")

# Sidebar para controles
with st.sidebar:
    st.header("Control de Flota")
    if st.button("➕ Generar Nuevos Envíos"):
        for _ in range(5):
            st.session_state.shipments.append(generate_data())
    
    if st.button("🗑️ Resetear Datos"):
        st.session_state.shipments = []
        st.rerun()

df = pd.DataFrame(st.session_state.shipments)

if not df.empty:
    # Métricas clave
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Envíos Totales", len(df))
    c2.metric("Riesgo Promedio", f"{df['Riesgo'].mean():.1f}%")
    c3.metric("Valor en Riesgo", f"${(df['Valor_USD'].sum()/1e6):.2f}M")
    c4.metric("Alertas Críticas", len(df[df['Estado'] == 'CRÍTICO']))

    # Mapa de Rutas
    st.subheader("📍 Monitoreo Global en Tiempo Real")
    fig = go.Figure()

    for _, row in df.iterrows():
        color = "red" if row['Estado'] == 'CRÍTICO' else "orange" if row['Estado'] == 'ALTO' else "green"
        
        # Dibujar línea de ruta
        fig.add_trace(go.Scattergeo(
            lat=[row['Lat_O'], row['Lat_D']],
            lon=[row['Lon_O'], row['Lon_D']],
            mode='lines',
            line=dict(width=2, color=color),
            opacity=0.4,
            hoverinfo='none'
        ))
        
        # Dibujar punto de destino (Barco simulado)
        fig.add_trace(go.Scattergeo(
            lat=[row['Lat_D']], lon=[row['Lon_D']],
            mode='markers',
            marker=dict(size=10, color=color, symbol='diamond'),
            name=row['ID'],
            text=f"ID: {row['ID']}<br>Riesgo: {row['Riesgo']}%"
        ))

    fig.update_layout(geo=dict(projection_type='natural earth', showland=True, landcolor="#f0f0f0"),
                      margin=dict(l=0, r=0, t=0, b=0), height=500)
    st.plotly_chart(fig, use_container_width=True)

    # Tabla de Decisiones
    st.subheader("📋 Matriz de Decisiones Logísticas")
    st.dataframe(df[['ID', 'Origen', 'Destino', 'Riesgo', 'Estado', 'Valor_USD']], use_container_width=True)
    
else:
    st.info("Utiliza el panel lateral para generar datos y visualizar la red de suministros.")
