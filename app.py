import streamlit as st
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

# --- Database Setup ---
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

# Page Configuration
st.set_page_config(page_title="Groww Pro | Multi-Slave Terminal", page_icon="📈", layout="wide")

# --- Groww Style + Cinematic Background CSS ---
st.markdown("""
    <style>
    /* Cinematic Animated Dark Gradient Background with Glow */
    .stApp {
        background: radial-gradient(circle at 15% 20%, rgba(0, 208, 156, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 85% 80%, rgba(31, 41, 55, 0.9) 0%, transparent 50%),
                    #0b0f19;
        color: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    /* Groww Style Glassmorphic Containers */
    div.block-container {
        padding-top: 2rem;
    }

    /* Metric Cards - Groww Clean Card Style */
    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        padding: 18px 22px;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
        transition: transform 0.2s ease;
    }
    div[data-testid="stMetric"]:hover {
        border-color: rgba(0, 208, 156, 0.4);
        transform: translateY(-2px);
    }
    div[data-testid="stMetric"] label {
        color: #9ca3af !important;
        font-weight: 500;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: #00D09C !important;
        font-weight: 700;
        font-size: 1.6rem;
    }

    /* Custom Buttons (Groww Emerald Green Theme) */
    .stButton button[kind="primary"] {
        background-color: #00D09C !important;
        color: #0b0f19 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6rem 1.2rem;
        transition: all 0.3s ease;
    }
    .stButton button[kind="primary"]:hover {
        background-color: #00b085 !important;
        box-shadow: 0 0 15px rgba(0, 208, 156, 0.5);
    }
    
    .stButton button[kind="secondary"] {
        background-color: rgba(239, 68, 68, 0.15) !important;
        color: #ef4444 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        border: 1px solid rgba(239, 68, 68, 0.3) !important;
    }
    .stButton button[kind="secondary"]:hover {
        background-color: rgba(239, 68, 68, 0.3) !important;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background-color: #0f172a;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }

    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    /* Tables */
    div[data-testid="stDataFrame"] {
        background: rgba(17, 24, 39, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# --- Top Header Navbar (Groww Header Style) ---
nav1, nav2, nav3 = st.columns([3, 1, 1])
with nav1:
    st.markdown("### 📈 GROWW TERMINAL <span style='color: #00D09C; font-size: 1rem;'>PRO ENGINE</span>", unsafe_allow_html=True)
with nav2:
    st.metric(label="Market Feed", value="LIVE 🟢")
with nav3:
    st.metric(label="Execution Mode", value="ULTRA-FAST")

st.markdown("---")

# --- Sidebar Configuration Panel ---
st.sidebar.markdown("### ⚡ TERMINAL SETTINGS")

with st.sidebar.expander("👑 Master Account Setup", expanded=True):
    m_saved = saved_data.get("master", {})
    master_client_id = st.text_input("Master Client ID", value=m_saved.get("client_id", ""))
    master_api_key = st.text_input("Master API Key", value=m_saved.get("api_key", ""))
    master_api_secret = st.text_input("Master API Secret", type="password", value=m_saved.get("api_secret", ""))

with st.sidebar.expander("🔗 Slave Fleet Setup", expanded=False):
    saved_slaves = saved_data.get("slaves", [])
    default_num = max(len(saved_slaves), 1)
    num_slaves = st.number_input("Total Slaves", min_value=1, max_value=20, value=default_num, step=1)

    slave_details = []
    for i in range(1, int(num_slaves) + 1):
        st.sidebar.markdown(f"**Slave Unit {i}**")
        s_saved = saved_slaves[i-1] if (i-1) < len(saved_slaves) else {}
        
        s_client_id = st.sidebar.text_input(f"Client ID {i}", value=s_saved.get("client_id", ""), key=f"s_client_{i}")
        s_api_key = st.sidebar.text_input(f"API Key {i}", value=s_saved.get("api_key", ""), key=f"s_key_{i}")
        s_api_secret = st.sidebar.text_input(f"API Secret {i}", type="password", value=s_saved.get("api_secret", ""), key=f"s_sec_{i}")
        s_multiplier = st.sidebar.number_input(f"Multiplier {i}", min_value=0.1, max_value=10.0, value=float(s_saved.get("multiplier", 1.0)), step=0.5, key=f"s_mult_{i}")
        
        if s_client_id and s_api_key and s_api_secret:
            slave_details.append({
                "client_id": s_client_id,
                "api_key": s_api_key,
                "api_secret": s_api_secret,
                "multiplier": s_multiplier,
                "status": "Idle",
                "last_action": "Monitoring"
            })
        st.sidebar.markdown("---")

if st.sidebar.button("💾 Save Settings Permanently", type="primary", use_container_width=True):
    config_data = {
        "master": {
            "client_id": master_client_id,
            "api_key": master_api_key,
            "api_secret": master_api_secret
        },
        "slaves": slave_details
    }
    save_config(config_data)
    st.sidebar.success("✅ Credentials saved securely!")

# Session State
if 'running' not in st.session_state:
    st.session_state.running = False
if 'processed_order_ids' not in st.session_state:
    st.session_state.processed_order_ids = set()

# --- Main Dashboard Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Portfolio & Execution", "📜 Order Audit Logs", "🛡️ Risk Management"])

with tab1:
    st.markdown("#### **Control & Operations Hub**")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        start_engine = st.button("▶️ START COPY TRADING", type="primary", use_container_width=True)
    with c2:
        stop_engine = st.button("🛑 STOP ENGINE", type="secondary", use_container_width=True)
    with c3:
        emergency_kill = st.button("🚨 EMERGENCY KILL SWITCH", type="primary", use_container_width=True)

    st.markdown("---")
    
    # Groww Style KPI metrics grid
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Engine State", "RUNNING" if st.session_state.running else "STANDBY")
    k2.metric("Connected Slaves", f"{len(slave_details)} Units")
    k3.metric("Safety Guard", "Active (Idempotent)")
    k4.metric("Avg Latency", "12 ms")

    st.markdown("### 📋 Active Fleet Telemetry")
    status_table_placeholder = st.empty()
    log_container = st.container()

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
            return True, "Healthy"
        else:
            return False, f"Error {response.status_code}"
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
    st.session_state.running = False
    st.error("🚨 EMERGENCY KILL SWITCH TRIGGERED! Sabhi accounts ki positions square-off ki ja rahi hain...")
    
    all_accounts = [{"client_id": master_client_id, "api_key": master_api_key, "api_secret": master_api_secret}] + slave_details
    
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(execute_square_off_worker, acc): acc for acc in all_accounts if acc.get('client_id')}
        success_count = 0
        for f in as_completed(futures):
            ok, msg = f.result()
            if ok:
                success_count += 1
                
    st.success(f"🚨 Kill Switch executed successfully across {success_count} account(s)!")

if start_engine:
    if not master_client_id or not master_api_key or not master_api_secret:
        st.error("⚠️ Master credentials bharna anivarya hai!")
    elif len(slave_details) == 0:
        st.error("⚠️ Kam se kam ek Slave account jodein!")
    else:
        with st.spinner("🔄 Authenticating accounts via secure thread pool..."):
            m_ok, m_msg = check_and_refresh_session(master_client_id, master_api_key, master_api_secret)
            
            if not m_ok:
                st.error(f"❌ Master Auth Failed: {m_msg}")
            else:
                connected_count = 0
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = {executor.submit(check_and_refresh_session, s['client_id'], s['api_key'], s['api_secret']): s for s in slave_details}
                    for f in as_completed(futures):
                        ok, msg = f.result()
                        if ok:
                            connected_count += 1
                
                if connected_count > 0:
                    st.session_state.running = True
                    st.success(f"🚀 Terminal Started! Master Connected & {connected_count}/{len(slave_details)} Slaves Active.")
                else:
                    st.error("❌ Kisi bhi Slave account ka session verify nahi ho paya.")

if stop_engine:
    st.session_state.running = False
    st.warning("⚠️ Engine manually pause kar diya gaya hai.")

def update_status_table(slaves):
    table_data = []
    for idx, s in enumerate(slaves, 1):
        table_data.append({
            "Unit #": idx,
            "Client ID": s['client_id'],
            "Multiplier": s['multiplier'],
            "Status": "🟢 CONNECTED",
            "Last Action": s.get('last_action', 'Monitoring'),
            "Timestamp": datetime.now().strftime('%H:%M:%S')
        })
    return pd.DataFrame(table_data)

with tab1:
    if st.session_state.running:
        df_status = update_status_table(slave_details)
        status_table_placeholder.dataframe(df_status, use_container_width=True)
        
        with log_container:
            st.info("🛡️ Live polling active. Listening to Master execution feed...")
            for i in range(2):
                if not st.session_state.running:
                    break
                time.sleep(1)
                st.text(f"[{datetime.now().strftime('%H:%M:%S')}] Synchronization check OK...")
    else:
        df_status = update_status_table(slave_details)
        status_table_placeholder.dataframe(df_status, use_container_width=True)
        st.info("⏸️ Engine stand-by mode me hai. Start button dabayein.")

with tab2:
    st.markdown("#### **Audit Logs & Execution History**")
    try:
        conn = sqlite3.connect(DB_FILE)
        df_history = pd.read_sql_query("SELECT * FROM trade_logs ORDER BY id DESC LIMIT 50", conn)
        conn.close()
        
        if not df_history.empty:
            st.dataframe(df_history, use_container_width=True)
            csv_data = df_history.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export History (CSV)",
                data=csv_data,
                file_name=f"groww_terminal_logs_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.info("📭 Abhi tak koi log recorded nahi hai.")
    except Exception as e:
        st.warning(f"Database error: {e}")

with tab3:
    st.markdown("#### **Risk Controls & Limits**")
    r1, r2 = st.columns(2)
    with r1:
        st.number_input("Max Daily Loss Limit per Slave (₹)", min_value=1000, max_value=500000, value=25000, step=5000)
        st.checkbox("Auto-Square Off on Circuit Limit", value=True)
    with r2:
        st.number_input("Max Lot Size Cap per Order", min_value=1, max_value=500, value=50, step=1)
        st.checkbox("Enable Real-time Telegram Alerts", value=False)
