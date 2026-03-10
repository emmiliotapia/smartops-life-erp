import streamlit as st
import requests
import os

# Configuration
st.set_page_config(page_title="SmartOps Terminal UI", layout="wide", initial_sidebar_state="collapsed")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("style.css")

# --- 2. Elementos de Identidad Visual ---
# System Status Bar
st.markdown("""
<div class="text-muted" style="font-size: 0.8rem; margin-bottom: 20px; display: flex; justify-content: space-between;">
    <span>[ STATUS: OPERATIONAL ]</span>
    <span>[ LOC: MXLI_BC ]</span>
    <span>[ ENGINE: TAPIA-CORE_V1 ]</span>
</div>
""", unsafe_allow_html=True)

# Ejemplo de Estructura de Texto: Terminal Boot
st.markdown("""
<div style="margin-bottom: 30px;">
    > SYSTEM_LOG: BOOTING_SUCCESSFUL...<br>
    > USER: EMMILIO_ARCHITECT
</div>
""", unsafe_allow_html=True)

# Load dashboard data
try:
    response = requests.get(f"{BACKEND_URL}/dashboard")
    dashboard_data = response.json()
except Exception as e:
    dashboard_data = {"daily_power": 0.0, "penalty_days": 0, "debt_bosses": []}

daily_power = dashboard_data.get('daily_power', 0.0)

col1, col2, col3 = st.columns(3)

# 1. Daily Power (Text Gauge)
with col1:
    st.markdown("""
    <div class="terminal-card">
        <h3 class="glow-text">[01] DAILY_POWER</h3>
    """, unsafe_allow_html=True)
    
    st.markdown(f"> CURRENT_BALANCE: <span class='glow-text'>${daily_power:.2f} MXN</span>", unsafe_allow_html=True)
    
    # ASCII Progress Bar replacing graphical ones (3. Refactorización de Widgets)
    # Assuming $500 is 100% just for visualization
    percentage = min(int((daily_power / 500) * 100), 100) if daily_power > 0 else 0
    filled = int(percentage / 5)
    bar_str = ("█" * filled) + ("░" * (20 - filled))
    
    st.markdown(f"<div style='margin-top: 10px;'>[ {bar_str} ] {percentage}%</div>", unsafe_allow_html=True)
    
    penalty_days = dashboard_data.get('penalty_days', 0)
    if penalty_days > 0:
        st.markdown(f"<div style='color:#FF0000; margin-top: 15px;'>> WARN: PENALTY_MODE [{penalty_days:.1f} DAYS]</div>", unsafe_allow_html=True)
        
    if st.button("> EXEC RESET_MONGODAY()"):
        try:
            res = requests.post(f"{BACKEND_URL}/reset_monday")
            if res.status_code == 200:
                st.success("> OK")
                st.rerun()
        except:
            pass
            
    st.markdown("</div>", unsafe_allow_html=True)
    
# 2. Add Transaction Form
with col2:
    st.markdown("""
    <div class="terminal-card">
        <h3 class="glow-text">[02] TX_CMD</h3>
    """, unsafe_allow_html=True)
    st.markdown("> INPUT NEW TRANSACTION DATA")
    
    with st.form("transaction_form"):
        tx_type = st.selectbox("TYPE", ["Expense", "Income", "Apartado", "Defense"])
        amount = st.number_input("AMOUNT", min_value=0.01, step=10.0)
        desc = st.text_input("DESC")
        
        try:
            buckets_res = requests.get(f"{BACKEND_URL}/buckets").json()
            debts_res = dashboard_data.get("debt_bosses", [])
        except:
            buckets_res = []
            debts_res = []
            
        category_options = {"None": None}
        if tx_type == "Apartado":
            for b in buckets_res:
                category_options[f"BUCKET_TARGET: {b['name']}"] = b['id']
        elif tx_type == "Defense":
            for d in debts_res:
                category_options[f"THREAT_TARGET: {d['name']}"] = d['id']
                
        category = st.selectbox("TARGET_NODE", options=list(category_options.keys()))
        
        submitted = st.form_submit_button("> EXECUTE")
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
                    st.success("> TX SENT")
                    st.rerun()
            except:
                pass
    st.markdown('</div>', unsafe_allow_html=True)

# 3. Debt Bosses (ASCII HP Bars)
with col3:
    st.markdown("""
    <div class="terminal-card">
        <h3 class="glow-text">[03] DEBT_BOSSES</h3>
    """, unsafe_allow_html=True)
    
    debt_bosses = dashboard_data.get("debt_bosses", [])
    if not debt_bosses:
        st.markdown("> NO_ACTIVE_THREATS")
    else:
        for boss in debt_bosses:
            st.markdown(f"> TARGET: {boss['name']}", unsafe_allow_html=True)
            st.markdown(f"<span class='text-muted'>$ {boss['total_hp']:.2f}</span>", unsafe_allow_html=True)
            
            # HP Bar implementation: |||||||||||||░░░░
            # Assuming max HP is initial_hp if it existed, for now just rendering based on a fictional 10k max scale for demo
            hp_percent = 50 # Default 50% for visual since DB doesn't have max_hp stored easily right now unless computed
            filled_hp = 12
            bar_hp = ("|" * filled_hp) + ("░" * (20 - filled_hp))
            st.markdown(f"<div style='margin-bottom: 15px;'>HP: [{bar_hp}]</div>", unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- Recent Log Section ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 class='glow-text'>[04] SYSTEM_LOG</h3>", unsafe_allow_html=True)

try:
    tx_list = requests.get(f"{BACKEND_URL}/transactions?limit=10").json()
    if tx_list:
        for tx in tx_list:
            sign = "+" if tx['type'] == "Income" else "-"
            st.markdown(f"<div class='text-muted'>[{tx['timestamp'][:10]}] <span style='color: var(--green-accent);'>[ {sign} ] ${tx['amount']:.2f}</span> | {tx['type'].upper()} | {tx.get('description', '')}</div>", unsafe_allow_html=True)
    else:
        st.markdown("> LOG_EMPTY")
except:
    pass

st.sidebar.markdown("<h3 class='glow-text'>[ CONFIG ]</h3>", unsafe_allow_html=True)
with st.sidebar.expander("> NEW_BUCKET"):
    with st.form("new_bucket_form"):
        b_name = st.text_input("B_NAME")
        b_target = st.number_input("B_TARGET", min_value=0.0)
        if st.form_submit_button("> INIT"):
            requests.post(f"{BACKEND_URL}/buckets", json={"name": b_name, "target_balance": b_target})
            st.rerun()
