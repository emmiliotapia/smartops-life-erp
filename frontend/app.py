import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

# Fetch Data
try:
    response = requests.get(f"{BACKEND_URL}/dashboard")
    data = response.json()
except:
    data = {"daily_power": 0.0, "penalty_days": 0, "debt_bosses": [], "state": "MODO_GUERRA", "projections": []}

daily_power = data.get("daily_power", 0.0)
penalty_days = data.get("penalty_days", 0)

# Determine global mode colors
primary_color = "#FF007A" if penalty_days > 0 or daily_power < 0 else "#00FF41"
border_color = f"{primary_color}33" # with transparency

# 1. FORZAR LAYOUT ANCHO Y TEMA OSCURO
st.set_page_config(page_title="SMART-OPS OS", layout="wide", initial_sidebar_state="expanded")

# 2. INYECCIÓN DE CSS PARA SIDEBAR Y HUD (ESTILO MATRIX)
st.markdown(f"""
    <style>
    /* Fondo negro total */
    [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {{
        background-color: #000000 !important;
        border-right: 1px solid {border_color};
    }}
    /* Texto Verde Mono (o Magenta si hay penalización) */
    * {{
        color: {primary_color} !important;
        font-family: 'JetBrains Mono', monospace !important;
    }}
    /* Input backgrounds */
    input, select, .stTextInput > div > div > input, .stNumberInput > div > div > input, .stSelectbox > div > div {{
        background-color: #000000 !important;
        color: {primary_color} !important;
        border: 1px solid {primary_color} !important;
        border-radius: 0px !important;
    }}
    /* Contenedores de inputs */
    [data-baseweb="select"] > div {{
        background-color: #000000 !important;
        border-radius: 0px !important;
        border-color: {primary_color} !important;
    }}
    /* Estilo de los items del Menú Lateral */
    .stRadio > div {{
        gap: 10px;
    }}
    button[kind="secondary"] {{
        border: 1px solid {primary_color} !important;
        background: transparent !important;
        border-radius: 0px !important;
        transition: 0.2s all;
    }}
    button[kind="secondary"]:hover {{
        background: {primary_color} !important;
        color: #000000 !important;
    }}
    button[kind="primary"] {{
        border: 1px solid {primary_color} !important;
        background: transparent !important;
        border-radius: 0px !important;
    }}
    /* Ocultar basurilla de Streamlit */
    [data-testid="stHeader"], footer, .stDeployButton {{display: none !important;}}
    </style>
    """, unsafe_allow_html=True)

# 3. SIDEBAR DE NAVEGACIÓN (OBLIGATORIO)
with st.sidebar:
    st.markdown("### 🛸 SYSTEM_NAV")
    st.markdown("---")
    menu = st.radio(
        "SELECT_MODULE:",
        ["[01] TERMINAL", "[02] DASHBOARD", "[03] CRM_OPS", "[04] VAULTS", "[05] BOSS_RAID"],
        index=0,
        label_visibility="collapsed"
    )
    st.markdown("---")
    status_label = "ONLINE" if penalty_days == 0 else "PENALTY_MODE"
    st.markdown(f"`STATUS: {status_label}`\n\n`USER: EMMILIO_ARCH`\n\n`LOC: MXLI_BC`")

# 4. LÓGICA DE MÓDULOS
if menu == "[01] TERMINAL":
    st.markdown("# > TERMINAL_CENTRAL")
    col1, col2, col3 = st.columns(3)
    
    # Calculate mock values for runway and buff
    next_week_buff = 0.0 # Could load from DB later
    runway = "CALC_PENDING"
    
    with col1:
        st.metric("DAILY_POWER", f"${daily_power:.2f}", "-PENALTY" if penalty_days > 0 else "")
    with col2:
        st.metric("NEXT_WEEK_BUFF", f"${next_week_buff:.2f}")
    with col3:
        st.metric("RUNWAY", runway)
    
    st.markdown("---")
    
    col_cmd, col_proj = st.columns([1, 1.5])
    
    with col_cmd:
        st.markdown("### [ COMMAND_INPUT ]")
        with st.form("transaction_form"):
            st.markdown("> AGREGAR_MOVIMIENTO:")
            tx_type = st.selectbox("TYPE", ["Expense", "Income", "Apartado", "Defense"])
            amount = st.number_input("AMOUNT", min_value=0.01, step=10.0)
            desc = st.text_input("DESC", placeholder="Concepto...")
            
            try:
                buckets_res = requests.get(f"{BACKEND_URL}/buckets").json()
                debts_res = data.get("debt_bosses", [])
            except:
                buckets_res = []
                debts_res = []
                
            category_options = {"None": None}
            if tx_type == "Apartado":
                for b in buckets_res:
                    category_options[f"VAULT: {b['name']}"] = b['id']
            elif tx_type == "Defense":
                for d in debts_res:
                    category_options[f"TARGET: {d['name']}"] = d['id']
                    
            category = st.selectbox("TARGET_NODE", options=list(category_options.keys()))
            
            submitted = st.form_submit_button("> EXECUTE_TX")
            if submitted:
                cat_id = category_options[category]
                payload = {
                    "amount": amount,
                    "type": tx_type,
                    "description": desc,
                    "category_id": cat_id
                }
                try:
                    res = requests.post(f"{BACKEND_URL}/transactions", json=payload)
                    if res.status_code == 200:
                        st.success("> TX_ACCEPTED")
                    else:
                        st.error(f"> ERR: {res.json().get('detail', 'Unknown')}")
                except Exception as e:
                    st.error(f"> SYSERR: {e}")
                    
        if st.button("> EXEC RESET_MONDAY()"):
            try:
                res = requests.post(f"{BACKEND_URL}/reset_monday")
                if res.status_code == 200:
                    st.success("> CYCLE_RESET_OK")
            except:
                pass


    with col_proj:
        st.markdown("### [ FUTURE_SIGHT_PROJECTION ]")
        projections = data.get("projections", [])
        if not projections:
            # Dummy data if no connection or no logic yet
            projections = [daily_power + (i * 10) for i in range(14)]
            
        st.markdown("<div style='display: grid; grid-template-columns: repeat(4, 1fr); gap: 10px;'>", unsafe_allow_html=True)
        for i, val in enumerate(projections):
            day_label = f"D+{i}" if i > 0 else "TODAY"
            st.markdown(f"""
            <div style='border: 1px solid {primary_color}; padding: 10px; text-align: center; background: #000000;'>
                <div style='font-size: 0.8rem; opacity: 0.8;'>{day_label}</div>
                <div style='font-weight: bold;'>${val:.0f}</div>
            </div>
            """, unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)

elif menu == "[03] CRM_OPS":
    st.markdown("# > OPERATIONS_PIPELINE")
    st.write("> UNDER_CONSTRUCTION")
else:
    section_name = menu.split('] ')[1] if '] ' in menu else menu
    st.markdown(f"# > {section_name}_MODULE")
    st.write("> UNDER_CONSTRUCTION. AWAITING DATA STREAM.")
