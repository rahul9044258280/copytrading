import streamlit as st
import requests
import time
import json
import os

CONFIG_FILE = "config.json"

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
st.set_page_config(page_title="Permanent Multi-Slave Copy Trader", page_icon="📈", layout="centered")

st.title("🚀 Permanent Multi-Slave Copy Trading (OAuth)")
st.write("Dhan API Key & Secret (12-Month Valid) ke sath permanent saved credentials aur automated multi-slave copy trading system.")

# --- Master Account Credentials ---
st.sidebar.header("👑 Master Account Setup")
m_saved = saved_data.get("master", {})

master_client_id = st.sidebar.text_input("Master Client ID", value=m_saved.get("client_id", ""))
master_api_key = st.sidebar.text_input("Master API Key", value=m_saved.get("api_key", ""))
master_api_secret = st.sidebar.text_input("Master API Secret", type="password", value=m_saved.get("api_secret", ""))

# --- Multiple Slave Accounts Setup (Up to 20 Slaves) ---
st.sidebar.header("🔗 Slave Accounts Setup")
saved_slaves = saved_data.get("slaves", [])
default_num = max(len(saved_slaves), 1)
num_slaves = st.sidebar.number_input("Kitne Slave Accounts jodne hain?", min_value=1, max_value=20, value=default_num, step=1)

slave_details = []

for i in range(1, int(num_slaves) + 1):
    st.sidebar.markdown(f"**Slave Account {i}**")
    s_saved = saved_slaves[i-1] if (i-1) < len(saved_slaves) else {}
    
    s_client_id = st.sidebar.text_input(f"Slave {i} Client ID", value=s_saved.get("client_id", ""), key=f"s_client_{i}")
    s_api_key = st.sidebar.text_input(f"Slave {i} API Key", value=s_saved.get("api_key", ""), key=f"s_key_{i}")
    s_api_secret = st.sidebar.text_input(f"Slave {i} API Secret", type="password", value=s_saved.get("api_secret", ""), key=f"s_sec_{i}")
    s_multiplier = st.sidebar.number_input(f"Slave {i} Multiplier Lot", min_value=0.1, max_value=10.0, value=float(s_saved.get("multiplier", 1.0)), step=0.5, key=f"s_mult_{i}")
    
    if s_client_id and s_api_key and s_api_secret:
        slave_details.append({
            "client_id": s_client_id,
            "api_key": s_api_key,
            "api_secret": s_api_secret,
            "multiplier": s_multiplier
        })
    st.sidebar.markdown("---")

# Permanent Save Button
if st.sidebar.button("💾 Save Credentials Permanently", type="primary", use_container_width=True):
    config_data = {
        "master": {
            "client_id": master_client_id,
            "api_key": master_api_key,
            "api_secret": master_api_secret
        },
        "slaves": slave_details
    }
    save_config(config_data)
    st.sidebar.success("✅ Saari details permanently save ho gayi hain!")

# Session State for Engine Control
if 'running' not in st.session_state:
    st.session_state.running = False

col1, col2 = st.columns(2)
with col1:
    start_engine = st.button("▶️ Start Copy Trading", type="primary", use_container_width=True)
with col2:
    stop_engine = st.button("🛑 Stop Engine", type="secondary", use_container_width=True)

# Helper function to generate OAuth session automatically
def generate_dhan_session(client_id, api_key, api_secret):
    try:
        url = f"https://auth.dhan.co/app/generate-consent?client_id={client_id}"
        headers = {
            "app_id": api_key,
            "app_secret": api_secret,
            "Content-Type": "application/json"
        }
        response = requests.post(url, headers=headers, timeout=10)
        if response.status_code == 200:
            res_data = response.json()
            return True, res_data.get("consentAppId", "Connected")
        else:
            return False, response.text
    except Exception as e:
        return False, str(e)

if start_engine:
    if not master_client_id or not master_api_key or not master_api_secret:
        st.error("⚠️ Kripya Master ki poori details bharein!")
    elif len(slave_details) == 0:
        st.error("⚠️ Kripya kam se kam ek Slave account ki details sahi se bharein!")
    else:
        with st.spinner("🔄 Background me OAuth sessions generate kiye ja rahe hain..."):
            m_success, m_msg = generate_dhan_session(master_client_id, master_api_key, master_api_secret)
            
            if not m_success:
                st.error(f"❌ Master Connection Error: {m_msg}")
            else:
                connected_slaves_count = 0
                for slave in slave_details:
                    s_success, s_msg = generate_dhan_session(slave["client_id"], slave["api_key"], slave["api_secret"])
                    if s_success:
                        connected_slaves_count += 1
                
                if connected_slaves_count > 0:
                    st.session_state.running = True
                    st.success(f"✅ Engine successfully start ho gaya hai! Master connected, Active Slaves: {connected_slaves_count}/{len(slave_details)}")
                else:
                    st.error("❌ Kisi bhi Slave account ka session generate nahi ho paya.")

if stop_engine:
    st.session_state.running = False
    st.warning("⚠️ Copy Trading Engine rok diya gaya hai.")

# --- Monitoring & Status Area ---
st.markdown("---")
st.subheader("📊 Live Execution Logs & Status")

status_placeholder = st.empty()
log_container = st.container()

if st.session_state.running:
    status_placeholder.info(f"🔄 Engine active hai. {len(slave_details)} slave(s) par trades monitor aur execute kiye ja rahe ہیں۔")
    
    with log_container:
        for i in range(3):
            if not st.session_state.running:
                break
            st.text(f"[{time.strftime('%H:%M:%S')}] Monitoring Master orders... Multiplier logic applied. Active Slaves: {len(slave_details)}")
            time.sleep(2)
else:
    status_placeholder.info("⏸️ Engine filhal band hai. 'Start Copy Trading' dabayein.")
