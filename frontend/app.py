import streamlit as st
import requests
import os

# Configuration
st.set_page_config(page_title="SmartOps Life ERP", layout="wide", initial_sidebar_state="expanded")

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")

def load_css(file_name):
    with open(file_name) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

try:
    load_css("style.css")
except FileNotFoundError:
    pass

st.title("SmartOps Life ERP ⚡")

# Load dashboard data
try:
    response = requests.get(f"{BACKEND_URL}/dashboard")
    dashboard_data = response.json()
except Exception as e:
    st.error(f"Cannot connect to the backend: {e}")
    dashboard_data = {"daily_power": 0.0, "penalty_days": 0, "debt_bosses": []}

col1, col2, col3 = st.columns([1, 1.5, 1])

# 1. Daily Power Widget
with col1:
    st.markdown('<div class="neon-cyan" style="padding: 20px; border-radius: 12px; text-align: center;">', unsafe_allow_html=True)
    st.metric(label="Daily Power ⚡", value=f"${dashboard_data.get('daily_power', 0.0):.2f}")
    
    penalty_days = dashboard_data.get('penalty_days', 0)
    if penalty_days > 0:
        st.markdown(f"<p style='color: var(--magenta); font-weight: bold; margin-top: 10px;'>🚨 PENALTY MODE: {penalty_days:.1f} Days</p>", unsafe_allow_html=True)
        
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("Trigger Monday Reset 🔄"):
        try:
            res = requests.post(f"{BACKEND_URL}/reset_monday")
            if res.status_code == 200:
                st.success("Monday Reset Protocol Activated!")
                st.rerun()
        except:
            st.error("Engine failure on reset.")
    
# 2. Add Transaction Form
with col2:
    st.markdown('<div class="neon-cyan" style="padding: 2px; border-radius: 12px; margin-bottom: 20px;">', unsafe_allow_html=True)
    st.markdown("### Log Transaction")
    with st.form("transaction_form"):
        tx_type = st.selectbox("Type", ["Expense", "Income", "Apartado", "Defense"])
        amount = st.number_input("Amount", min_value=0.01, step=10.0)
        desc = st.text_input("Description")
        
        # Load buckets/debts for categories
        try:
            buckets_res = requests.get(f"{BACKEND_URL}/buckets").json()
            debts_res = requests.get(f"{BACKEND_URL}/dashboard").json().get("debt_bosses", [])
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
                
        category = st.selectbox("Category Entity", options=list(category_options.keys()))
        
        submitted = st.form_submit_button("Submit Action 🚀")
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
                    st.success("Transaction logged! The engine has updated your stats.")
                    st.rerun()
                else:
                    st.error(f"Error: {res.text}")
            except Exception as e:
                st.error(f"Error connecting to backend: {e}")
    st.markdown('</div>', unsafe_allow_html=True)

# 3. Debt Bosses
with col3:
    st.markdown('<div class="neon-magenta" style="padding: 20px; border-radius: 12px; text-align: center;">', unsafe_allow_html=True)
    st.markdown("### Debt Bosses 💀")
    debt_bosses = dashboard_data.get("debt_bosses", [])
    if not debt_bosses:
        st.info("No active debt bosses. You are clear!")
    else:
        for boss in debt_bosses:
            st.markdown(f"<div style='margin-bottom: 5px; color: #aaaaaa;'><b>{boss['name']}</b></div>", unsafe_allow_html=True)
            st.markdown(f"<div style='margin-bottom: 5px; color: var(--magenta); text-shadow: 0 0 5px var(--magenta); font-size: 1.2rem;'>HP: ${boss['total_hp']:.2f}</div>", unsafe_allow_html=True)
            # Placeholder progress 
            st.progress(100 if boss['total_hp'] > 0 else 0) 
            st.markdown("<hr style='border-color: rgba(255,255,255,0.1);'>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
            
st.markdown("---")
st.markdown("### Recent Transactions")
# Recent transactions view
try:
    tx_list = requests.get(f"{BACKEND_URL}/transactions?limit=10").json()
    if tx_list:
        for tx in tx_list:
            st.markdown(f"**{tx['timestamp'][:10]}** | <span style='color: var(--cyan);'>{tx['type']}</span> | <span style='color: var(--magenta);'>${tx['amount']:.2f}</span> | {tx.get('description', '')}", unsafe_allow_html=True)
            st.divider()
    else:
        st.write("No transactions yet.")
except:
    st.write("Could not load transactions.")

st.sidebar.title("System Config")
with st.sidebar.expander("Create new Bucket"):
    with st.form("new_bucket_form"):
        b_name = st.text_input("Bucket Name")
        b_target = st.number_input("Target Balance", min_value=0.0)
        if st.form_submit_button("Create Bucket"):
            requests.post(f"{BACKEND_URL}/buckets", json={"name": b_name, "target_balance": b_target})
            st.rerun()
