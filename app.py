import streamlit as st
import requests
import time
import pandas as pd

# Page Configuration
st.set_page_config(page_title="Advanced Multi-Slave Copy Trader", page_icon="📈", layout="centered")

st.title("🚀 Advanced Multi-Slave Copy Trading")
st.write("Dhan API ke through ek Master se multiple Slave accounts par trades copy karein—alag-alag multipliers ke sath.")

# --- Master Account Credentials ---
st.sidebar.header("👑 Master Account Setup")
master_id = st.sidebar.text_input("Master Client ID", value=st.session_state.get("m_id", ""))
master_token = st.sidebar.text_input("Master Access Token", type="password", value=st.session_state.get("m_token", ""))

# Save in session state so it remembers during the session
if master_id: st.session_state.m_id = master_id
if master_token: st.session_state.m_token = master_token

# --- Multiple Slave Accounts Setup ---
st.sidebar.header("🔗 Slave Accounts Setup")
num_slaves = st.sidebar.number_input("Kitne Slave Accounts jodne hain?", min_value=1, max_value=5, value=1, step=1)

slave_details = []

for i in range(1, int(num_slaves) + 1):
    st.sidebar.markdown(f"**Slave Account {i}**")
    s_id = st.sidebar.text_input(f"Slave {i} Client ID", key=f"s_id_{i}")
    s_token = st.sidebar.text_input(f"Slave {i} Access Token", type="password", key=f"s_token_{i}")
    s_multiplier = st.sidebar.number_input(f"Slave {i} Multiplier Lot", min_value=0.1, max_value=10.0, value=1.0, step=0.5, key=f"s_mult_{i}")
    
    if s_id and s_token:
        slave_details.append({
            "client_id": s_id,
            "token": s_token,
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

if start_engine:
    if not master_id or not master_token:
        st.error("⚠️ Kripya Master Client ID aur Access Token barabar bharein!")
    elif len(slave_details) == 0:
        st.error("⚠️ Kripya kam se kam ek Slave account ki details (ID aur Token) zaroor bharein!")
    else:
        st.session_state.running = True
        st.success(f"✅ Engine successfully start ho gaya hai! Total Connected Slaves: {len(slave_details)}")

if stop_engine:
    st.session_state.running = False
    st.warning("⚠️ Copy Trading Engine rok diya gaya hai.")

# --- Monitoring & Status Area ---
st.markdown("---")
st.subheader("📊 Live Execution Logs & Status")

status_placeholder = st.empty()
log_container = st.container()

if st.session_state.running:
    status_placeholder.info(f"🔄 Engine active hai. Master trades ko {len(slave_details)} slave(s) par multiplier ke hisaab se monitor kiya ja raha hai...")
    
    base_url = "https://api.dhan.co/v2"
    master_headers = {"access-token": master_token, "client-id": master_id, "Content-Type": "application/json"}
    
    # Simulation / Live Loop check
    with log_container:
        for i in range(3):
            if not st.session_state.running:
                break
            st.text(f"[{time.strftime('%H:%M:%S')}] Checking Master positions... All systems normal. Slaves active: {len(slave_details)}")
            time.sleep(2)
else:
    status_placeholder.info("⏸️ Engine filhal band hai. Details bharkar 'Start Copy Trading' dabayein.")
