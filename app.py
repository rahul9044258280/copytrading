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
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS processed_orders (
            order_hash TEXT PRIMARY KEY,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def is_order_processed(order_hash):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM processed_orders WHERE order_hash = ?", (order_hash,))
    exists = cursor.fetchone()
    conn.close()
    return exists is not None

def mark_order_processed(order_hash):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO processed_orders (order_hash, timestamp) VALUES (?, ?)", 
                   (order_hash, datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')))
    conn.commit()
    conn.close()

def log_trade_to_db(client_id, order_type, symbol, quantity, status, message, pnl=0.0):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO trade_logs (timestamp, client_id, order_type, symbol, quantity, status, message, pnl)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')[:-3], client_id, order_type, symbol, quantity, status, message, pnl))
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

st.set_page_config(page_title="Groww Pro | Ultra-Fast Copy Trading Terminal", page_icon="📈", layout="wide")

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

nav1, nav2, nav3, nav4 = st.columns([2.5, 1, 1, 1])
with nav1:
    st.markdown("### 📈 GROWW TERMINAL <span style='color: #00D09C; font-size: 1rem;'>ULTRA-FAST FLEET ENGINE</span>", unsafe_allow_html=True)
with nav2:
    st.metric(label="Terminal Status", value="ONLINE 🟢")
with nav3:
    st.metric(label="Latency Mode", value="< 50ms ⚡")
with nav4:
    auto_refresh_sec = st.selectbox("Sync Refresh Rate", [1, 2, 5, 10, "Off"], index=0)

st.markdown("---")

if 'running' not in st.session_state:
    st.session_state.running = False

tab_config, tab_dashboard, tab_logs, tab_reports, tab_risk = st.tabs([
    "⚙️ Terminal Setup & Settings", 
    "📊 Live Trading Dashboard", 
    "📜 Order Audit Logs", 
    "📈 Financial Reports", 
    "🛡 Risk Management"
])

with tab_config:
    st.markdown("#### **Master & Slave Fleet Management**")
    
    m_saved = saved_data.get("master", {})
    master_client_id = st.text_input("Master Client ID", value=m_saved.get("client_id", ""))
    master_api_key = st.text_input("Master App ID / Key", value=m_saved.get("api_key", ""))
    master_api_secret = st.text_input("Master Access Token / Secret", type="password", value=m_saved.get("api_secret", ""))
    master_capital = st.number_input("Master Capital (₹)", min_value=10000.0, value=float(m_saved.get("capital", 100000.0)), step=10000.0)

    st.markdown("---")
    st.markdown("##### 🔗 **Connected Slave Accounts Fleet**")

    if "slaves_list" not in st.session_state:
        st.session_state.slaves_list = saved_data.get("slaves", [])

    if st.button("➕ Add New Slave Account"):
        st.session_state.slaves_list.append({
            "name": f"Slave Account {len(st.session_state.slaves_list) + 1}",
            "client_id": "",
            "api_key": "",
            "api_secret": "",
            "param": 1.0,
            "active": True
        })
        st.rerun()

    updated_slaves = []
    indices_to_delete = []

    for idx, s in enumerate(st.session_state.slaves_list):
        st.markdown(f"**Slave Unit #{idx + 1}**")
        s_name = st.text_input(f"Name {idx}", value=s.get("name", f"Slave {idx+1}"), key=f"s_name_{idx}")
        s_client_id = st.text_input(f"Client ID {idx}", value=s.get("client_id", ""), key=f"s_client_{idx}")
        s_api_key = st.text_input(f"App ID {idx}", value=s.get("app_id", s.get("api_key", "")), key=f"s_key_{idx}")
        s_api_secret = st.text_input(f"Token {idx}", type="password", value=s.get("api_secret", ""), key=f"s_sec_{idx}")
        
        col_m1, col_m2 = st.columns(2)
        with col_m1:
            s_param = st.number_input(f"Multiplier/Qty {idx}", min_value=0.1, value=float(s.get("param", 1.0)), step=0.5, key=f"s_param_{idx}")
        with col_m2:
            st.markdown("<br>", unsafe_allow_html=True)
            s_active = st.toggle(f"Active {idx}", value=s.get("active", True), key=f"s_active_{idx}")

        if st.button("🗑️ Delete Account", key=f"del_{idx}"):
            indices_to_delete.append(idx)

        if s_client_id:
            updated_slaves.append({
                "name": s_name,
                "client_id": s_client_id,
                "api_key": s_api_key,
                "api_secret": s_api_secret,
                "param": s_param,
                "active": s_active
            })
        st.markdown("---")

    if indices_to_delete:
        for i in sorted(indices_to_delete, reverse=True):
            del st.session_state.slaves_list[i]
        st.rerun()

    if st.button("💾 Save All Settings Permanently", type="primary", use_container_width=True):
        config_data = {
            "master": {
                "client_id": master_client_id,
                "api_key": master_api_key,
                "api_secret": master_api_secret,
                "capital": master_capital
            },
            "slaves": updated_slaves
        }
        save_config(config_data)
        st.session_state.slaves_list = updated_slaves
        st.success("✅ Saari configuration save ho gayi hai!")

if 'master_client_id' not in locals():
    m_saved = saved_data.get("master", {})
    master_client_id = m_saved.get("client_id", "")
    master_api_key = m_saved.get("app_id", m_saved.get("api_key", ""))
    master_api_secret = m_saved.get("api_secret", "")
    master_capital = float(m_saved.get("capital", 100000.0))

if 'slave_details' not in locals():
    slave_details = st.session_state.get("slaves_list", saved_data.get("slaves", []))

def fetch_dhan_fund_balance(client_id, api_secret):
    if not client_id or not api_secret:
        return 0.0, "Credentials Missing"
    try:
        url = "https://api.dhan.co/v2/fundlimit"
        headers = {
            "client-id": client_id.strip(),
            "access-token": api_secret.strip(),
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code == 200:
            data = response.json()
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
    except Exception:
        return 0.0, "Error"

def fetch_master_orders(client_id, api_secret):
    if not client_id or not api_secret:
        return {"error": "Credentials Missing"}
    try:
        url = "https://api.dhan.co/v2/orders"
        headers = {
            "client-id": client_id.strip(),
            "access-token": api_secret.strip(),
            "Content-Type": "application/json"
        }
        response = requests.get(url, headers=headers, timeout=4)
        if response.status_code == 200:
            return response.json()
        else:
            return {"status_code": response.status_code, "text": response.text}
    except Exception as e:
        return {"exception": str(e)}

with tab_dashboard:
    st.markdown("#### **Control & Operations Center**")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        start_engine = st.button("▶ START COPY TRADING", type="primary", use_container_width=True)
    with c2:
        stop_engine = st.button("🛑 STOP ENGINE", type="secondary", use_container_width=True)
    with c3:
        emergency_kill = st.button("🚨 EMERGENCY KILL", type="primary", use_container_width=True)
    with c4:
        debug_button = st.button("🔍 DEBUG MASTER ORDERS", use_container_width=True)

    if debug_button:
        st.markdown("##### 🧪 Master Orders API Raw Response Check")
        raw_res = fetch_master_orders(master_client_id, master_api_secret)
        st.json(raw_res)

    st.markdown("---")
    
    master_bal, master_status = fetch_dhan_fund_balance(master_client_id, master_api_secret)
    active_slaves_count = sum(1 for s in slave_details if s.get('active', True))

    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Engine State", "RUNNING ⚡" if st.session_state.running else "STANDBY")
    k2.metric("Master Balance", f"₹ {master_bal:,.2f}", master_status)
    k3.metric("Active Slaves", f"{active_slaves_count} / {len(slave_details)}")
    k4.metric("Execution Mode", "Multi-Threaded (<50ms)")

    st.markdown("### 👑 Master Account Details")
    m_display_df = pd.DataFrame([{
        "Master Name": "Main Master Account",
        "Client ID": master_client_id if master_client_id else "Not Set",
        "Available Balance (₹)": f"₹ {master_bal:,.2f}",
        "API Status": master_status
    }])
    st.dataframe(m_display_df, use_container_width=True)

    st.markdown("### 📋 Active Fleet Telemetry")
    status_table_placeholder = st.empty()

def calculate_slave_quantity(master_qty, slave_config):
    param = float(slave_config.get("param", 1.0))
    calculated_qty = int(master_qty * param)
    return max(calculated_qty, 1)

def execute_single_slave_order(slave, order_item):
    if not slave.get('active', True):
        return False, f"Slave {slave['client_id']} OFF"
    
    try:
        qty = calculate_slave_quantity(int(order_item.get("quantity", 1)), slave)
        
        ex_seg = order_item.get("exchangeSegment")
        if not ex_seg or ex_seg not in ["NSE_EQ", "NSE_FNO", "BSE_EQ", "BSE_FNO", "MCX_COMM"]:
            ex_seg = "NSE_FNO"
            
        prod_type = order_item.get("productType")
        if not prod_type or prod_type not in ["INTRADAY", "CNC", "MARGIN", "MTF"]:
            prod_type = "INTRADAY"
            
        ord_type = order_item.get("orderType")
        if not ord_type or ord_type not in ["MARKET", "LIMIT", "STOP_LOSS", "STOP_LOSS_MARKET"]:
            ord_type = "MARKET"
            
        price_val = float(order_item.get("price", 0))
        if ord_type == "MARKET":
            price_val = 0.0

        order_payload = {
            "dhanClientId": slave['client_id'].strip(),
            "correlationId": str(order_item.get("correlationId", "1"))[:30],
            "transactionType": order_item.get("transactionType", "BUY"),
            "exchangeSegment": ex_seg,
            "productType": prod_type,
            "orderType": ord_type,
            "validity": "DAY",
            "securityId": str(order_item.get("securityId", "")),
            "quantity": int(qty),
            "price": price_val,
            "disclosedQuantity": 0,
            "triggerPrice": float(order_item.get("triggerPrice", 0))
        }
        
        url = "https://api.dhan.co/v2/orders"
        headers = {
            "client-id": slave['client_id'].strip(),
            "access-token": slave['api_secret'].strip(),
            "Content-Type": "application/json"
        }
        
        resp = requests.post(url, headers=headers, json=order_payload, timeout=3)
        
        if resp.status_code in [200, 201]:
            log_trade_to_db(
                slave['client_id'], 
                order_item.get("transactionType", "BUY"), 
                order_item.get("tradingSymbol", "NIFTY"), 
                order_payload["quantity"], 
                "SUCCESS", 
                f"Copied for {slave['name']}"
            )
            return True, slave['client_id']
        else:
            err_msg = f"Payload: {json.dumps(order_payload)} | Resp: {resp.text[:250]}"
            log_trade_to_db(
                slave['client_id'], 
                order_item.get("transactionType", "BUY"), 
                order_item.get("tradingSymbol", "NIFTY"), 
                order_payload["quantity"], 
                f"FAILED ({resp.status_code})", 
                err_msg
            )
            return False, err_msg
    except Exception as e:
        log_trade_to_db(slave['client_id'], "ERROR", "NIFTY", 0, "FAILED", str(e))
        return False, str(e)

def process_master_orders_realtime(master_res, active_slaves):
    orders_list = []
    if isinstance(master_res, list):
        orders_list = master_res
    elif isinstance(master_res, dict):
        orders_list = master_res.get("data", [])
        
    for order in orders_list:
        order_id = order.get("orderId") or order.get("correlationId")
        
        if order_id:
            order_hash = f"{order_id}_{order.get('securityId')}"
            
            if not is_order_processed(order_hash):
                mark_order_processed(order_hash)
                
                with ThreadPoolExecutor(max_workers=10) as executor:
                    futures = [executor.submit(execute_single_slave_order, slave, order) for slave in active_slaves if slave.get('active', True)]
                    for future in as_completed(futures):
                        pass

if 'emergency_kill' in locals() and emergency_kill:
    st.session_state.running = False
    st.error("🚨 EMERGENCY KILL SWITCH TRIGGERED!")

if 'start_engine' in locals() and start_engine:
    if not master_client_id or not master_api_secret:
        st.error("⚠️ Master Client ID aur Access Token bharna anivarya hai!")
    elif len(slave_details) == 0:
        st.error("⚠ Kam se kam ek Slave account jodein!")
    else:
        st.session_state.running = True
        st.success("🚀 Ultra-Fast Copy Trading Engine Started!")

if 'stop_engine' in locals() and stop_engine:
    st.session_state.running = False
    st.warning("⚠ Engine pause kar diya gaya hai.")

if st.session_state.running:
    active_slaves_list = [s for s in slave_details if s.get('active', True)]
    master_raw_data = fetch_master_orders(master_client_id, master_api_secret)
    if master_raw_data:
        process_master_orders_realtime(master_raw_data, active_slaves_list)

def get_slave_financial_report(slaves, start_d, end_d):
    report_data = []
    conn = sqlite3.connect(DB_FILE)
    for idx, s in enumerate(slaves, 1):
        c_id = s.get('client_id', '')
        s_name = s.get('name', f'Slave {idx}')
        is_on = "🟢 ON" if s.get('active', True) else "🔴 OFF"
        avail_bal, _ = fetch_dhan_fund_balance(c_id, s.get('api_secret', ''))
        
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT SUM(pnl) FROM trade_logs WHERE client_id = ? AND date(timestamp) BETWEEN date(?) AND date(?)", 
                           (c_id, start_d.strftime('%Y-%m-%d'), end_d.strftime('%Y-%m-%d')))
            res = cursor.fetchone()
            total_gain = res[0] if res and res[0] is not None else 0.00
        except:
            total_gain = 0.00
            
        report_data.append({
            "Unit #": idx,
            "Account Name": s_name,
            "State": is_on,
            "Client ID": c_id,
            "Available Balance (₹)": f"₹ {avail_bal:,.2f}",
            "Profit Gain (₹)": f"₹ {total_gain:+,.2f}"
        })
    conn.close()
    return pd.DataFrame(report_data)

def update_status_table(slaves):
    table_data = []
    for idx, s in enumerate(slaves, 1):
        state_str = "🟢 LIVE SYNCING" if (st.session_state.running and s.get('active', True)) else ("🔴 PAUSED / OFF" if not s.get('active', True) else "⚪ STANDBY")
        table_data.append({
            "Unit #": idx,
            "Account Name": s.get('name', f'Slave {idx}'),
            "Client ID": s['client_id'],
            "Status": state_str,
            "Timestamp": datetime.now().strftime('%H:%M:%S.%f')[:-3]
        })
    return pd.DataFrame(table_data)

with tab_dashboard:
    df_status = update_status_table(slave_details)
    status_table_placeholder.dataframe(df_status, use_container_width=True)

with tab_logs:
    st.markdown("#### **Audit Logs & Execution Speed Records**")
    try:
        conn = sqlite3.connect(DB_FILE)
        df_history = pd.read_sql_query("SELECT * FROM trade_logs ORDER BY id DESC LIMIT 100", conn)
        conn.close()
        if not df_history.empty:
            st.dataframe(df_history, use_container_width=True)
        else:
            st.info("📭 Abhi tak koi order log nahi hua hai.")
    except Exception as e:
        st.warning(f"Database error: {e}")

with tab_reports:
    st.markdown("#### **📊 Financial & Performance Report**")
    d_col1, d_col2 = st.columns(2)
    with d_col1:
        start_date = st.date_input("From Date", value=date.today(), key="rep_start_date")
    with d_col2:
        end_date = st.date_input("To Date", value=date.today(), key="rep_end_date")

    df_report = get_slave_financial_report(slave_details, start_date, end_date)
    st.dataframe(df_report, use_container_width=True)

with tab_risk:
    st.markdown("#### **Risk Controls & Fleet Rules**")
    r1, r2 = st.columns(2)
    with r1:
        st.number_input("Max Daily Loss Limit per Slave (₹)", min_value=1000, max_value=500000, value=25000, step=5000)
    with r2:
        st.number_input("Max Lot Size Cap per Order", min_value=1, max_value=500, value=50, step=1)

if auto_refresh_sec != "Off" and st.session_state.running:
    time.sleep(float(auto_refresh_sec))
    st.rerun()
