import streamlit as st
import requests
import os

# Configuration
st.set_page_config(page_title="SmartOpsIA", layout="wide", initial_sidebar_state="collapsed")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("style.css")

# --- Top Header Status Bar ---
st.markdown("""
<div class="status-bar">
    <span>SYSTEM: ONLINE</span>
    <span>LATENCY: 12ms</span>
    <span>LOC: MXLI_BC</span>
</div>
<div class="status-divider"></div>
""", unsafe_allow_html=True)

# --- Title Header ---
st.markdown("""
<div class="main-title">
    SmartOps<span class="title-ia">IA</span>
</div>
<div class="subtitle">
    > Automatizando lo aburrido para que tú factures.<span class="cursor-blink"></span>
</div>
""", unsafe_allow_html=True)

# Load dashboard data
try:
    response = requests.get(f"{BACKEND_URL}/dashboard")
    dashboard_data = response.json()
except Exception as e:
    dashboard_data = {"daily_power": 0.0, "penalty_days": 0, "debt_bosses": []}

col1, col2, col3 = st.columns(3)

# 1. Energia y Penalizaciones (Daily Power widget revamped)
with col1:
    st.markdown("""
    <div class="terminal-card">
        <div class="terminal-card-title">[01] Energía & Penalizaciones</div>
        <div class="terminal-card-text">
            Monitor de estado vital del sistema y de los días penalizados por inactividad.
            <br><br>
    """, unsafe_allow_html=True)
    
    st.metric(label="> Nivel_Energia", value=f"${dashboard_data.get('daily_power', 0.0):.2f}")
    
    penalty_days = dashboard_data.get('penalty_days', 0)
    if penalty_days > 0:
        st.markdown(f"<p style='color: #FF003C; font-weight: bold; margin-top: 15px;'>> WARN: PENALTY_MODE_ACTIVE ({penalty_days:.1f} DAYS)</p>", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("> Initialize_Reset()"):
        try:
            res = requests.post(f"{BACKEND_URL}/reset_monday")
            if res.status_code == 200:
                st.success("> Protocolo Reset Activado.")
                st.rerun()
        except:
            st.error("> ERROR: Engine failure.")
            
    st.markdown("</div></div>", unsafe_allow_html=True)
    
# 2. Add Transaction Form (Terminal Style)
with col2:
    st.markdown("""
    <div class="terminal-card">
        <div class="terminal-card-title">[02] Transacciones Manuales</div>
        <div class="terminal-card-text">
            Ingreso y registro de anomalías financieras, buckets y daño a deudas.
        </div>
        <br>
    """, unsafe_allow_html=True)
    with st.form("transaction_form"):
        tx_type = st.selectbox("Type", ["Expense", "Income", "Apartado", "Defense"])
        amount = st.number_input("Amount", min_value=0.01, step=10.0)
        desc = st.text_input("Description")
        
        # Load buckets/debts for categories
        try:
            buckets_res = requests.get(f"{BACKEND_URL}/buckets").json()
            debts_res = dashboard_data.get("debt_bosses", [])
        except:
            buckets_res = []
            debts_res = []
            
        category_options = {"None": None}
        if tx_type == "Apartado":
            for b in buckets_res:
                category_options[f"Bucket: {b['name']}"] = b['id']
        elif tx_type == "Defense":
            for d in debts_res:
                category_options[f"Debt: {d['name']}"] = d['id']
                
        category = st.selectbox("Entity_Target", options=list(category_options.keys()))
        
        submitted = st.form_submit_button("> Ejecutar_Transaccion()")
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
                    st.rerun()
                else:
                    st.error(f"> ERR: {res.text}")
            except Exception as e:
                st.error(f"> ERR_NET: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# 3. Debt Bosses
with col3:
    st.markdown("""
    <div class="terminal-card">
        <div class="terminal-card-title">[03] Debt Bosses (Threats)</div>
        <div class="terminal-card-text">
            Sistemas hostiles activos con deuda pendiente. Proceder con precaución.
            <br><br>
    """, unsafe_allow_html=True)
    
    debt_bosses = dashboard_data.get("debt_bosses", [])
    if not debt_bosses:
        st.markdown("> STATUS: CLEAR [No active threats present]", unsafe_allow_html=True)
    else:
        for boss in debt_bosses:
            st.markdown(f"<div style='color: #FFFFFF;'><b>> TARGET: {boss['name']}</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='color: #888888; font-size: 0.9rem; margin-bottom: 5px;'>  HP_REMAINING: <b>${boss['total_hp']:.2f}</b></div>", unsafe_allow_html=True)
            # Text based progress bar
            st.progress(100 if boss['total_hp'] > 0 else 0) 
            st.markdown("<br>", unsafe_allow_html=True)
            
    st.markdown('</div></div>', unsafe_allow_html=True)

# --- Recent Log Section ---
st.markdown("---")
st.markdown("<div style='color: var(--green-accent); font-family: \"JetBrains Mono\", monospace;'> > LOG_DE_TRANSACCIONES_RECIENTES </div><br>", unsafe_allow_html=True)

try:
    tx_list = requests.get(f"{BACKEND_URL}/transactions?limit=10").json()
    if tx_list:
        for tx in tx_list:
            amount_color = "#00FF41" if tx['type'] == "Income" else "#FF003C"
            st.markdown(f"<span style='color: #555555;'>[{tx['timestamp'][:10]}]</span> <span style='color: {amount_color};'>[{tx['type'].upper():<9}]</span> | <b>${tx['amount']:.2f}</b> | <span style='color: #888888;'>{tx.get('description', '')}</span>", unsafe_allow_html=True)
            st.markdown("<hr style='margin: 5px 0; border-color: #222;'>", unsafe_allow_html=True)
    else:
        st.markdown("> [LOG_EMPTY]", unsafe_allow_html=True)
except:
    st.markdown("> [LOG_UNAVAILABLE_OR_OFFLINE]", unsafe_allow_html=True)

# Admin Sidebar (Collapsed by default, styled minimally)
st.sidebar.markdown("<div style='color: var(--green-accent); font-family: \"JetBrains Mono\", monospace; font-size: 1.2rem; font-weight: bold;'>SYS_CONFIG</div><br>", unsafe_allow_html=True)
with st.sidebar.expander(">> CREATE_BUCKET()"):
    with st.form("new_bucket_form"):
        b_name = st.text_input("VAR bucket_name")
        b_target = st.number_input("VAR target_balance", min_value=0.0)
        if st.form_submit_button("> COMMIT"):
            requests.post(f"{BACKEND_URL}/buckets", json={"name": b_name, "target_balance": b_target})
            st.rerun()
