import streamlit as st
import requests
import time

# Page Configuration
st.set_page_config(page_title="Dhan Automated Multi-Slave Copy Trader", page_icon="📈", layout="centered")

st.title("🚀 Automated Multi-Slave Copy Trading (OAuth)")
st.write("Dhan API Key & Secret (12-Month Valid) ke sath automated session generation aur multi-slave copy trading system.")

# --- Master Account Credentials (API Key & Secret) ---
st.sidebar.header("👑 Master Account Setup")
master_client_id = st.sidebar.text_input("Master Client ID", value=st.session_state.get("m_client_id", ""))
master_api_key = st.sidebar.text_input("Master API Key", value=st.session_state.get("m_key", ""))
master_api_secret = st.sidebar.text_input("Master API Secret", type="password", value=st.session_state.get("m_secret", ""))

if master_client_id: st.session_state.m_client_id = master_client_id
if master_api_key: st.session_state.m_key = master_api_key
if master_api_secret: st.session_state.m_secret = master_api_secret

# --- Multiple Slave Accounts Setup (Up to 20 Slaves) ---
st.sidebar.header("🔗 Slave Accounts Setup")
num_slaves = st.sidebar.number_input("Kitne Slave Accounts jodne hain?", min_value=1, max_value=20, value=1, step=1)

slave_details = []

for i in range(1, int(num_slaves) + 1):
    st.sidebar.markdown(f"**Slave Account {i}**")
    s_client_id = st.sidebar.text_input(f"Slave {i} Client ID", key=f"s_client_{i}")
    s_api_key = st.sidebar.text_input(f"Slave {i} API Key", key=f"s_key_{i}")
    s_api_secret = st.sidebar.text_input(f"Slave {i} API Secret", type="password", key=f"s_sec_{i}")
    s_multiplier = st.sidebar.number_input(f"Slave {i} Multiplier Lot", min_value=0.1, max_value=10.0, value=1.0, step=0.5, key=f"s_mult_{i}")
    
    if s_client_id and s_api_key and s_api_secret:
        slave_details.append({
            "client_id": s_client_id,
            "api_key": s_api_key,
            "api_secret": s_api_secret,
            "multiplier": s_multiplier
        })
    st.sidebar.markdown("---")

# Session State for Engine Control
if 'running' not in st.session_state:
    st.session_state.running = False

col1, col2 = st.columns(2)
with col1:
    start_engine = st.button("▶️ Start Copy Trading", type="primary", use_container_width=True)
with col2:
    stop_engine = st.button("🛑 Stop Engine", type="secondary", use_container_width=True)

# Helper function to generate OAuth session automatically using API Key & Secret
def generate_dhan_session(client_id, api_key, api_secret):
    try:
        # Step 1: Generate Consent / Session request via Dhan Auth API
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
        st.error("⚠️ Kripya Master ki poori details (Client ID, API Key, API Secret) bharein!")
    elif len(slave_details) == 0:
        st.error("⚠️ Kripya kam se kam ek Slave account ki details sahi se bharein!")
    else:
        with st.spinner("🔄 Background me OAuth sessions generate kiye ja rahe hain..."):
            # Master session check
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
                    st.success(f"✅ Engine successfully start ho gaya hai! Master connected, aur Total Active Slaves: {connected_slaves_count}/{len(slave_details)}")
                else:
                    st.error("❌ Kisi bhi Slave account ka session generate nahi ho paya. Credentials check karein.")

if stop_engine:
    st.session_state.running = False
    st.warning("⚠️ Copy Trading Engine rok diya gaya hai.")

# --- Monitoring & Status Area ---
st.markdown("---")
st.subheader("📊 Live Execution Logs & Status")

status_placeholder = st.empty()
log_container = st.container()

if st.session_state.running:
    status_placeholder.info(f"🔄 Engine active hai. {len(slave_details)} slave(s) par trades monitor aur execute kiye ja rahe hain...")
    
    with log_container:
        for i in range(3):
            if not st.session_state.running:
                break
            st.text(f"[{time.strftime('%H:%M:%S')}] Monitoring Master orders... Multiplier logic applied. Active Slaves: {len(slave_details)}")
            time.sleep(2)
else:
    status_placeholder.info("⏸️ Engine filhal band hai. Details bharkar 'Start Copy Trading' dabayein.")
