import streamlit as st
import requests
import os
import datetime

# --- CONFIGURACIÓN BASE ---
st.set_page_config(page_title="SmartOps VIVID", layout="wide", initial_sidebar_state="expanded")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# --- 1. INYECCIÓN DE ESTILO MATRIX (CSS OBLIGATORIO) ---
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&display=swap');

    /* Ocultar basura de Streamlit */
    #MainMenu, footer, header { visibility: hidden !important; display: none !important; }
    .stDeployButton, .viewerBadge_container__1QSob { display: none !important; }
    
    /* Fondo Absoluto y Texto Verde Matrix */
    .stApp {
        background-color: #000000 !important;
        color: #00FF41 !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    
    /* Tipografía Global Muted y Normal */
    p, label, span, div, h1, h2, h3, h4, h5, h6, .stMarkdown p {
        font-family: 'JetBrains Mono', monospace !important;
        color: #00FF41 !important;
    }

    /* Muted Text para headers chicos o placeholders */
    .muted-text { color: #555555 !important; }

    /* Estilo de Botones: Bordes 1px, Esquinas rectas, Fondo Tranparente */
    .stButton > button, .stFormSubmitButton > button {
        background-color: transparent !important;
        border: 1px solid #00FF41 !important;
        border-radius: 0px !important;
        color: #00FF41 !important;
        font-family: 'JetBrains Mono', monospace !important;
        box-shadow: none !important;
        padding: 8px 16px !important;
        transition: 0.2s all;
    }
    .stButton > button:hover, .stFormSubmitButton > button:hover {
        background-color: #00FF41 !important;
        color: #000000 !important;
    }

    /* Inputs y Selects */
    input, select, .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div {
        background-color: #000000 !important;
        color: #00FF41 !important;
        border: 1px solid rgba(0, 255, 65, 0.4) !important;
        border-radius: 0px !important;
        font-family: 'JetBrains Mono', monospace !important;
    }
    input:focus { border-color: #00FF41 !important; box-shadow: 0 0 5px #00FF41 !important; }

    /* Scrollbars Matrix */
    ::-webkit-scrollbar { width: 8px; }
    ::-webkit-scrollbar-track { background: #000000; }
    ::-webkit-scrollbar-thumb { background: #00FF41; border-radius: 0px; }
    
    /* Efecto "Terminal Glow" para titulos */
    .glow { text-shadow: 0 0 5px #00FF41; }

    /* Contenedores (Cards) transparentes con borde sutil */
    .matrix-card {
        border: 1px solid rgba(0, 255, 65, 0.2);
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Modos: CSS Variables dinámicas para el borde principal */
    .mode-expansion { border-top: 2px solid #00FF41 !important; }
    .mode-penalty { border-top: 2px solid #FF007A !important; }
</style>
""", unsafe_allow_html=True)

# Fetch Data
try:
    response = requests.get(f"{BACKEND_URL}/dashboard")
    data = response.json()
except:
    data = {"daily_power": 0.0, "penalty_days": 0, "debt_bosses": [], "state": "MODO_GUERRA", "projections": []}

daily_power = data.get("daily_power", 500.0) # Using default fallback if 0
penalty_days = data.get("penalty_days", 0)
debts = data.get("debt_bosses", [])

# 4. Lógica de "Modo Guerra" vs "Modo Expansión". 
# Si hay sobregiro/penalidades usa clase magenta, de lo contrario verde.
card_mode_class = "mode-penalty" if penalty_days > 0 or daily_power < 0 else "mode-expansion"
metric_color = "#FF007A" if daily_power < 0 else "#00FF41"


# --- 2. ARQUITECTURA DE NAVEGACIÓN (SIDEBAR) ---
st.sidebar.markdown("<h3 class='glow'>> SYSTEM_NAV</h3>", unsafe_allow_html=True)
pages = [
    "[01] TERMINAL",
    "[02] DASHBOARD",
    "[03] CRM_OPS",
    "[04] VAULTS",
    "[05] BOSS_RAID"
]
selection = st.sidebar.radio("Go to:", pages, label_visibility="collapsed")


# --- 3. IMPLEMENTACIÓN DEL HUD [01] TERMINAL ---
if selection == "[01] TERMINAL":
    # Header Táctico
    st.markdown("""
    <div style="display: flex; justify-content: space-between; border-bottom: 1px solid rgba(0, 255, 65, 0.2); margin-bottom: 20px; padding-bottom: 5px;">
        <span class="muted-text">[ STATUS: ONLINE ]</span>
        <span class="muted-text">[ LEVEL: 20K_GOAL ]</span>
        <span class="muted-text">[ RUNWAY: CALC_PENDING ]</span>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1.2, 1])

    with col1:
        # Métrica de Poder
        st.markdown(f"<div class='matrix-card {card_mode_class}'>", unsafe_allow_html=True)
        st.markdown("<h4 class='glow'>[ DAILY POWER ]</h4>", unsafe_allow_html=True)
        st.markdown(f"<h1 style='color: {metric_color} !important; text-shadow: 0 0 10px {metric_color};'>$ {daily_power:.2f}</h1>", unsafe_allow_html=True)
        
        if card_mode_class == "mode-penalty":
            st.markdown(f"<span style='color: #FF007A; font-weight: bold;'>[ PENALTY_MODE_ACTIVE: {penalty_days:.1f} DAYS ]</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"<span class='muted-text'>[ EXPANSION_MODE ] No Debts Detected.</span>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

        # Input de Comando
        st.markdown(f"<div class='matrix-card'>", unsafe_allow_html=True)
        with st.form("command_input"):
            st.markdown("<h4 class='glow'>[ QUICK_LOG ]</h4>", unsafe_allow_html=True)
            cmd_text = st.text_input("> AGREGAR_MOVIMIENTO:", placeholder="Ej: 50 Comida Expense (En desarrollo el parser de cmd)")
            
            # Temporary dropdowns until Natural Language parsing is fully integrated
            c1, c2 = st.columns(2)
            with c1: tx_type = st.selectbox("TYPE", ["Expense", "Income", "Apartado", "Defense"])
            with c2: amount = st.number_input("AMOUNT", min_value=0.01, step=10.0)
            
            submitted = st.form_submit_button("[ EXECUTE_TRANSACTION ]")
            if submitted:
                # Basic execution simulation
                try:
                    payload = {"amount": amount, "type": tx_type, "description": cmd_text, "category_id": None}
                    res = requests.post(f"{BACKEND_URL}/transactions", json=payload)
                    st.success("> TX_SENT")
                except:
                    st.error("> SYSTEM_ERROR")
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        # Proyección a 14 días (Tabla o lista)
        st.markdown(f"<div class='matrix-card'>", unsafe_allow_html=True)
        st.markdown("<h4 class='glow'>> PROJECTION[14_DAYS]</h4>", unsafe_allow_html=True)
        st.markdown("<span class='muted-text'>Simulación de Daily Power si Gasto = $0</span><hr>", unsafe_allow_html=True)
        
        projections = data.get("projections", [])
        if not projections:
            # Dummy data si el backend está caído/vacío
            projections = [daily_power + (i * 12.5) for i in range(14)]
            
        for i in range(0, 14, 2):
            if i+1 < len(projections):
                d1 = f"D+{i}: ${projections[i]:.0f}"
                d2 = f"D+{i+1}: ${projections[i+1]:.0f}"
                st.markdown(f"<div style='display: flex; justify-content: space-between;'><span class='muted-text'>{d1}</span><span style='color: #00FF41;'>{d2}</span></div>", unsafe_allow_html=True)
                
        st.markdown("</div>", unsafe_allow_html=True)

else:
    st.markdown(f"<h3 class='glow'>[ {selection.split('] ')[1]} MODULE_OFFLINE ]</h3>", unsafe_allow_html=True)
    st.markdown("<span class='muted-text'>> AWAITING_IMPLEMENTATION...</span>", unsafe_allow_html=True)
