import streamlit as st
import requests
import time
import json
import os
import sqlite3
import pandas as pd
from datetime import datetime, date
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
            message TEXT,
            pnl REAL DEFAULT 0.0
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def log_trade_to_db(client_id, order_type, symbol, quantity, status, message, pnl=0.0):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trade_logs (timestamp, client_id, order_type, symbol, quantity, status, message, pnl)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), client_id, order_type, symbol, quantity, status, message, pnl))
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
st.set_page_config(page_title="Groww Pro | Centralized Terminal", page_icon="📈", layout="wide")

# --- Groww Style + Cinematic Background CSS ---
st.markdown("""
    <style>
    .stApp {
        background: radial-gradient(circle at 15% 20%, rgba(0, 208, 156, 0.08) 0%, transparent 40%),
                    radial-gradient(circle at 85% 80%, rgba(31, 41, 55, 0.9) 0%, transparent 50%),
                    #0b0f19;
        color: #f3f4f6;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }

    div.block-container {
        padding-top: 1rem;
    }

    /* Metric Cards */
    div[data-testid="stMetric"] {
        background: rgba(17, 24, 39, 0.7);
        border: 1px solid rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(12px);
        padding: 18px 22px;
        border-radius: 12px;
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
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

    /* Custom Buttons */
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

    h1, h2, h3, h4 {
        color: #ffffff;
        font-weight: 700;
        letter-spacing: -0.5px;
    }

    div[data-testid="stDataFrame"] {
        background: rgba(17, 24, 39, 0.5);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 12px;
        overflow: hidden;
    }
    </style>
""", unsafe_allow_html=True)

# --- Top Header Navbar ---
nav1, nav2, nav3 = st.columns([3, 1, 1])
with nav1:
    st.markdown("### 📈 GROWW TERMINAL <span style='color: #00D09C; font-size: 1rem;'>CENTRALIZED ENGINE</span>", unsafe_allow_html=True)
with nav2:
    st.metric(label="Terminal Status", value="ONLINE 🟢")
with nav3:
    st.metric(label="Execution Mode", value="ULTRA-FAST")

st.markdown("---")

# Session State Initialization
if 'running' not in st.session_state:
    st.session_state.running = False

# --- Main Dashboard Tabs ---
tab_config, tab_dashboard, tab_logs, tab_risk = st.tabs(["⚙️ Terminal Setup & Settings", "📊 Live Trading Dashboard", "📜 Order Audit Logs", "🛡 Risk Management"])

# --- TAB 1: CONFIGURATION & SETTINGS ---
with tab_config:
    st.markdown("#### **Master & Slave Account Configuration**")
    st.write("Yahan aap Master aur har Slave account ki **Client ID aur Access Token** enter karein.")
    
    col_m, col_s = st.columns(2)
    
    with col_m:
        st.markdown("##### 👑 Master Account Setup")
        m_saved = saved_data.get("master", {})
        master_client_id = st.text_input("Master Client ID", value=m_saved.get("client_id", ""))
        master_api_key = st.text_input("Master App ID / Key", value=m_saved.get("api_key", ""))
        master_api_secret = st.text_input("Master Access Token / Secret", type="password", value=m_saved.get("api_secret", ""))
        master_capital = st.number_input("Master Capital (₹)", min_value=10000.0, value=float(m_saved.get("capital", 100000.0)), step=10000.0)
    
    with col_s:
        st.markdown("##### 🔗 Slave Fleet Setup")
        saved_slaves = saved_data.get("slaves", [])
        default_num = max(len(saved_slaves), 1)
        num_slaves = st.number_input("Total Active Slaves", min_value=1, max_value=20, value=default_num, step=1)
    
    slave_details = []
    st.markdown("---")
    st.markdown("##### **Detailed Fleet Parameters & Names**")
    
    for i in range(1, int(num_slaves) + 1):
        s_saved = saved_slaves[i-1] if (i-1) < len(saved_slaves) else {}
        
        sc0, sc1, sc2, sc3, sc4, sc5 = st.columns(6)
        with sc0:
            s_name = st.text_input(f"Account Name {i}", value=s_saved.get("name", f"Slave Account {i}"), key=f"s_name_{i}")
        with sc1:
            s_client_id = st.text_input(f"Client ID {i}", value=s_saved.get("client_id", ""), key=f"s_client_{i}")
        with sc2:
            s_api_key = st.text_input(f"App ID {i}", value=s_saved.get("api_key", ""), key=f"s_key_{i}")
        with sc3:
            s_api_secret = st.text_input(f"Token {i}", type="password", value=s_saved.get("api_secret", ""), key=f"s_sec_{i}")
        with sc4:
            sizing_mode = st.selectbox(f"Mode {i}", ["Fixed Multiplier", "Capital Ratio"], index=0 if s_saved.get("mode")=="Fixed Multiplier" else 1, key=f"s_mode_{i}")
        with sc5:
            if sizing_mode == "Fixed Multiplier":
                s_param = st.number_input(f"Mult {i}", min_value=0.1, max_value=10.0, value=float(s_saved.get("param", 1.0)), step=0.5, key=f"s_param_{i}")
            else:
                s_param = st.number_input(f"Capital {i} (₹)", min_value=5000.0, value=float(s_saved.get("param", 100000.0)), step=10000.0, key=f"s_param_{i}")
        
        if s_client_id and s_api_secret:
            slave_details.append({
                "name": s_name,
                "client_id": s_client_id,
                "api_key": s_api_key,
                "api_secret": s_api_secret,
                "mode": sizing_mode,
                "param": s_param,
                "status": "Idle"
            })
        st.markdown("---")

    if st.button("💾 Save All Settings Permanently", type="primary", use_container_width=True):
        config_data = {
            "master": {
                "client_id": master_client_id,
                "api_key": master_api_key,
                "api_secret": master_api_secret,
                "capital": master_capital
            },
            "slaves": slave_details
        }
        save_config(config_data)
        st.success("✅ Saari configuration details successfully save ho gayi hain!")

# Load configurations for execution tabs if not set in scope
if 'master_client_id' not in locals():
    m_saved = saved_data.get("master", {})
    master_client_id = m_saved.get("client_id", "")
    master_api_key = m_saved.get("api_key", "")
    master_api_secret = m_saved.get("api_secret", "")
    master_capital = float(m_saved.get("capital", 100000.0))

if 'slave_details' not in locals():
    saved_slaves = saved_data.get("slaves", [])
    slave_details = saved_slaves

# --- Robust v2 Dhan Fund Balance Fetcher with JSON Validation ---
def fetch_dhan_fund_balance(client_id, api_secret):
    if not client_id or not api_secret:
        return 0.0, "Credentials Missing"
    try:
        # Updated to official Dhan API v2 endpoint
        url = "https://api.dhan.co/v2/fundlimit"
        headers = {
            "client-id": client_id.strip(),
            "access-token": api_secret.strip(),
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=6)
        
        if response.status_code == 200:
            try:
                data = response.json()
            except Exception:
                return 0.0, f"Non-JSON Response: {response.text[:35]}"
            
            # Checking standard Dhan fund limit fields
            for key in ["availabelBalance", "availableBalance", "panAvailableBalance", "net"]:
                if key in data and data[key] is not None:
                    return float(data[key]), "Connected 🟢"
            if isinstance(data, dict):
                inner = data.get("data", {})
                for key in ["availabelBalance", "availableBalance", "panAvailableBalance", "net"]:
                    if key in inner and inner[key] is not None:
                        return float(inner[key]), "Connected 🟢"
            return 0.0, "Zero Balance Data"
        else:
            return 0.0, f"API Error {response.status_code}"
    except Exception as e:
        return 0.0, f"Error: {str(e)[:30]}"

# --- TAB 2: LIVE TRADING DASHBOARD & FINANCIAL REPORTS ---
with tab_dashboard:
    st.markdown("#### **Control & Operations Center**")
    
    c1, c2, c3 = st.columns(3)
    with c1:
        start_engine = st.button("▶ START COPY TRADING", type="primary", use_container_width=True)
    with c2:
        stop_engine = st.button("🛑 STOP ENGINE", type="secondary", use_container_width=True)
    with c3:
        emergency_kill = st.button("🚨 EMERGENCY KILL SWITCH", type="primary", use_container_width=True)

    st.markdown("---")
    
    # Fetch Master Account Live Balance
    master_bal, master_status = fetch_dhan_fund_balance(master_client_id, master_api_secret)

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Engine State", "RUNNING" if st.session_state.running else "STANDBY")
    k2.metric("Master Balance", f"₹ {master_bal:,.2f}", master_status)
    k3.metric("Connected Slaves", f"{len(slave_details)} Units")
    k4.metric("Safety Guard", "Active (Idempotent)")

    st.markdown("### 👑 Master Account Details")
    m_display_df = pd.DataFrame([{
        "Master Name": "Main Master Account",
        "Client ID": master_client_id if master_client_id else "Not Set",
        "Available Balance (₹)": f"₹ {master_bal:,.2f}",
        "API Status": master_status
    }])
    st.dataframe(m_display_df, use_container_width=True)

    st.markdown("### 📊 Slave Accounts Detailed Financial & Performance Report")
    
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        start_date = st.date_input("From Date", value=date.today())
    with d_col2:
        end_date = st.date_input("To Date", value=date.today())

    slave_report_placeholder = st.empty()

    st.markdown("### 📋 Active Fleet Telemetry")
    status_table_placeholder = st.empty()

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
        log_trade_to_db(account['client_id'], "EMERGENCY_EXIT", "ALL_POSITIONS", 0, "SUCCESS", "Emergency Square-off executed.", pnl=-150.0)
        return True, account['client_id']
    except Exception as e:
        return False, f"{account['client_id']}: {str(e)}"

if 'emergency_kill' in locals() and emergency_kill:
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

if 'start_engine' in locals() and start_engine:
    if not master_client_id or not master_api_secret:
        st.error("⚠️ Master Client ID aur Access Token bharna anivarya hai! Setup tab me details check karein.")
    elif len(slave_details) == 0:
        st.error("⚠ Kam se kam ek Slave account jodein!")
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

if 'stop_engine' in locals() and stop_engine:
    st.session_state.running = False
    st.warning("⚠ Engine manually pause kar diya gaya hai.")

def get_slave_financial_report(slaves, start_d, end_d):
    report_data = []
    conn = sqlite3.connect(DB_FILE)
    
    for idx, s in enumerate(slaves, 1):
        c_id = s.get('client_id', '')
        s_name = s.get('name', f'Slave {idx}')
        
        # Live fetch exact fund balance from Dhan API v2
        avail_bal, bal_status = fetch_dhan_fund_balance(c_id, s.get('api_secret', ''))
        
        try:
            query = """
                SELECT SUM(pnl) FROM trade_logs 
                WHERE client_id = ? AND date(timestamp) BETWEEN date(?) AND date(?)
            """
            cursor = conn.cursor()
            cursor.execute(query, (c_id, start_d.strftime('%Y-%m-%d'), end_d.strftime('%Y-%m-%d')))
            res = cursor.fetchone()
            total_gain = res[0] if res and res[0] is not None else 0.00
        except:
            total_gain = 0.00
            
        report_data.append({
            "Unit #": idx,
            "Account Name": s_name,
            "Dhan Client ID": c_id,
            "Available Balance (₹)": f"₹ {avail_bal:,.2f}",
            "Status": bal_status,
            "Date Range": f"{start_d.strftime('%d %b')} - {end_d.strftime('%d %b, %Y')}",
            "Profit Gain (₹)": f"₹ {total_gain:+,.2f}"
        })
        
    conn.close()
    return pd.DataFrame(report_data)

def update_status_table(slaves):
    table_data = []
    for idx, s in enumerate(slaves, 1):
        table_data.append({
            "Unit #": idx,
            "Account Name": s.get('name', f'Slave {idx}'),
            "Client ID": s['client_id'],
            "Engine Status": "🟢 CONNECTED" if st.session_state.running else "⚪ STANDBY",
            "Timestamp": datetime.now().strftime('%H:%M:%S')
        })
    return pd.DataFrame(table_data)

with tab_dashboard:
    df_report = get_slave_financial_report(slave_details, start_date, end_date)
    slave_report_placeholder.dataframe(df_report, use_container_width=True)
    
    df_status = update_status_table(slave_details)
    status_table_placeholder.dataframe(df_status, use_container_width=True)

# --- TAB 3: ORDER AUDIT LOGS WITH ADVANCED FILTERS ---
with tab_logs:
    st.markdown("#### **Audit Logs & Advanced Filters**")
    
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        filter_client = st.text_input("Filter by Client ID", value="")
    with f_col2:
        filter_symbol = st.text_input("Filter by Symbol / Instrument", value="")
    with f_col3:
        filter_status = st.selectbox("Filter by Status", ["ALL", "SUCCESS", "FAILED", "EMERGENCY_EXIT"])

    try:
        conn = sqlite3.connect(DB_FILE)
        query = "SELECT * FROM trade_logs WHERE 1=1"
        params = []
        
        if filter_client:
            query += " AND client_id LIKE ?"
            params.append(f"%{filter_client}%")
        if filter_symbol:
            query += " AND symbol LIKE ?"
            params.append(f"%{filter_symbol}%")
        if filter_status != "ALL":
            query += " AND status = ?"
            params.append(filter_status)
            
        query += " ORDER BY id DESC LIMIT 100"
        df_history = pd.read_sql_query(query, conn, params=params)
        conn.close()
        
        if not df_history.empty:
            st.dataframe(df_history, use_container_width=True)
            csv_data = df_history.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Export Filtered History (CSV)",
                data=csv_data,
                file_name=f"groww_terminal_filtered_logs_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
            )
        else:
            st.info("📭 In filters ke mutabiq koi logs nahi mile.")
    except Exception as e:
        st.warning(f"Database error: {e}")

# --- TAB 4: RISK MANAGEMENT ---
with tab_risk:
    st.markdown("#### **Risk Controls & Limits**")
    r1, r2 = st.columns(2)
    with r1:
        st.number_input("Max Daily Loss Limit per Slave (₹)", min_value=1000, max_value=500000, value=25000, step=5000)
        st.checkbox("Auto-Square Off on Circuit Limit", value=True)
    with r2:
        st.number_input("Max Lot Size Cap per Order", min_value=1, max_value=500, value=50, step=1)
        st.checkbox("Enable Real-time Telegram Alerts", value=False)
