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

# --- Static Header ---
# We retrieve state for the header if possible
try:
    response = requests.get(f"{BACKEND_URL}/dashboard")
    dashboard_data = response.json()
except Exception as e:
    dashboard_data = {"daily_power": 0.0, "penalty_days": 0, "debt_bosses": [], "state": "MODO_GUERRA", "projections": []}

current_state = dashboard_data.get('state', 'MODO_GUERRA')
daily_power = dashboard_data.get('daily_power', 0.0)

st.markdown(f"""
<div class="text-muted fade-in-up" style="font-size: 0.8rem; margin-bottom: 20px; display: flex; justify-content: space-between; animation-duration: 0.5s; border-bottom: 1px solid var(--glass-border); padding-bottom: 5px;">
    <span>[ STATUS: ONLINE ]</span>
    <span style="color: var(--green-accent);">[ STATE: {current_state} ]</span>
    <span>[ LEVEL: 20K_GOAL ]</span>
    <span>[ RUNWAY: CALC_PENDING ]</span>
</div>
""", unsafe_allow_html=True)

# --- Sidebar Navigation ---
st.sidebar.markdown("<h3 class='glow-text'>[ SYSTEM_NAV ]</h3>", unsafe_allow_html=True)
pages = ["[01] TERMINAL", "[02] DASHBOARD", "[03] CRM_OPS", "[04] VAULTS", "[05] BOSS_RAID"]
selection = st.sidebar.radio("Go to", pages, label_visibility="collapsed")

if selection == "[01] TERMINAL":
    # Typewriter Title
    st.markdown("""
    <div style="margin-bottom: 30px;">
        <div class="typewriter-title">> SYSTEM_LOG: TERMINAL_ACTIVE...</div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("""
        <div class="terminal-card fade-in-up" style="animation-delay: 0.2s;">
            <h3 class="glow-text">[ INPUT_CMD ]</h3>
        """, unsafe_allow_html=True)
        
        with st.form("quick_cmd_form"):
            st.markdown("> EXECUTE TRANSACTION")
            tx_type = st.selectbox("TYPE", ["Expense", "Income", "Apartado", "Defense"])
            amount = st.number_input("AMOUNT", min_value=0.01, step=1.0)
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
                    category_options[f"VAULT: {b['name']}"] = b['id']
            elif tx_type == "Defense":
                for d in debts_res:
                    category_options[f"TARGET: {d['name']}"] = d['id']
                    
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
                        st.success("> TX_ACCEPTED")
                        st.rerun()
                    else:
                        st.error(f"> ERR: {res.json().get('detail', 'Unknown')}")
                except Exception as e:
                    st.error(f"> SYSERR: {e}")
        st.markdown("</div>", unsafe_allow_html=True)
        
        if st.button("> EXEC RESET_MONDAY()"):
            try:
                res = requests.post(f"{BACKEND_URL}/reset_monday")
                if res.status_code == 200:
                    st.success("> CYCLE_RESET_OK")
                    st.rerun()
            except:
                pass

    with col2:
        st.markdown(f"""
        <div class="terminal-card fade-in-up pulse-neon" style="animation-delay: 0.4s;">
            <h3 class="glow-text">[ DAILY_POWER_PROJECTION ]</h3>
            <p>> 14_DAY_FORECAST_INITIATED...</p>
        """, unsafe_allow_html=True)
        
        projections = dashboard_data.get('projections', [])
        if projections:
            st.markdown("<div style='display: grid; grid-template-columns: repeat(7, 1fr); gap: 10px; margin-top: 20px;'>", unsafe_allow_html=True)
            for i, val in enumerate(projections):
                day_label = f"D+{i}" if i > 0 else "TODAY"
                st.markdown(f"""
                <div style='border: 1px solid var(--glass-border); padding: 10px; text-align: center; background: rgba(0, 255, 65, 0.05);'>
                    <div class='text-muted' style='font-size: 0.8rem;'>{day_label}</div>
                    <div style='color: var(--green-accent); font-weight: bold; margin-top: 5px;'>${val:.0f}</div>
                </div>
                """, unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
        else:
            st.markdown("> [ DATA_STREAM_OFFLINE ]")
            
        st.markdown("</div>", unsafe_allow_html=True)

elif selection == "[02] DASHBOARD":
    st.markdown("### > UNDER_CONSTRUCTION. BRINGING LEGACY COMPONENTS HERE...")

# Layout 3 columns Setup
col1, col2, col3 = st.columns([1,1.5,1])

    current_time = datetime.datetime.now().strftime("%H:%M:%S UTC")
    
    col1, col2, col3 = st.columns([1,1.5,1])
    
    with col1:
        st.markdown(f"""
        <div class="terminal-card fade-in-up" style="animation-delay: 0.2s;">
            <h3 class="glow-text">[ SYSTEM_STATUS ]</h3>
            <div style="margin-bottom: 20px;">
                > USER: <span class='glow-text'>EMMILIO_ARCHITECT</span><br>
                > TIME: <span class='text-muted'>{current_time}</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        pulse_class = "pulse-neon"
        penalty_days = dashboard_data.get('penalty_days', 0)
        if penalty_days > 0 or daily_power < 0:
            pulse_class = "pulse-magenta"
            
        st.markdown(f"""
        <div class="terminal-card fade-in-up {pulse_class}" style="animation-delay: 0.4s;">
            <h3 class="glow-text" style="{'color:#FF007A;' if pulse_class=='pulse-magenta' else ''}">[ DAILY_POWER ]</h3>
        """, unsafe_allow_html=True)
        
        percentage = min(int((daily_power / 500) * 100), 100) if daily_power > 0 else 0
        filled = int(percentage / 5)
        bar_str = ("█" * filled) + ("░" * (20 - filled))
        
        color_style = "color:#FF007A; text-shadow: 0 0 5px #FF007A;" if daily_power < 0 else "color:var(--green-accent);"
        st.markdown(f"> CURRENT_BALANCE: <span style='{color_style} font-weight: bold;'>${daily_power:.2f} MXN</span>", unsafe_allow_html=True)
        st.markdown(f"<div style='margin-top: 10px;'>[ {bar_str} ] {percentage}%</div>", unsafe_allow_html=True)
        
        if penalty_days > 0:
            st.markdown(f"<div style='color:#FF007A; margin-top: 15px; font-weight: bold;'>> CRITICAL: PENALTY_MODE [{penalty_days:.1f} DAYS]</div>", unsafe_allow_html=True)
                
        st.markdown("</div>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="terminal-card fade-in-up" style="animation-delay: 0.6s;">
            <h3 class="glow-text">[ WEEK_FOCUS ]</h3>
            <p>> OUTFLOW_ANALYSIS:<br>
              <span class="text-muted">MON:</span> █░░░░░░░░░ [10%]<br>
              <span class="text-muted">TUE:</span> ████░░░░░░ [40%]<br>
              <span class="text-muted">WED:</span> █░░░░░░░░░ [10%]<br>
              <span class="text-muted">THU:</span> ██████░░░░ [60%]<br>
              <span class="text-muted">FRI:</span> ░░░░░░░░░░ [ 0%]<br>
            </p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="terminal-card fade-in-up" style="animation-delay: 1.0s;">
            <h3 class="glow-text">[ ACTIVE_RAIDS ]</h3>
        """, unsafe_allow_html=True)
        
        debt_bosses = dashboard_data.get("debt_bosses", [])
        if not debt_bosses:
            st.markdown("> NO_ACTIVE_THREATS")
        else:
            for boss in debt_bosses:
                st.markdown(f"> BOSS_ENGAGED: <span style='color: #FF007A;'>{boss['name']}</span>", unsafe_allow_html=True)
                st.markdown(f"<span class='text-muted'>$ {boss['total_hp']:.2f} REMAINING</span>", unsafe_allow_html=True)
                
                filled_hp = 12
                bar_hp = ("|" * filled_hp) + ("░" * (20 - filled_hp))
                st.markdown(f"<div style='margin-bottom: 20px; color:#FF007A; text-shadow: 0 0 5px #FF007A;'>HP: [{bar_hp}]</div>", unsafe_allow_html=True)
                
        st.markdown('</div>', unsafe_allow_html=True)
        
    # --- Recent Log Section ---
    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown("<h3 class='glow-text fade-in-up' style='animation-delay: 1.2s;'>[ SYSTEM_LOG ]</h3>", unsafe_allow_html=True)
    
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

else:
    st.markdown(f"### > MODULE {selection} UNAVAILABLE.")

