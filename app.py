import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random
from plotly.subplots import make_subplots

# Configuración de la página
st.set_page_config(
    page_title="Supply Chain Resilience Platform Pro",
    page_icon="🚢",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar la apariencia
st.markdown("""
<style>
    .main {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        background-attachment: fixed;
    }
    .stApp {
        background: rgba(255, 255, 255, 0.95);
    }
    div[data-testid="metric-container"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        color: white;
    }
    div[data-testid="metric-container"] label {
        color: white !important;
    }
    div[data-testid="metric-container"] [data-testid="stMetricValue"] {
        color: white;
        font-size: 2rem;
        font-weight: bold;
    }
    .css-1d391kg {
        background: white;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    h1 {
        color: #667eea;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    h2, h3 {
        color: #764ba2;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# INICIALIZACIÓN DE DATOS
# ============================================

if 'shipments_data' not in st.session_state:
    st.session_state.shipments_data = []

if 'vessel_positions' not in st.session_state:
    st.session_state.vessel_positions = {}

ORIGIN_PORTS = {
    "Ningbo, China": {"lat": 29.8683, "lon": 121.5440, "code": "CNNGB"},
    "Shanghai, China": {"lat": 31.2304, "lon": 121.4737, "code": "CNSHA"},
    "Busan, Corea del Sur": {"lat": 35.1796, "lon": 129.0756, "code": "KRPUS"},
    "Singapur": {"lat": 1.3521, "lon": 103.8198, "code": "SGSIN"},
    "Hong Kong": {"lat": 22.3193, "lon": 114.1694, "code": "HKHKG"},
    "Shenzhen, China": {"lat": 22.5431, "lon": 114.0579, "code": "CNSZX"}
}

DESTINATION_PORTS = {
    "Puerto Caucedo, RD": {"lat": 18.4264, "lon": -69.6618, "code": "DOCAU"},
    "Puerto de Balboa, Panamá": {"lat": 8.9517, "lon": -79.5671, "code": "PABLB"},
    "Puerto de Colón, Panamá": {"lat": 9.3592, "lon": -79.9009, "code": "PAONX"},
    "Puerto de Cartagena, Colombia": {"lat": 10.3932, "lon": -75.5144, "code": "COCTG"},
    "Puerto de Veracruz, México": {"lat": 19.2006, "lon": -96.1429, "code": "MXVER"}
}

# Tipos de carga
CARGO_TYPES = ["Electrónicos", "Textiles", "Maquinaria", "Alimentos", "Químicos", "Automotriz"]

# ============================================
# FUNCIONES DE SIMULACIÓN AVANZADA
# ============================================

def calculate_vessel_position(origin, destination, days_elapsed, total_days):
    """Calcula la posición actual del barco en su ruta"""
    progress = min(days_elapsed / total_days, 1.0)
    
    lat = origin["lat"] + (destination["lat"] - origin["lat"]) * progress
    lon = origin["lon"] + (destination["lon"] - origin["lon"]) * progress
    
    # Agregar algo de variación para simular rutas marítimas
    variation = np.sin(progress * np.pi) * 2
    lat += variation
    
    return {"lat": lat, "lon": lon, "progress": progress * 100}

def calculate_risk_score(climate, congestion, stability):
    return round(climate * 0.3 + congestion * 0.5 + stability * 0.2, 1)

def calculate_status(risk_score, days_to_zero, transit_total):
    if days_to_zero < transit_total:
        return "CRÍTICO"
    elif risk_score > 70:
        return "ALTO RIESGO"
    elif risk_score > 40:
        return "RIESGO MEDIO"
    else:
        return "NORMAL"

def generate_shipment_data(form_data=None):
    """Genera un nuevo envío con datos detallados"""
    if form_data:
        origin = form_data["origin"]
        destination = form_data["destination"]
        transit_base = form_data["transit_base"]
        inventory = form_data["inventory"]
        consumption = form_data["consumption"]
        climate = form_data["climate"]
        congestion = form_data["congestion"]
        stability = form_data["stability"]
        cargo_type = form_data["cargo_type"]
        cargo_value = form_data["cargo_value"]
    else:
        origin = random.choice(list(ORIGIN_PORTS.keys()))
        destination = random.choice(list(DESTINATION_PORTS.keys()))
        transit_base = random.randint(25, 40)
        inventory = random.randint(100, 500)
        consumption = random.randint(5, 25)
        climate = random.randint(0, 100)
        congestion = random.randint(0, 100)
        stability = random.randint(0, 100)
        cargo_type = random.choice(CARGO_TYPES)
        cargo_value = random.randint(50000, 500000)
    
    risk_score = calculate_risk_score(climate, congestion, stability)
    delay = int((risk_score / 100) * 15)
    transit_total = transit_base + delay
    days_to_zero = inventory / consumption
    eta = datetime.now() + timedelta(days=transit_total)
    status = calculate_status(risk_score, days_to_zero, transit_total)
    
    # Calcular fecha de zarpe
    departure_date = datetime.now() - timedelta(days=random.randint(0, 10))
    days_in_transit = (datetime.now() - departure_date).days
    
    vessel_id = f"VSL-{random.randint(1000, 9999)}"
    
    shipment = {
        "ID": f"SHP-{1000+len(st.session_state.shipments_data)}",
        "Vessel_ID": vessel_id,
        "Origen": origin,
        "Destino": destination,
        "Origin_Lat": ORIGIN_PORTS[origin]["lat"],
        "Origin_Lon": ORIGIN_PORTS[origin]["lon"],
        "Dest_Lat": DESTINATION_PORTS[destination]["lat"],
        "Dest_Lon": DESTINATION_PORTS[destination]["lon"],
        "Tránsito_Base": transit_base,
        "Retraso": delay,
        "Tránsito_Total": transit_total,
        "Días_Transcurridos": days_in_transit,
        "ETA": eta.strftime("%Y-%m-%d"),
        "Fecha_Zarpe": departure_date.strftime("%Y-%m-%d"),
        "Inventario_Actual": inventory,
        "Consumo_Diario": consumption,
        "Días_Stock_Cero": round(days_to_zero, 1),
        "Riesgo_Clima": climate,
        "Congestión_Puerto": congestion,
        "Estabilidad_Social": stability,
        "Score_Riesgo": risk_score,
        "Estado": status,
        "Tipo_Carga": cargo_type,
        "Valor_Carga_USD": cargo_value,
        "Velocidad_Nudos": round(random.uniform(12, 18), 1),
        "Distancia_Restante_NM": round((1 - (days_in_transit / transit_total)) * random.uniform(8000, 12000), 0),
        "Fecha_Creación": datetime.now().strftime("%Y-%m-%d %H:%M")
    }
    
    # Calcular posición actual del barco
    vessel_pos = calculate_vessel_position(
        ORIGIN_PORTS[origin],
        DESTINATION_PORTS[destination],
        days_in_transit,
        transit_total
    )
    
    st.session_state.vessel_positions[vessel_id] = vessel_pos
    
    return shipment

def predict_stockout_risk(inventory, daily_consumption, transit_days, threshold_days=5):
    days_to_stockout = inventory / daily_consumption
    buffer = days_to_stockout - transit_days
    
    if buffer < 0:
        return "DESABASTO INMINENTE", "🔴"
    elif buffer < threshold_days:
        return "RIESGO ALTO", "🟡"
    else:
        return "NORMAL", "🟢"

# ============================================
# FUNCIONES DE VISUALIZACIÓN AVANZADA
# ============================================

def create_advanced_route_map(df, selected_status, show_vessels=True):
    """Crea un mapa 3D interactivo con rutas y barcos"""
    if df.empty:
        return None
    
    if selected_status != "Todos":
        df_filtered = df[df["Estado"] == selected_status]
    else:
        df_filtered = df
    
    if df_filtered.empty:
        return None
    
    fig = go.Figure()
    
    color_map = {
        "CRÍTICO": "#FF0000",
        "ALTO RIESGO": "#FF8C00",
        "RIESGO MEDIO": "#FFD700",
        "NORMAL": "#00FF00"
    }
    
    # Agregar rutas con animación
    for idx, row in df_filtered.iterrows():
        color = color_map.get(row["Estado"], "blue")
        
        # Línea de ruta con gradiente
        fig.add_trace(go.Scattergeo(
            lon=[row["Origin_Lon"], row["Dest_Lon"]],
            lat=[row["Origin_Lat"], row["Dest_Lat"]],
            mode='lines',
            line=dict(width=3, color=color),
            opacity=0.7,
            hoverinfo='skip',
            showlegend=False
        ))
        
        # Marcador de origen (grande)
        fig.add_trace(go.Scattergeo(
            lon=[row["Origin_Lon"]],
            lat=[row["Origin_Lat"]],
            mode='markers+text',
            marker=dict(size=15, color='#1E90FF', symbol='circle', 
                       line=dict(width=2, color='white')),
            text=row["Origen"].split(",")[0],
            textposition="top center",
            textfont=dict(size=10, color='black', family='Arial Black'),
            hovertemplate=f"<b>Puerto Origen:</b> {row['Origen']}<br><b>ID Envío:</b> {row['ID']}<extra></extra>",
            showlegend=False
        ))
        
        # Marcador de destino (grande)
        fig.add_trace(go.Scattergeo(
            lon=[row["Dest_Lon"]],
            lat=[row["Dest_Lat"]],
            mode='markers+text',
            marker=dict(size=18, color=color, symbol='square',
                       line=dict(width=2, color='white')),
            text=row["Destino"].split(",")[0],
            textposition="bottom center",
            textfont=dict(size=10, color='black', family='Arial Black'),
            hovertemplate=f"<b>Puerto Destino:</b> {row['Destino']}<br><b>Estado:</b> {row['Estado']}<br><b>ETA:</b> {row['ETA']}<extra></extra>",
            showlegend=False
        ))
        
        # Posición del barco en tránsito
        if show_vessels and row["Vessel_ID"] in st.session_state.vessel_positions:
            vessel_pos = st.session_state.vessel_positions[row["Vessel_ID"]]
            
            fig.add_trace(go.Scattergeo(
                lon=[vessel_pos["lon"]],
                lat=[vessel_pos["lat"]],
                mode='markers+text',
                marker=dict(
                    size=20,
                    color='white',
                    symbol='circle',
                    line=dict(width=3, color=color)
                ),
                text='🚢',
                textfont=dict(size=20),
                hovertemplate=f"""
                <b>Vessel ID:</b> {row['Vessel_ID']}<br>
                <b>Envío:</b> {row['ID']}<br>
                <b>Progreso:</b> {vessel_pos['progress']:.1f}%<br>
                <b>Velocidad:</b> {row['Velocidad_Nudos']} nudos<br>
                <b>Distancia restante:</b> {row['Distancia_Restante_NM']:.0f} NM<br>
                <b>Tipo carga:</b> {row['Tipo_Carga']}<br>
                <b>Valor:</b> ${row['Valor_Carga_USD']:,.0f}<br>
                <b>Estado:</b> {row['Estado']}<br>
                <extra></extra>
                """,
                showlegend=False
            ))
    
    fig.update_layout(
        title={
            'text': "🌍 Mapa Global de Rutas y Tracking en Tiempo Real",
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20, 'color': '#667eea', 'family': 'Arial Black'}
        },
        geo=dict(
            projection_type='natural earth',
            showland=True,
            landcolor='#F5F5DC',
            coastlinecolor='#2F4F4F',
            coastlinewidth=2,
            showcountries=True,
            countrycolor='#696969',
            countrywidth=1,
            showocean=True,
            oceancolor='#E0F6FF',
            showlakes=True,
            lakecolor='#B0E0E6',
            center=dict(lat=15, lon=-50),
            projection_scale=1.3
        ),
        height=600,
        margin=dict(l=0, r=0, t=50, b=0),
        paper_bgcolor='rgba(255,255,255,0.95)'
    )
    
    return fig

def create_risk_timeline(df):
    """Crea una línea de tiempo de riesgos por envío"""
    fig = go.Figure()
    
    df_sorted = df.sort_values('Score_Riesgo', ascending=True)
    
    colors = df_sorted['Estado'].map({
        'CRÍTICO': '#FF0000',
        'ALTO RIESGO': '#FF8C00',
        'RIESGO MEDIO': '#FFD700',
        'NORMAL': '#00FF00'
    })
    
    fig.add_trace(go.Bar(
        y=df_sorted['ID'],
        x=df_sorted['Score_Riesgo'],
        orientation='h',
        marker=dict(
            color=colors,
            line=dict(color='white', width=2)
        ),
        text=df_sorted['Score_Riesgo'].round(1),
        textposition='outside',
        hovertemplate='<b>%{y}</b><br>Score: %{x:.1f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='📊 Score de Riesgo por Envío',
        xaxis_title='Score de Riesgo (0-100)',
        yaxis_title='ID de Envío',
        height=max(400, len(df) * 30),
        showlegend=False,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(255,255,255,0.95)',
        font=dict(size=12)
    )
    
    fig.add_vline(x=40, line_dash="dash", line_color="orange", annotation_text="Medio")
    fig.add_vline(x=70, line_dash="dash", line_color="red", annotation_text="Crítico")
    
    return fig

def create_inventory_gauge(df):
    """Crea gauges para inventarios críticos"""
    fig = make_subplots(
        rows=1, cols=min(4, len(df)),
        specs=[[{'type': 'indicator'}] * min(4, len(df))],
        subplot_titles=[f"{row['ID']}" for _, row in df.head(4).iterrows()]
    )
    
    for idx, (_, row) in enumerate(df.head(4).iterrows(), 1):
        days_left = row['Días_Stock_Cero']
        transit = row['Tránsito_Total']
        
        fig.add_trace(go.Indicator(
            mode="gauge+number+delta",
            value=days_left,
            title={'text': f"Días de Stock"},
            delta={'reference': transit, 'increasing': {'color': "green"}, 'decreasing': {'color': "red"}},
            gauge={
                'axis': {'range': [0, max(days_left, transit) * 1.2]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, transit * 0.5], 'color': "lightcoral"},
                    {'range': [transit * 0.5, transit], 'color': "lightyellow"},
                    {'range': [transit, max(days_left, transit) * 1.2], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': transit
                }
            }
        ), row=1, col=idx)
    
    fig.update_layout(
        height=300,
        showlegend=False,
        paper_bgcolor='rgba(255,255,255,0.95)',
        font=dict(size=10)
    )
    
    return fig

def create_3d_risk_scatter(df):
    """Crea un scatter 3D de riesgos"""
    fig = go.Figure(data=[go.Scatter3d(
        x=df['Riesgo_Clima'],
        y=df['Congestión_Puerto'],
        z=df['Estabilidad_Social'],
        mode='markers+text',
        marker=dict(
            size=df['Score_Riesgo'] / 5,
            color=df['Score_Riesgo'],
            colorscale='Reds',
            showscale=True,
            colorbar=dict(title="Score<br>Riesgo"),
            line=dict(color='white', width=2)
        ),
        text=df['ID'],
        textposition='top center',
        hovertemplate='<b>%{text}</b><br>Clima: %{x}<br>Congestión: %{y}<br>Social: %{z}<br>Score: %{marker.color:.1f}<extra></extra>'
    )])
    
    fig.update_layout(
        title='🎲 Análisis 3D de Factores de Riesgo',
        scene=dict(
            xaxis_title='Riesgo Climático',
            yaxis_title='Congestión Portuaria',
            zaxis_title='Inestabilidad Social',
            camera=dict(eye=dict(x=1.5, y=1.5, z=1.3))
        ),
        height=500,
        paper_bgcolor='rgba(255,255,255,0.95)'
    )
    
    return fig

def create_value_at_risk_chart(df):
    """Calcula y visualiza el valor en riesgo"""
    df['Valor_en_Riesgo'] = df['Valor_Carga_USD'] * (df['Score_Riesgo'] / 100)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=df['ID'],
        y=df['Valor_Carga_USD'],
        name='Valor Total',
        marker_color='lightblue',
        hovertemplate='<b>%{x}</b><br>Valor Total: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.add_trace(go.Bar(
        x=df['ID'],
        y=df['Valor_en_Riesgo'],
        name='Valor en Riesgo',
        marker_color='coral',
        hovertemplate='<b>%{x}</b><br>Valor en Riesgo: $%{y:,.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title='💰 Valor en Riesgo por Envío',
        xaxis_title='ID de Envío',
        yaxis_title='Valor USD',
        barmode='overlay',
        height=400,
        paper_bgcolor='rgba(255,255,255,0.95)',
        legend=dict(x=0.01, y=0.99)
    )
    
    return fig

# ============================================
# INTERFAZ PRINCIPAL
# ============================================

st.title("🚢 Supply Chain Resilience Platform Pro")
st.markdown("### *Monitoreo Avanzado con Tracking en Tiempo Real*")

# ============================================
# SIDEBAR MEJORADO
# ============================================

with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3774/3774299.png", width=100)
    st.title("⚙️ Panel de Control")
    
    tabs = st.tabs(["📝 Nuevo Envío", "🔧 Configuración", "💾 Datos"])
    
    # TAB 1: FORMULARIO DETALLADO
    with tabs[0]:
        st.subheader("Crear Nuevo Envío")
        
        with st.form("detailed_shipment_form", clear_on_submit=True):
            st.markdown("**📍 Ubicaciones**")
            col1, col2 = st.columns(2)
            with col1:
                origin = st.selectbox("🏭 Origen", list(ORIGIN_PORTS.keys()), key="origin")
            with col2:
                destination = st.selectbox("🏪 Destino", list(DESTINATION_PORTS.keys()), key="dest")
            
            st.markdown("**🚢 Detalles del Envío**")
            col1, col2 = st.columns(2)
            with col1:
                cargo_type = st.selectbox("📦 Tipo de Carga", CARGO_TYPES)
                transit_base = st.number_input("⏱️ Tránsito Base (días)", 20, 50, 30)
            with col2:
                cargo_value = st.number_input("💵 Valor Carga (USD)", 10000, 1000000, 100000, 10000)
            
            st.markdown("**📊 Inventario**")
            col1, col2 = st.columns(2)
            with col1:
                inventory = st.number_input("📦 Inventario Actual", 50, 1000, 200, 10)
            with col2:
                consumption = st.number_input("📉 Consumo Diario", 1, 100, 15, 1)
            
            st.markdown("**⚠️ Factores de Riesgo (0-100)**")
            climate = st.slider("🌤️ Riesgo Climático", 0, 100, 30, 5, 
                              help="Tormentas, huracanes, condiciones marítimas adversas")
            congestion = st.slider("🚧 Congestión Portuaria", 0, 100, 50, 5,
                                 help="Retrasos en puerto, carga/descarga")
            stability = st.slider("⚡ Inestabilidad Social", 0, 100, 20, 5,
                                help="Huelgas, conflictos, restricciones")
            
            submitted = st.form_submit_button("🚀 Crear Envío", use_container_width=True)
            
            if submitted:
                form_data = {
                    "origin": origin,
                    "destination": destination,
                    "transit_base": transit_base,
                    "inventory": inventory,
                    "consumption": consumption,
                    "climate": climate,
                    "congestion": congestion,
                    "stability": stability,
                    "cargo_type": cargo_type,
                    "cargo_value": cargo_value
                }
                
                new_shipment = generate_shipment_data(form_data)
                st.session_state.shipments_data.append(new_shipment)
                st.success(f"✅ Envío {new_shipment['ID']} creado exitosamente!")
                st.balloons()
                st.rerun()
    
    # TAB 2: CONFIGURACIÓN
    with tabs[1]:
        st.subheader("Configuración de Visualización")
        
        risk_threshold = st.slider("🎯 Umbral Riesgo Crítico", 50, 90, 70, 5)
        stockout_buffer = st.slider("⏰ Buffer Días", 3, 15, 5, 1)
        status_filter = st.selectbox("🔍 Filtrar Estado", 
                                    ["Todos", "CRÍTICO", "ALTO RIESGO", "RIESGO MEDIO", "NORMAL"])
        show_vessels = st.checkbox("🚢 Mostrar Barcos en Mapa", value=True)
        
        st.markdown("---")
        st.markdown("**🎨 Tema de Visualización**")
        chart_theme = st.radio("Seleccionar tema", ["Claro", "Oscuro"], horizontal=True)
    
    # TAB 3: GESTIÓN DE DATOS
    with tabs[2]:
        st.subheader("Gestión de Datos")
        
        col1, col2 = st.columns(2)
        with col1:
            num_samples = st.number_input("Cantidad", 5, 50, 10, 5)
            if st.button("🎲 Generar Datos", use_container_width=True):
                for _ in range(num_samples):
                    st.session_state.shipments_data.append(generate_shipment_data())
                st.success(f"✅ {num_samples} envíos generados")
                st.rerun()
        
        with col2:
            if st.button("🗑️ Limpiar Todo", use_container_width=True):
                st.session_state.shipments_data = []
                st.session_state.vessel_positions = {}
                st.success("✅ Datos limpiados")
                st.rerun()
        
        st.markdown(f"**📊 Total de envíos:** {len(st.session_state.shipments_data)}")
        
        if st.session_state.shipments_data:
            df_export = pd.DataFrame(st.session_state.shipments_data)
            csv = df_export.to_csv(index=False)
            st.download_button(
                label="📥 Exportar CSV",
                data=csv,
                file_name=f"shipments_{datetime.now().strftime('%Y%m%d_%H%M')}.csv",
                mime="text/csv",
                use_container_width=True
            )

# ============================================
# DASHBOARD PRINCIPAL
# ============================================

df = pd.DataFrame(st.session_state.shipments_data)

if df.empty:
    st.info("👆 **No hay envíos registrados.** Usa el panel lateral para crear envíos o generar datos de ejemplo.")
    
    # Mostrar demo visual
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Envíos Totales", "0", "Crear nuevo")
    with col2:
        st.metric("Riesgo Promedio", "N/A", "Sin datos")
    with col3:
        st.metric("Valor Total", "$0", "Sin carga")
    
    st.stop()

# Agregar predicción
df["Predicción_Desabasto"], df["Indicador"] = zip(*df.apply(
    lambda row: predict_stockout_risk(
        row["Inventario_Actual"],
        row["Consumo_Diario"],
        row["Tránsito_Total"],
        stockout_buffer
    ), axis=1
))

# ============================================
# MÉTRICAS PRINCIPALES MEJORADAS
# ============================================

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    critical = len(df[df["Estado"] == "CRÍTICO"])
    st.metric("🔴 Críticos", critical, 
             delta=f"-{critical}" if critical > 0 else "OK",
             delta_color="inverse")

with col2:
    avg_risk = df["Score_Riesgo"].mean()
    st.metric("⚠️ Riesgo Promedio", f"{avg_risk:.1f}", 
             delta=f"{avg_risk-50:.1f}",
             delta_color="inverse")

with col3:
    high_risk = len(df[df["Score_Riesgo"] > risk_threshold])
    st.metric("🟠 Alto Riesgo", high_risk)

with col4:
    total_value = df["Valor_Carga_USD"].sum()
    st.metric("💰 Valor Total", f"${total_value/1000:.0f}K")

with col5:
    in_transit = len(df)
    st.metric("🚢 En Tránsito", in_transit)

st.markdown("---")

# ============================================
# MAPA AVANZADO
# ============================================

st.subheader("🗺️ Mapa de Tracking Global en Tiempo Real")

col1, col2 = st.columns([3, 1])

with col2:
    st.markdown("**🎛️ Controles del Mapa**")
    st.info(f"""
    **Leyenda de Estados:**
    - 🔴 CRÍTICO
    - 🟠 ALTO RIESGO  
    - 🟡 RIESGO MEDIO
    - 🟢 NORMAL
    
    **Símbolos:**
    - 🔵 Puerto Origen
    - ⬜ Puerto Destino
    - 🚢 Barco en tránsito
    """)
    
    # Info adicional
    if status_filter != "Todos":
        filtered_count = len(df[df["Estado"] == status_filter])
        st.metric(f"Envíos {status_filter}", filtered_count)

with col1:
    route_map = create_advanced_route_map(df, status_filter, show_vessels)
    if route_map:
        st.plotly_chart(route_map, use_container_width=True)

st.markdown("---")

# ============================================
# ANÁLISIS DE INVENTARIOS CRÍTICOS
# ============================================

st.subheader("📦 Dashboard de Inventarios Críticos")

critical_inventory = df.nsmallest(4, 'Días_Stock_Cero')

if not critical_inventory.empty:
    gauge_chart = create_inventory_gauge(critical_inventory)
    st.plotly_chart(gauge_chart, use_container_width=True)
    
    st.caption("*Los gauges muestran días de stock disponible vs. días de tránsito restantes. La línea roja indica el ETA.*")

st.markdown("---")

# ============================================
# GRÁFICOS AVANZADOS EN GRID
# ============================================

st.subheader("📊 Análisis Multidimensional de Riesgos")

tab1, tab2, tab3, tab4 = st.tabs(["📈 Timeline Riesgos", "🎲 Análisis 3D", "💰 Valor en Riesgo", "📉 Distribuciones"])

with tab1:
    col1, col2 = st.columns([2, 1])
    with col1:
        risk_timeline = create_risk_timeline(df)
        st.plotly_chart(risk_timeline, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Top 5 Riesgos")
        top_risks = df.nlargest(5, 'Score_Riesgo')[['ID', 'Score_Riesgo', 'Estado', 'Tipo_Carga']]
        
        for idx, row in top_risks.iterrows():
            with st.container():
                st.markdown(f"""
                **{row['ID']}** - {row['Tipo_Carga']}  
                Score: **{row['Score_Riesgo']:.1f}** | {row['Estado']}
                """)
                st.progress(row['Score_Riesgo'] / 100)
                st.markdown("---")

with tab2:
    scatter_3d = create_3d_risk_scatter(df)
    st.plotly_chart(scatter_3d, use_container_width=True)
    
    st.info("🔍 **Interpretación:** Cada punto representa un envío. El tamaño y color indican el nivel de riesgo total. Rota el gráfico con el mouse.")

with tab3:
    value_risk = create_value_at_risk_chart(df)
    st.plotly_chart(value_risk, use_container_width=True)
    
    total_at_risk = (df['Valor_Carga_USD'] * (df['Score_Riesgo'] / 100)).sum()
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("💵 Valor Total Transportado", f"${df['Valor_Carga_USD'].sum():,.0f}")
    with col2:
        st.metric("⚠️ Valor en Riesgo", f"${total_at_risk:,.0f}")
    with col3:
        risk_percentage = (total_at_risk / df['Valor_Carga_USD'].sum()) * 100
        st.metric("📊 % en Riesgo", f"{risk_percentage:.1f}%")

with tab4:
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Distribución de Riesgos**")
        fig_hist = px.histogram(
            df,
            x="Score_Riesgo",
            nbins=20,
            color="Estado",
            color_discrete_map={
                "CRÍTICO": "#FF0000",
                "ALTO RIESGO": "#FF8C00",
                "RIESGO MEDIO": "#FFD700",
                "NORMAL": "#00FF00"
            },
            title="Histograma de Scores de Riesgo"
        )
        fig_hist.update_layout(height=350, paper_bgcolor='rgba(255,255,255,0.95)')
        st.plotly_chart(fig_hist, use_container_width=True)
    
    with col2:
        st.markdown("**Distribución por Tipo de Carga**")
        fig_pie = px.pie(
            df,
            names="Tipo_Carga",
            values="Valor_Carga_USD",
            title="Valor por Tipo de Carga",
            hole=0.4
        )
        fig_pie.update_layout(height=350, paper_bgcolor='rgba(255,255,255,0.95)')
        st.plotly_chart(fig_pie, use_container_width=True)

st.markdown("---")

# ============================================
# TABLA INTERACTIVA DETALLADA
# ============================================

st.subheader("📋 Tabla Detallada de Envíos")

# Filtrar datos
if status_filter != "Todos":
    df_display = df[df["Estado"] == status_filter]
else:
    df_display = df

df_display = df_display.sort_values("Score_Riesgo", ascending=False)

# Selector de columnas
all_columns = df_display.columns.tolist()
default_cols = [
    "Indicador", "ID", "Vessel_ID", "Origen", "Destino", "Estado",
    "Tipo_Carga", "Valor_Carga_USD", "Tránsito_Total", "Días_Transcurridos",
    "ETA", "Inventario_Actual", "Días_Stock_Cero", "Score_Riesgo",
    "Velocidad_Nudos", "Distancia_Restante_NM"
]

selected_cols = st.multiselect(
    "Selecciona columnas a mostrar:",
    all_columns,
    default=[col for col in default_cols if col in all_columns]
)

if selected_cols:
    def highlight_risk(row):
        if row["Estado"] == "CRÍTICO":
            return ['background-color: #ffcccc'] * len(row)
        elif row["Estado"] == "ALTO RIESGO":
            return ['background-color: #ffe6cc'] * len(row)
        elif row["Estado"] == "RIESGO MEDIO":
            return ['background-color: #ffffcc'] * len(row)
        else:
            return ['background-color: #ccffcc'] * len(row)
    
    st.dataframe(
        df_display[selected_cols].style.apply(highlight_risk, axis=1),
        use_container_width=True,
        height=400
    )

st.markdown("---")

# ============================================
# ANÁLISIS COMPARATIVO
# ============================================

st.subheader("🔬 Análisis Comparativo de Factores")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown("**🌤️ Riesgo Climático**")
    avg_climate = df["Riesgo_Clima"].mean()
    st.metric("Promedio", f"{avg_climate:.1f}")
    st.progress(avg_climate / 100)
    
    fig_climate = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_climate,
        title={'text': "Clima"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "lightblue"},
               'steps': [
                   {'range': [0, 40], 'color': "lightgreen"},
                   {'range': [40, 70], 'color': "yellow"},
                   {'range': [70, 100], 'color': "red"}
               ]}
    ))
    fig_climate.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_climate, use_container_width=True)

with col2:
    st.markdown("**🚧 Congestión Portuaria**")
    avg_congestion = df["Congestión_Puerto"].mean()
    st.metric("Promedio", f"{avg_congestion:.1f}")
    st.progress(avg_congestion / 100)
    
    fig_congestion = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_congestion,
        title={'text': "Congestión"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "orange"},
               'steps': [
                   {'range': [0, 40], 'color': "lightgreen"},
                   {'range': [40, 70], 'color': "yellow"},
                   {'range': [70, 100], 'color': "red"}
               ]}
    ))
    fig_congestion.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_congestion, use_container_width=True)

with col3:
    st.markdown("**⚡ Inestabilidad Social**")
    avg_stability = df["Estabilidad_Social"].mean()
    st.metric("Promedio", f"{avg_stability:.1f}")
    st.progress(avg_stability / 100)
    
    fig_stability = go.Figure(go.Indicator(
        mode="gauge+number",
        value=avg_stability,
        title={'text': "Social"},
        gauge={'axis': {'range': [0, 100]},
               'bar': {'color': "purple"},
               'steps': [
                   {'range': [0, 40], 'color': "lightgreen"},
                   {'range': [40, 70], 'color': "yellow"},
                   {'range': [70, 100], 'color': "red"}
               ]}
    ))
    fig_stability.update_layout(height=200, margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_stability, use_container_width=True)

st.markdown("---")

# ============================================
# ANÁLISIS DE CORRELACIÓN
# ============================================

st.subheader("🔗 Matriz de Correlación de Factores")

correlation_data = df[['Riesgo_Clima', 'Congestión_Puerto', 'Estabilidad_Social', 
                       'Score_Riesgo', 'Retraso', 'Valor_Carga_USD']].corr()

fig_heatmap = px.imshow(
    correlation_data,
    text_auto='.2f',
    aspect="auto",
    color_continuous_scale='RdYlGn_r',
    title="Correlación entre Variables"
)
fig_heatmap.update_layout(height=400, paper_bgcolor='rgba(255,255,255,0.95)')
st.plotly_chart(fig_heatmap, use_container_width=True)

# ============================================
# FOOTER
# ============================================

st.markdown("---")
st.markdown("""
<div style='text-align: center; padding: 20px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 10px; color: white;'>
    <h3>🚢 Supply Chain Resilience Platform Pro v2.0</h3>
    <p>Powered by Streamlit & Plotly | Tracking en Tiempo Real | Análisis Predictivo Avanzado</p>
    <p><i>Datos sintéticos generados para demostración - Listo para integración con APIs reales</i></p>
</div>
""", unsafe_allow_html=True)
