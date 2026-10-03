import streamlit as st
import requests
import time

st.set_page_config(page_title="Mobile Copy Trader", page_icon="📈", layout="centered")

st.title("📱 Mobile Copy Trading")
st.write("Dhan API ke through apne trades ko mobile se control karein.")

# Inputs for Credentials
st.sidebar.header("🔑 Credentials")
master_id = st.sidebar.text_input("Master Client ID")
master_token = st.sidebar.text_input("Master Access Token", type="password")

slave_id = st.sidebar.text_input("Slave Client ID")
slave_token = st.sidebar.text_input("Slave Access Token", type="password")

multiplier = st.sidebar.number_input("Multiplier", value=1.0, min_value=0.1)

if 'running' not in st.session_state:
    st.session_state.running = False

col1, col2 = st.columns(2)
with col1:
    if st.button("▶️ Start", type="primary", use_container_width=True):
        if not master_id or not slave_id:
            st.error("Details bharein!")
        else:
            st.session_state.running = True
            st.success("Engine Started!")

with col2:
    if st.button("🛑 Stop", type="secondary", use_container_width=True):
        st.session_state.running = False
        st.warning("Engine Stopped.")

st.markdown("---")
status_box = st.empty()

if st.session_state.running:
    status_box.info("🔄 Engine background me active hai...")
    # Yeh loop mobile par status dikhata rahega
    for _ in range(3):
        if not st.session_state.running:
            break
        time.sleep(2)
else:
    status_box.info("⏸️ Engine band hai. Start dabayein.")