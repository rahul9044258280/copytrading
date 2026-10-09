import streamlit as st
import asyncio
import aiohttp
import time
import logging

# Logging configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- STREAMLIT PAGE CONFIGURATION ---
st.set_page_config(page_title="Pro Copy Trading Terminal", layout="wide", initial_sidebar_state="expanded")

# --- DARK CINEMATIC GROWW-INSPIRED STYLING ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }
    .metric-card {
        background-color: #1f2937;
        border: 1px solid #374151;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
    }
    .stButton>button {
        width: 100%;
        background-color: #10b981;
        color: white;
        font-weight: bold;
        border-radius: 6px;
        border: none;
        padding: 10px;
    }
    .stButton>button:hover {
        background-color: #059669;
    }
    </style>
""", unsafe_allow_html=True)

# --- ASYNC BATCH COPY TRADING ENGINE ---
class CopyTradingEngine:
    def __init__(self, batch_size=100, delay_between_batches=0.2):
        self.batch_size = batch_size  # Ek baar me kitne clients ko hit karna hai
        self.delay = delay_between_batches  # Batches ke beech ka gap (seconds)

    async def place_single_order(self, session, client_cred, order_payload):
        """
        Individual client ke liye async API request bhejta hai.
        """
        # Note: Live deployment par yahan Angel One / Broker ka actual endpoint aayega
        url = "https://apiconnect.angelbroking.com/rest/secure/angelbroking/order/v1/placeOrder"
        headers = {
            "Authorization": f"Bearer {client_cred['auth_token']}",
            "Content-Type": "application/json",
            "X-PrivateKey": client_cred['api_key']
        }
        
        try:
            # Paper trading simulation mode check (agar token dummy hai toh success simulate karega)
            if "dummy" in client_cred['auth_token']:
                await asyncio.sleep(0.05) # Network latency simulate karne ke liye
                return {"client_id": client_cred['client_id'], "status": "SUCCESS", "response": {"message": "Paper Trade Executed Successfully"}}

            async with session.post(url, json=order_payload, headers=headers, timeout=5) as response:
                result = await response.json()
                if response.status == 200 and result.get("status") == True:
                    return {"client_id": client_cred['client_id'], "status": "SUCCESS", "response": result}
                else:
                    return {"client_id": client_cred['client_id'], "status": "FAILED", "response": result}
        except Exception as e:
            return {"client_id": client_cred['client_id'], "status": "ERROR", "response": str(e)}

    async def execute_copy_trade_for_all(self, clients_list, order_payload):
        """
        1000+ clients ke liye batches banakar async requests fire karta hai.
        """
        start_time = time.time()
        success_count = 0
        failed_count = 0
        logs = []

        async with aiohttp.ClientSession() as session:
            for i in range(0, len(clients_list), self.batch_size):
                batch = clients_list[i:i + self.batch_size]
                
                # Batch ke liye saari tasks ek sath create karo
                tasks = [self.place_single_order(session, client, order_payload) for client in batch]
                results = await asyncio.gather(*tasks)
                
                for res in results:
                    if res['status'] == 'SUCCESS':
                        success_count += 1
                    else:
                        failed_count += 1
                        logs.append(f"Client {res['client_id']} Error: {res['response']}")
                
                # Broker rate limit se bachne ke liye chhota sa delay
                if i + self.batch_size < len(clients_list):
                    await asyncio.sleep(self.delay)

        end_time = time.time()
        total_time = end_time - start_time
        return success_count, failed_count, total_time, logs


# --- STREAMLIT USER INTERFACE ---
st.title("⚡ Pro Multi-Account Copy Trading Terminal")
st.markdown("---")

# Sidebar for Configuration
st.sidebar.header("⚙️ Terminal Settings")
total_simulated_clients = st.sidebar.number_input("Total Clients to Simulate", min_value=1, max_value=5000, value=1000)
batch_size_input = st.sidebar.slider("Batch Size (Clients per hit)", min_value=10, max_value=500, value=100)
batch_delay_input = st.sidebar.slider("Batch Delay (Seconds)", min_value=0.0, max_value=1.0, value=0.2, step=0.05)

# Main Dashboard Layout
col1, col2, col3 = st.columns(3)
with col1:
    st.markdown('<div class="metric-card"><h3>Total Target</h3><h2>{} Accounts</h2></div>'.format(total_simulated_clients), unsafe_allow_html=True)
with col2:
    st.markdown('<div class="metric-card"><h3>Batch Mode</h3><h2>{} / batch</h2></div>'.format(batch_size_input), unsafe_allow_html=True)
with col3:
    st.markdown('<div class="metric-card"><h3>System Status</h3><h2 style="color: #10b981;">Ready (Paper Mode)</h2></div>', unsafe_allow_html=True)

st.markdown("### 📋 Master Order Execution Panel")

with st.form("order_form"):
    f_col1, f_col2, f_col3 = st.columns(3)
    with f_col1:
        symbol = st.selectbox("Trading Symbol", ["NIFTY", "BANKNIFTY", "FINNIFTY", "RELIANCE", "TATASTEEL"])
    with f_col2:
        action = st.radio("Transaction Type", ["BUY", "SELL"], horizontal=True)
    with f_col3:
        quantity = st.number_input("Lot / Quantity", min_value=1, value=15)

    order_type = st.selectbox("Order Type", ["MARKET", "LIMIT"])
    
    # Submit Button
    submitted = st.form_submit_button("🚀 Execute Trade Across All Accounts")

if submitted:
    # 1. Dummy Client List generate karna (Aapke 1000+ accounts ke liye)
    clients = [
        {"client_id": f"CUST_{i:04d}", "auth_token": "dummy_token_xyz", "api_key": "dummy_api_key"}
        for i in range(1, total_simulated_clients + 1)
    ]

    # 2. Payload prepare karna
    payload = {
        "tradingsymbol": symbol,
        "transactiontype": action,
        "quantity": str(quantity),
        "ordertype": order_type,
        "producttype": "INTRADAY"
    }

    # 3. Progress bar aur status text
    progress_text = st.empty()
    progress_bar = st.progress(0)
    progress_text.text("Executing async batches across accounts...")

    # 4. Engine Run Karna
    engine = CopyTradingEngine(batch_size=batch_size_input, delay_between_batches=batch_delay_input)
    
    # Run async loop inside Streamlit
    success, failed, time_taken, error_logs = asyncio.run(engine.execute_copy_trade_for_all(clients, payload))

    progress_bar.progress(100)
    progress_text.text("Execution Completed!")

    # 5. Results Display
    st.markdown("---")
    st.subheader("📊 Execution Report")
    
    r_col1, r_col2, r_col3 = st.columns(3)
    r_col1.metric("Successful Trades", f"{success} / {total_simulated_clients}", delta="100% Success" if failed == 0 else f"-{failed} Failed")
    r_col2.metric("Failed Trades", f"{failed}")
    r_col3.metric("Total Time Taken", f"{time_taken:.2f} seconds")

    if error_logs:
        with st.expander("🔍 View Error Logs"):
            for log in error_logs[:50]: # First 50 errors dikhane ke liye
                st.error(log)
    else:
        st.success("🎉 Sabhi accounts me trade bina kisi error ke successfully place ho gaye!")
