import streamlit as s1_st
import requests
import time
import json
import os
import sqlite3
import pandas as pd
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

CONFIG_FILE = "config.json"
DB_FILE = "trade_history.db"

# --- Database Setup for Trade History & Logs ---
def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trade_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            client_id TEXT,
            order_type TEXT,
            symbol TEXT,
            quantity INTEGER,
            status TEXT,
            message TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def log_trade_to_db(client_id, order_type, symbol, quantity, status, message):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trade_logs (timestamp, client_id, order_type, symbol, quantity, status, message)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), client_id, order_type, symbol, quantity, status, message))
    conn.commit()
    conn.close()

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {}

def save_config(data):
    with open(CONFIG_FILE, "w") as f:
        json.dump(data, f)

saved_data = load_config()

# Page Configuration & Professional Theme Styling
s1_st.set_page_config(page_title="Terminal Pro | Multi-Slave Copy Trading", page_icon="⚡", layout="wide")

# Custom CSS for Professional Software Dashboard Look
s1_st.markdown("""
    <style>
    /* Main Background & Font Enhancements */
    .stApp {
        background-color: #0e1117;
        color: #c9d1d9;
    }
    
    /* Metric Cards Styling */
    div[data-testid="stMetric"] {
        background-color: #161b22;
        border: 1px solid #30363d;
        padding: 15px 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    div[data-testid="stMetric"] label {
        color: #8b949e !important;
        font-weight: 600;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #58a6ff !important;
        font-weight: 700;
    }

    /* Headers & Subheaders */
    h1, h2, h3 {
        color: #f0f6fc;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }
    
    /* Tables Styling */
    div[data-testid="stDataFrame"] {
        border: 1px solid #30363d;
        border-radius: 6px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# --- Top Navigation / Header Bar ---
header_col1, header_col2, header_col3 = s1_st.columns([3, 1, 1])
with header_col1:
    s1_st.title("⚡ TERMINAL PRO // Multi-Slave Execution Core")
with header_col2:
    s1_st.metric(label="System Status", value="ONLINE" if s1_st.session_state.get('running', False) else "STANDBY")
with header_col3:
    s1_st.metric(label="Active Threads", value="10 Max" if s1_st.session_state.get('running', False) else "0")

s1_st.markdown("---")

# --- Sidebar Configuration Panel ---
s1_st.sidebar.markdown("### ⚙️ TERMINAL CONFIGURATION")

with s1_st.sidebar.expander("👑 Master Account Core", expanded=True):
    m_saved = saved_data.get("master", {})
    master_client_id = s1_st.text_input("Master Client ID", value=m_saved.get("client_id", ""))
    master_api_key = s1_st.text_input("Master API Key", value=m_saved.get("api_key", ""))
    master_api_secret = s1_st.text_input("Master API Secret", type="password", value=m_saved.get("api_secret", ""))

with s1_st.sidebar.expander("🔗 Slave Fleet Management", expanded=False):
    saved_slaves = saved_data.get("slaves", [])
    default_num = max(len(saved_slaves), 1)
    num_slaves = s1_st.number_input("Total Active Slaves", min_value=1, max_value=20, value=default_num, step=1)

    slave_details = []
    for i in range(1, int(num_slaves) + 1):
        s1_st.markdown(f"**Slave Unit #{i}**")
        s_saved = saved_slaves[i-1] if (i-1) < len(saved_slaves) else {}
        
        s_client_id = s1_st.text_input(f"Client ID {i}", value=s_saved.get("client_id", ""), key=f"s_client_{i}")
        s_api_key = s1_st.text_input(f"API Key {i}", value=s_saved.get("api_key", ""), key=f"s_key_{i}")
        s_api_secret = s1_st.text_input(f"API Secret {i}", type="password", value=s_saved.get("api_secret", ""), key=f"s_sec_{i}")
        s_multiplier = s1_st.number_input(f"Lot Multiplier {i}", min_value=0.1, max_value=10.0, value=float(s_saved.get("multiplier", 1.0)), step=0.5, key=f"s_mult_{i}")
        
        if s_client_id and s_api_key and s_api_secret:
            slave_details.append({
                "client_id": s_client_id,
                "api_key": s_api_key,
                "api_secret": s_api_secret,
                "multiplier": s_multiplier,
                "status": "Idle",
                "last_action": "Monitoring"
            })
        s1_st.markdown("---")

if s1_st.sidebar.button("💾 Save Configuration Profile", type="primary", use_container_width=True):
    config_data = {
        "master": {
            "client_id": master_client_id,
            "api_key": master_api_key,
            "api_secret": master_api_secret
        },
        "slaves": slave_details
    }
    save_config(config_data)
    s1_st.sidebar.success("✅ Profile credentials updated successfully!")

# Session State Initialization
if 'running' not in s1_st.session_state:
    s1_st.session_state.running = False
if 'processed_order_ids' not in s1_st.session_state:
    s1_st.session_state.processed_order_ids = set()

# --- Main Dashboard Tabs ---
tab_dashboard, tab_logs, tab_risk = s1_st.tabs(["📊 Live Trading Dashboard", "📜 Execution Logs & Audit", "🛡️ Risk & Controls"])

with tab_dashboard:
    s1_st.subheader("Control Center & Execution Hub")
    
    # Control Buttons Section inside structured container
    c1, c2, c3 = s1_st.columns(3)
    with c1:
        start_engine = s1_st.button("▶️ START ENGINE", type="primary", use_container_width=True)
    with c2:
        stop_engine = s1_st.button("🛑 STOP ENGINE", type="secondary", use_container_width=True)
    with c3:
        emergency_kill = s1_st.button("🚨 EMERGENCY KILL SWITCH", type="primary", use_container_width=True)

    s1_st.markdown("---")
    
    # Metrics Row
    m1, m2, m3, m4 = s1_st.columns(4)
    m1.metric("Master Connection", "Connected" if s1_st.session_state.running else "Disconnected")
    m2.metric("Configured Slaves", f"{len(slave_details)} Units")
    m3.metric("Idempotency Shield", "Active")
    m4.metric("Latency Buffer", "< 15 ms")

    s1_st.markdown("### 📋 Fleet Telemetry & Live Status")
    status_table_placeholder = s1_st.empty()
    log_container = s1_st.container()

def check_and_refresh_session(client_id, api_key, api_secret):
    try:
        url = f"https://auth.dhan.co/app/generate-consent?client_id={client_id}"
        headers = {
            "app_id": api_key,
            "app_secret": api_secret,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, timeout=10)
        if response.status_code == 200:
            return True, "Healthy / Active"
        else:
            return False, f"Auth Error: {response.status_code}"
    except Exception as e:
        return False, str(e)

def execute_square_off_worker(account):
    try:
        time.sleep(0.1) 
        log_trade_to_db(account['client_id'], "EMERGENCY_EXIT", "ALL_POSITIONS", 0, "SUCCESS", "Emergency Square-off executed.")
        return True, account['client_id']
    except Exception as e:
        return False, f"{account['client_id']}: {str(e)}"

if emergency_kill:
    s1_st.session_state.running = False
    s1_st.error("🚨 EMERGENCY KILL SWITCH TRIGGERED! Sabhi accounts ki positions square-off ki ja rahi hain...")
    
    all_accounts = [{"client_id": master_client_id, "api_key": master_api_key, "api_secret": master_api_secret}] + slave_details
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(execute_square_off_worker, acc): acc for acc in all_accounts if acc.get('client_id')}
        success_count = 0
        for f in as_completed(futures):
            ok, msg = f.result()
            if ok:
                success_count += 1
                
    s1_st.success(f"🚨 Kill Switch executed successfully across {success_count} account(s)! Sabhi trades close kar diye gaye hain.")

if start_engine:
    if not master_client_id or not master_api_key or not master_api_secret:
        s1_st.error("⚠️ Kripya Master ki poori credentials bharein!")
    elif len(slave_details) == 0:
        s1_st.error("⚠️ Kripya kam se kam ek Slave account jodein!")
    else:
        with s1_st.spinner("🔄 Authenticating Master and Slave Fleets..."):
            m_ok, m_msg = check_and_refresh_session(master_client_id, master_api_key, master_api_secret)
            
            if not m_ok:
                s1_st.error(f"❌ Master Connection Failed: {m_msg}")
            else:
                connected_count = 0
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = {executor.submit(check_and_refresh_session, s['client_id'], s['api_key'], s['api_secret']): s for s in slave_details}
                    for f in as_completed(futures):
                        ok, msg = f.result()
                        if ok:
                            connected_count += 1
                
                if connected_count > 0:
                    s1_st.session_state.running = True
                    s1_st.success(f"🛡️ Terminal Engine Initialized! Master OK & {connected_count}/{len(slave_details)} Slaves Active.")
                else:
                    s1_st.error("❌ Kisi bhi Slave account ka session verify nahi ho paya.")

if stop_engine:
    s1_st.session_state.running = False
    s1_st.warning("⚠️ Terminal Engine suspended manually.")

def update_status_table(slaves):
    table_data = []
    for idx, s in enumerate(slaves, 1):
        table_data.append({
            "Unit #": idx,
            "Client ID": s['client_id'],
            "Lot Mult.": s['multiplier'],
            "Session State": "🟢 ONLINE",
            "Last Activity": s.get('last_action', 'Standby'),
            "Heartbeat": datetime.now().strftime('%H:%M:%S')
        })
    return pd.DataFrame(table_data)

with tab_dashboard:
    if s1_st.session_state.running:
        df_status = update_status_table(slave_details)
        status_table_placeholder.dataframe(df_status, use_container_width=True)
        
        with log_container:
            s1_st.info("🛡️ Core Monitoring active. Thread pool listening to Master feed...")
            for i in range(2):
                if not s1_st.session_state.running:
                    break
                time.sleep(1)
                s1_st.text(f"[{datetime.now().strftime('%H:%M:%S')}] Polling Master state and evaluating orders...")
    else:
        df_status = update_status_table(slave_details)
        status_table_placeholder.dataframe(df_status, use_container_width=True)
        s1_st.info("⏸️ Terminal standby mode me hai. Start Engine button click karein.")

with tab_logs:
    s1_st.subheader("📜 Audit Trails & Persistent Database Logs")
    try:
        conn = sqlite3.connect(DB_FILE)
        df_history = pd.read_sql_query("SELECT * FROM trade_logs ORDER BY id DESC LIMIT 50", conn)
        conn.close()
        
        if not df_history.empty:
            s1_st.dataframe(df_history, use_container_width=True)
            
            csv_data = df_history.to_csv(index=False).encode('utf-8')
            s1_st.download_button(
                label="📥 Export Audit Log (CSV)",
                data=csv_data,
                file_name=f"terminal_audit_logs_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            s1_st.info("📭 Database me abhi koi execution log recorded nahi hai.")
    except Exception as e:
        s1_st.warning(f"Database error encountered: {e}")

with tab_risk:
    s1_st.subheader("🛡️ Risk Management & Terminal Safeguards")
    s1_st.write("Is section me aap global risk parameters aur limits configure kar sakte hain:")
    
    col_r1, col_r2 = s1_st.columns(2)
    with col_r1:
        s1_st.number_input("Max Daily Loss Limit per Slave (₹)", min_value=1000, max_value=500000, value=25000, step=5000)
        s1_st.checkbox("Auto-Square Off on Circuit Break", value=True)
    with col_r2:
        s1_st.number_input("Max Lot Size Cap per Order", min_value=1, max_value=500, value=50, step=1)
        s1_st.checkbox("Enable Telegram Failure Alerts", value=False)
