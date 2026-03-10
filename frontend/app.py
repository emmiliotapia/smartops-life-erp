import streamlit as st
import requests
import os
import datetime

# Configuration
st.set_page_config(page_title="SmartOps VIVID", layout="wide", initial_sidebar_state="collapsed")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def load_css(file_name):
    try:
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    except FileNotFoundError:
        pass

load_css("style.css")

# --- System Scan Line ---
st.markdown('<div class="scan-line"></div>', unsafe_allow_html=True)

# --- 2. Elementos de Identidad Visual ---
# System Status Bar
st.markdown("""
<div class="text-muted fade-in-up" style="font-size: 0.8rem; margin-bottom: 20px; display: flex; justify-content: space-between; animation-duration: 0.5s;">
    <span>[ STATUS: OPERATIONAL ]</span>
    <span>[ LOC: MXLI_BC ]</span>
    <span>[ ENGINE: TAPIA-CORE_V1 ]</span>
</div>
""", unsafe_allow_html=True)

# Typewriter Title
st.markdown("""
<div style="margin-bottom: 30px;">
    <div class="typewriter-title">> SYSTEM_LOG: BOOTING_SUCCESSFUL...</div>
</div>
""", unsafe_allow_html=True)

# Load dashboard data
try:
    response = requests.get(f"{BACKEND_URL}/dashboard")
    dashboard_data = response.json()
except Exception as e:
    dashboard_data = {"daily_power": 0.0, "penalty_days": 0, "debt_bosses": []}

daily_power = dashboard_data.get('daily_power', 0.0)

# Layout 3 columns Setup
col1, col2, col3 = st.columns([1,1.5,1])

# --- 1. Columna Izquierda (Status) ---
with col1:
    current_time = datetime.datetime.now().strftime("%H:%M:%S UTC")
    st.markdown(f"""
    <div class="terminal-card fade-in-up" style="animation-delay: 0.2s;">
        <h3 class="glow-text">[01] SYSTEM_STATUS</h3>
        <div style="margin-bottom: 20px;">
            > USER: <span class='glow-text'>EMMILIO_ARCHITECT</span><br>
            > TIME: <span class='text-muted'>{current_time}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pulse container for Metric
    pulse_class = "pulse-neon"
    penalty_days = dashboard_data.get('penalty_days', 0)
    # If penalty, pulse Magenta
    if penalty_days > 0 or daily_power < 0:
        pulse_class = "pulse-magenta"
        
    st.markdown(f"""
    <div class="terminal-card fade-in-up {pulse_class}" style="animation-delay: 0.4s;">
        <h3 class="glow-text" style="{'color:#FF007A;' if pulse_class=='pulse-magenta' else ''}">[02] DAILY_POWER</h3>
    """, unsafe_allow_html=True)
    
    # ASCII Progress Bar Model
    percentage = min(int((daily_power / 500) * 100), 100) if daily_power > 0 else 0
    filled = int(percentage / 5)
    bar_str = ("█" * filled) + ("░" * (20 - filled))
    
    color_style = "color:#FF007A; text-shadow: 0 0 5px #FF007A;" if daily_power < 0 else "color:var(--green-accent);"
    st.markdown(f"> CURRENT_BALANCE: <span style='{color_style} font-weight: bold;'>${daily_power:.2f} MXN</span>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-top: 10px;'>[ {bar_str} ] {percentage}%</div>", unsafe_allow_html=True)
    
    if penalty_days > 0:
        st.markdown(f"<div style='color:#FF007A; margin-top: 15px; font-weight: bold;'>> CRITICAL: PENALTY_MODE [{penalty_days:.1f} DAYS]</div>", unsafe_allow_html=True)
        
    if st.button("> EXEC RESET_MONGODAY()"):
        try:
            res = requests.post(f"{BACKEND_URL}/reset_monday")
            if res.status_code == 200:
                st.success("> OK")
                st.rerun()
        except:
            pass
            
    st.markdown("</div>", unsafe_allow_html=True)

# --- 2. Columna Central (Focus) ---
with col2:
    st.markdown("""
    <div class="terminal-card fade-in-up" style="animation-delay: 0.6s;">
        <h3 class="glow-text">[03] WEEK_FOCUS</h3>
        <p>> OUTFLOW_ANALYSIS:<br>
          <span class="text-muted">MON:</span> █░░░░░░░░░ [10%]<br>
          <span class="text-muted">TUE:</span> ████░░░░░░ [40%]<br>
          <span class="text-muted">WED:</span> █░░░░░░░░░ [10%]<br>
          <span class="text-muted">THU:</span> ██████░░░░ [60%]<br>
          <span class="text-muted">FRI:</span> ░░░░░░░░░░ [ 0%]<br>
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    <div class="terminal-card fade-in-up" style="animation-delay: 0.8s;">
        <h3 class="glow-text">[04] QUICK_LOG</h3>
    """, unsafe_allow_html=True)
    
    with st.form("transaction_form"):
        tx_type = st.selectbox("TYPE", ["Expense", "Income", "Apartado", "Defense"])
        amount = st.number_input("AMOUNT", min_value=0.01, step=10.0)
        desc = st.text_input("DESC", placeholder="[ WAITING FOR INPUT... ]")
        
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

# --- 3. Columna Derecha (Raid) ---
with col3:
    st.markdown("""
    <div class="terminal-card fade-in-up" style="animation-delay: 1.0s;">
        <h3 class="glow-text">[05] ACTIVE_RAIDS (DEBT_BOSSES)</h3>
    """, unsafe_allow_html=True)
    
    debt_bosses = dashboard_data.get("debt_bosses", [])
    if not debt_bosses:
        st.markdown("> NO_ACTIVE_THREATS")
    else:
        for boss in debt_bosses:
            st.markdown(f"> BOSS_ENGAGED: <span style='color: #FF007A;'>{boss['name']}</span>", unsafe_allow_html=True)
            st.markdown(f"<span class='text-muted'>$ {boss['total_hp']:.2f} REMAINING</span>", unsafe_allow_html=True)
            
            hp_percent = 50 
            filled_hp = 12
            bar_hp = ("|" * filled_hp) + ("░" * (20 - filled_hp))
            st.markdown(f"<div style='margin-bottom: 20px; color:#FF007A; text-shadow: 0 0 5px #FF007A;'>HP: [{bar_hp}]</div>", unsafe_allow_html=True)
            
    st.markdown('</div>', unsafe_allow_html=True)

# --- Recent Log Section ---
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("<h3 class='glow-text fade-in-up' style='animation-delay: 1.2s;'>[06] SYSTEM_LOG</h3>", unsafe_allow_html=True)

try:
    tx_list = requests.get(f"{BACKEND_URL}/transactions?limit=10").json()
    if tx_list:
        delay = 1.3
        for tx in tx_list:
            sign = "+" if tx['type'] == "Income" else "-"
            st.markdown(f"<div class='text-muted fade-in-up' style='animation-delay: {delay}s;'>[{tx['timestamp'][:10]}] <span style='color: var(--green-accent);'>[ {sign} ] ${tx['amount']:.2f}</span> | {tx['type'].upper()} | {tx.get('description', '')}</div>", unsafe_allow_html=True)
            delay += 0.1
    else:
        st.markdown("> LOG_EMPTY")
except:
    pass

st.sidebar.markdown("<h3 class='glow-text'>[ CONFIG ]</h3>", unsafe_allow_html=True)
with st.sidebar.expander("> NEW_BUCKET"):
    with st.form("new_bucket_form"):
        b_name = st.text_input("B_NAME", placeholder="[ WAITING FOR INPUT... ]")
        b_target = st.number_input("B_TARGET", min_value=0.0)
        if st.form_submit_button("> INIT"):
            requests.post(f"{BACKEND_URL}/buckets", json={"name": b_name, "target_balance": b_target})
            st.rerun()
