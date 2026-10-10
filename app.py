import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime
import time
from concurrent.futures import ThreadPoolExecutor

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="NSE-Style Interactive Sector & Stock Terminal",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CINEMATIC NSE PROFESSIONAL STYLING ---
st.markdown("""
    <style>
    .stApp {
        background-color: #0b0f19;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Sector Card Styling */
    .sector-card {
        background: #111827;
        border: 1px solid #1f2937;
        padding: 18px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        margin-bottom: 12px;
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        font-weight: 700;
        border-radius: 8px;
        border: none;
        padding: 10px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #111827;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #1f2937;
    }
    .stTabs [aria-selected="true"] {
        background-color: #1f2937 !important;
        color: #10b981 !important;
        border: 1px solid #374151;
    }
    </style>
""", unsafe_allow_html=True)

# --- COMPLETE NSE SECTOR UNIVERSE ---
SECTOR_MAP = {
    "IT & Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "OFSS.NS"],
    "Banking & Financials": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "PNB.NS", "BANKBARODA.NS"],
    "Automobile": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS"],
    "Pharmaceuticals": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "LUPIN.NS", "ALKEM.NS", "TORNTPHARM.NS"],
    "Energy & Oil/Gas": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "POWERGRID.NS", "NTPC.NS", "TATAPOWER.NS", "ADANIGREEN.NS"],
    "Metal & Infrastructure": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "GRASIM.NS", "ADANIENT.NS", "LT.NS", "JINDALSTEL.NS"]
}

# --- FAST SINGLE STOCK FETCHER ---
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

# --- PARALLEL MULTI-THREADED SCANNER ENGINE ---
def run_fast_scan(tickers):
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=30) as executor:
        results = list(executor.map(fetch_single_ticker, tickers))
    valid_data = [res for res in results if res is not None]
    execution_ms = round((time.time() - start_time) * 1000, 2)
    return pd.DataFrame(valid_data), execution_ms

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### 📊 NSE Terminal Panel")
    st.markdown("---")
    if st.button("🔄 Refresh All Markets"):
        st.cache_data.clear()
    st.markdown("---")
    st.info("Click on any sector in the overview tab to instantly load its complete stock portfolio like the official NSE portal.")

# --- APP HEADER ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("📊 NSE Live Sector & Stock Terminal")
    st.markdown("Clickable NSE-Style Sector Performance Matrix with Instant Stock Drill-Down.")
with col_h2:
    st.markdown(f"<div style='text-align: right; color: #10b981; font-weight: 600; padding-top: 10px;'>🟢 LIVE FEED<br><span style='font-size: 11px; color: #9ca3af;'>{datetime.now().strftime('%H:%M:%S')} IST</span></div>", unsafe_allow_html=True)

st.markdown("---")

# --- INITIALIZE SESSION STATE FOR SECTOR CLICK ---
if 'selected_sector_click' not in st.session_state:
    st.session_state.selected_sector_click = list(SECTOR_MAP.keys())[0]

# --- FETCH ALL DATA ONCE FOR SPEED ---
all_tickers = [t for sublist in SECTOR_MAP.values() for t in sublist]
with st.spinner("Scanning market sectors in milliseconds..."):
    master_df, speed_ms = run_fast_scan(all_tickers)

# --- TABS SETUP ---
tab1, tab2, tab3 = st.tabs(["📌 1. NSE Sector Overview", "📂 2. Stocks by Sector (Drill-Down)", "🔥 3. Top Gainers & Losers"])

# --- TAB 1: NSE SECTOR OVERVIEW (CLICKABLE CARDS) ---
with tab1:
    st.subheader("NSE Sector Performance Board (Click to Inspect)")
    st.caption(f"Scan completed in {speed_ms} ms")

    # Calculate Sector Averages
    sector_summary = []
    for sector, tickers in SECTOR_MAP.items():
        clean_tickers = [t.replace(".NS", "") for t in tickers]
        sec_stocks = master_df[master_df["Symbol"].isin(clean_tickers)]
        if not sec_stocks.empty:
            avg_chg = sec_stocks["Change (%)"].mean()
            sector_summary.append({
                "Sector": sector,
                "Avg Change (%)": round(avg_chg, 2),
                "Total Stocks": len(sec_stocks),
                "Gainers": len(sec_stocks[sec_stocks["Change (%)"] > 0]),
                "Losers": len(sec_stocks[sec_stocks["Change (%)"] < 0])
            })
    
    sec_df = pd.DataFrame(sector_summary).sort_values(by="Avg Change (%)", ascending=False)

    if not sec_df.empty:
        # Display in rows of 3 columns like NSE dashboard
        for i in range(0, len(sec_df), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(sec_df):
                    row = sec_df.iloc[i + j]
                    sec_name = row["Sector"]
                    avg_val = row["Avg Change (%)"]
                    color_code = "#10b981" if avg_val >= 0 else "#ef4444"
                    
                    with cols[j]:
                        st.markdown(f"""
                            <div class="sector-card">
                                <h4 style="margin: 0; color: #ffffff;">{sec_name}</h4>
                                <h2 style="margin: 5px 0; color: {color_code};">{avg_val:+.2f}%</h2>
                                <p style="font-size: 12px; color: #9ca3af; margin: 0;">Stocks: {row['Total Stocks']} | 🟢 {row['Gainers']} 🔴 {row['Losers']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Click button to jump to sector stocks
                        if st.button(f"🔍 View {sec_name} Stocks", key=f"btn_{sec_name}"):
                            st.session_state.selected_sector_click = sec_name
                            st.rerun()
    else:
        st.warning("Market data temporarily unavailable.")

# --- TAB 2: STOCKS BY SECTOR (CLICKABLE & FILTERABLE) ---
with tab2:
    st.subheader("📁 Sector Stock Portfolio List")
    
    # Dropdown automatically synced with clicked sector card
    selected_sector = st.selectbox(
        "Select Sector to View All Stocks", 
        list(SECTOR_MAP.keys()), 
        index=list(SECTOR_MAP.keys()).index(st.session_state.selected_sector_click)
    )
    
    # Update state if changed via dropdown manually
    st.session_state.selected_sector_click = selected_sector

    if selected_sector:
        tickers = SECTOR_MAP[selected_sector]
        clean_tickers = [t.replace(".NS", "") for t in tickers]
        sector_stocks_df = master_df[master_df["Symbol"].isin(clean_tickers)]
        
        if not sector_stocks_df.empty:
            st.markdown(f"### Showing all stocks under **{selected_sector}**")
            st.dataframe(
                sector_stocks_df.sort_values(by="Change (%)", ascending=False), 
                use_container_width=True, 
                hide_index=True
            )
        else:
            st.warning("No stock data found for this sector.")

# --- TAB 3: TOP GAINERS & LOSERS ---
with tab3:
    st.subheader("🔥 Top Market Movers Across All Sectors")

    if not master_df.empty:
        col_gain, col_loss = st.columns(2)
        
        with col_gain:
            st.markdown("### 🟢 Top Gainers")
            gainers = master_df.sort_values(by="Change (%)", ascending=False).head(5)
            st.dataframe(gainers, use_container_width=True, hide_index=True)
            
        with col_loss:
            st.markdown("### 🔴 Top Losers")
            losers = master_df.sort_values(by="Change (%)", ascending=True).head(5)
            st.dataframe(losers, use_container_width=True, hide_index=True)
