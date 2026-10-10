import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Ultra-Fast Milliseconds Intraday Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CINEMATIC DARK HIGH-SPEED UI STYLING ---
st.markdown("""
    <style>
    .stApp {
        background-color: #080c14;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Glow Status Bar */
    .speed-badge {
        background: linear-gradient(90deg, #10b981 0%, #3b82f6 100%);
        color: #ffffff;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.5px;
        box-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }

    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        font-weight: 700;
        border-radius: 8px;
        border: none;
        padding: 12px;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.4);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
        box-shadow: 0 6px 20px rgba(16, 185, 129, 0.7);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #0f172a;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #1e293b;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1e293b !important;
        color: #10b981 !important;
        border: 1px solid #334155;
    }
    </style>
""", unsafe_allow_html=True)

# --- BROAD SECTOR & NIFTY UNIVERSE ---
SECTOR_MAP = {
    "IT": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "MPHASIS.NS", "COFORGE.NS"],
    "Banking & Finance": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS"],
    "Auto": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS"],
    "Pharma": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "LUPIN.NS", "ALKEM.NS"],
    "Energy & Oil": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "POWERGRID.NS", "NTPC.NS", "TATAPOWER.NS"],
    "Metal & Infra": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "GRASIM.NS", "ADANIENT.NS", "LT.NS"]
}

# --- SINGLE STOCK FAST FETCH FUNCTION ---
def fetch_single_ticker(ticker):
    try:
        stock = yf.Ticker(ticker)
        hist = stock.history(period="2d")
        if len(hist) >= 2:
            prev_close = hist['Close'].iloc[-2]
            curr_price = hist['Close'].iloc[-1]
            change_pct = ((curr_price - prev_close) / prev_close) * 100
            volume = hist['Volume'].iloc[-1]
            
            return {
                "Symbol": ticker.replace(".NS", ""),
                "LTP": round(curr_price, 2),
                "Change (%)": round(change_pct, 2),
                "Volume": volume,
                "Prev Close": round(prev_close, 2)
            }
    except Exception:
        return None

# --- MULTI-THREADED ULTRA FAST SCANNER ENGINE ---
def fast_parallel_scan(tickers, max_workers=30):
    start_time = time.time()
    
    # Executing HTTP requests in parallel threads
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        results = list(executor.map(fetch_single_ticker, tickers))
    
    # Filter out None values
    valid_data = [res for res in results if res is not None]
    
    execution_ms = round((time.time() - start_time) * 1000, 2)
    return pd.DataFrame(valid_data), execution_ms


# --- SIDEBAR CONTROL PANEL ---
with st.sidebar:
    st.markdown("### ⚡ Fast Scanning Engine")
    st.markdown("---")
    max_threads = st.slider("Parallel Threads Count", min_value=10, max_value=50, value=30)
    st.info(f"Currently running with **{max_threads} concurrent threads** for near-zero latency.")
    st.markdown("---")
    st.caption("Engine: Ultra Parallel Async Core")

# --- HEADER SECTION ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("⚡ Ultra-Fast Intraday Terminal")
    st.markdown("Parallel Multi-Threaded Real-Time Scanner with Millisecond Processing.")
with col_h2:
    st.markdown(
        f"<div style='text-align: right;'><span class='speed-badge'>⚡ SPEED: MULTI-THREADED</span><br>"
        f"<span style='font-size: 11px; color: #9ca3af;'>{datetime.now().strftime('%H:%M:%S')} IST</span></div>", 
        unsafe_allow_html=True
    )

st.markdown("---")

# --- TABS SETUP ---
tab1, tab2, tab3 = st.tabs(["📌 1. Sector Matrix", "📂 2. Stocks by Sector", "🔥 3. Instant Gainers & Losers"])

# --- TAB 1: SECTOR MATRIX ---
with tab1:
    col_t1, col_t2 = st.columns([4, 1])
    with col_t1:
        st.subheader("Sector Momentum Pulse")
    with col_t2:
        refresh_sec = st.button("🚀 Fast Refresh All")

    all_tickers = [t for sublist in SECTOR_MAP.values() for t in sublist]
    
    with st.spinner("Executing parallel multi-threaded scan..."):
        master_df, speed_ms = fast_parallel_scan(all_tickers, max_workers=max_threads)

    if not master_df.empty:
        st.success(f"⚡ Full scan completed in **{speed_ms} ms** across all sectors!")
        
        # Sector averages calculation
        sector_summary = []
        for sector, tickers in SECTOR_MAP.items():
            clean_tickers = [t.replace(".NS", "") for t in tickers]
            sec_stocks = master_df[master_df["Symbol"].isin(clean_tickers)]
            if not sec_stocks.empty:
                avg_chg = sec_stocks["Change (%)"].mean()
                sector_summary.append({
                    "Sector": sector,
                    "Avg Change (%)": round(avg_chg, 2),
                    "Stocks Tracked": len(sec_stocks)
                })
        
        sec_df = pd.DataFrame(sector_summary).sort_values(by="Avg Change (%)", ascending=False)
        st.dataframe(sec_df, use_container_width=True, hide_index=True)

# --- TAB 2: STOCKS BY SECTOR ---
with tab2:
    st.subheader("Granular Sector Stock Inspector")
    selected_sector = st.selectbox("Select Target Sector", list(SECTOR_MAP.keys()))
    
    if selected_sector:
        sector_tickers = SECTOR_MAP[selected_sector]
        with st.spinner(f"Instant fetching stocks for {selected_sector}..."):
            sec_df, sec_speed = fast_parallel_scan(sector_tickers, max_workers=max_threads)
        
        if not sec_df.empty:
            st.caption(f"Fetched in {sec_speed} ms")
            st.dataframe(sec_df.sort_values(by="Change (%)", ascending=False), use_container_width=True, hide_index=True)

# --- TAB 3: INSTANT GAINERS & LOSERS ---
with tab3:
    st.subheader("Instant Breakout & Breakdown Scanner")

    if not master_df.empty:
        col_gain, col_loss = st.columns(2)
        
        with col_gain:
            st.markdown("### 🟢 Instant Top Gainers")
            gainers = master_df.sort_values(by="Change (%)", ascending=False).head(5)
            st.dataframe(gainers, use_container_width=True, hide_index=True)
            
        with col_loss:
            st.markdown("### 🔴 Instant Top Losers")
            losers = master_df.sort_values(by="Change (%)", ascending=True).head(5)
            st.dataframe(losers, use_container_width=True, hide_index=True)
