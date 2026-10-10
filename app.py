import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timezone, timedelta
import time
from concurrent.futures import ThreadPoolExecutor

# --- IST TIMEZONE CONFIGURATION (UTC +5:30) ---
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_time():
    return datetime.now(IST)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="IST Synchronized Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- CINEMATIC MATRIX & CARD STYLING ---
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

    .matrix-card {
        background: linear-gradient(135deg, #111827 0%, #1f2937 100%);
        border: 1px solid #374151;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 6px 16px rgba(0,0,0,0.4);
        margin-bottom: 12px;
        transition: transform 0.2s ease;
    }
    .matrix-card:hover {
        border-color: #10b981;
        transform: translateY(-2px);
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

# --- PARALLEL SCANNER ENGINE ---
def run_fast_scan(tickers):
    start_time = time.time()
    with ThreadPoolExecutor(max_workers=40) as executor:
        results = list(executor.map(fetch_single_ticker, tickers))
    valid_data = [res for res in results if res is not None]
    execution_ms = round((time.time() - start_time) * 1000, 2)
    return pd.DataFrame(valid_data), execution_ms

# --- SIDEBAR CONTROLS ---
with st.sidebar:
    st.markdown("### ⚡ IST Terminal Controls")
    st.markdown("---")
    enable_auto_refresh = st.checkbox("Enable Auto-Refresh (IST Live)", value=True)
    refresh_rate = st.slider("Refresh Interval (Seconds)", min_value=15, max_value=120, value=30)
    st.markdown("---")
    if st.button("🔄 Force Refresh Now"):
        st.cache_data.clear()
        st.rerun()
    st.info("Timing is synchronized with Indian Standard Time (IST). Optimized for 9:15 AM market open.")

# --- APP HEADER WITH IST TIME ---
current_ist = get_ist_time()
formatted_time = current_ist.strftime('%d %b %Y | %H:%M:%S IST')

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.title("⚡ IST Synchronized Cinematic Terminal")
    st.markdown("Real-Time Millisecond NSE Scanner mapped to Indian Standard Time.")
with col_h2:
    st.markdown(f"<div style='text-align: right; color: #10b981; font-weight: 600; padding-top: 10px;'>🟢 IST FEED ACTIVE<br><span style='font-size: 11px; color: #9ca3af;'>{formatted_time}</span></div>", unsafe_allow_html=True)

st.markdown("---")

# --- SESSION STATE INITIALIZATION ---
if 'selected_sector_click' not in st.session_state:
    st.session_state.selected_sector_click = list(SECTOR_MAP.keys())[0]

# --- FETCH ALL DATA ---
all_tickers = [t for sublist in SECTOR_MAP.values() for t in sublist]
with st.spinner("Scanning market in IST timezone..."):
    master_df, speed_ms = run_fast_scan(all_tickers)

# --- TABS SETUP ---
tab1, tab2, tab3 = st.tabs(["📌 1. Sector Overview", "📂 2. Stocks by Sector", "🔥 3. Top Gainers & Losers"])

# --- TAB 1: SECTOR OVERVIEW MATRIX ---
with tab1:
    st.subheader("NSE Sector Performance Board (IST Live)")
    st.caption(f"Scan completed in {speed_ms} ms | Timezone: IST (UTC+5:30)")

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
                            <div class="matrix-card">
                                <h4 style="margin: 0; color: #ffffff;">{sec_name}</h4>
                                <h2 style="margin: 5px 0; color: {color_code};">{avg_val:+.2f}%</h2>
                                <p style="font-size: 12px; color: #9ca3af; margin: 0;">Stocks: {row['Total Stocks']} | 🟢 {row['Gainers']} 🔴 {row['Losers']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        
                        if st.button(f"🔍 View {sec_name} Stocks", key=f"btn_{sec_name}"):
                            st.session_state.selected_sector_click = sec_name
                            st.rerun()

# --- TAB 2: STOCKS MATRIX BY SECTOR ---
with tab2:
    st.subheader("📁 Sector Stock Matrix Cards")
    
    selected_sector = st.selectbox(
        "Select Target Sector", 
        list(SECTOR_MAP.keys()), 
        index=list(SECTOR_MAP.keys()).index(st.session_state.selected_sector_click)
    )
    st.session_state.selected_sector_click = selected_sector

    if selected_sector:
        tickers = SECTOR_MAP[selected_sector]
        clean_tickers = [t.replace(".NS", "") for t in tickers]
        sector_stocks_df = master_df[master_df["Symbol"].isin(clean_tickers)]
        
        if not sector_stocks_df.empty:
            sector_stocks_df = sector_stocks_df.sort_values(by="Change (%)", ascending=False)
            
            for i in range(0, len(sector_stocks_df), 3):
                cols = st.columns(3)
                for j in range(3):
                    if i + j < len(sector_stocks_df):
                        stock = sector_stocks_df.iloc[i + j]
                        sym = stock["Symbol"]
                        ltp = stock["LTP"]
                        chg = stock["Change (%)"]
                        vol = stock["Volume"]
                        color_code = "#10b981" if chg >= 0 else "#ef4444"
                        
                        with cols[j]:
                            st.markdown(f"""
                                <div class="matrix-card">
                                    <h4 style="margin: 0; color: #ffffff;">{sym}</h4>
                                    <h3 style="margin: 4px 0; color: {color_code};">₹{ltp:,.2f} <span style="font-size: 16px;">({chg:+.2f}%)</span></h3>
                                    <p style="font-size: 11px; color: #9ca3af; margin: 0;">Vol: {vol:,} | Prev: ₹{stock['Prev Close']}</p>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.warning("No stock data found for this sector.")

# --- TAB 3: TOP GAINERS & LOSERS MATRIX ---
with tab3:
    st.subheader("🔥 Top Market Movers Matrix (IST)")

    if not master_df.empty:
        col_g, col_l = st.columns(2)
        
        with col_g:
            st.markdown("### 🟢 Top Gainers")
            gainers = master_df.sort_values(by="Change (%)", ascending=False).head(6)
            for _, row in gainers.iterrows():
                st.markdown(f"""
                    <div class="matrix-card">
                        <h4 style="margin: 0; color: #ffffff;">{row['Symbol']}</h4>
                        <h3 style="margin: 4px 0; color: #10b981;">₹{row['LTP']:,.2f} (+{row['Change (%)']:.2f}%)</h3>
                        <p style="font-size: 11px; color: #9ca3af; margin: 0;">Volume: {row['Volume']:,}</p>
                    </div>
                """, unsafe_allow_html=True)
                
        with col_l:
            st.markdown("### 🔴 Top Losers")
            losers = master_df.sort_values(by="Change (%)", ascending=True).head(6)
            for _, row in losers.iterrows():
                st.markdown(f"""
                    <div class="matrix-card">
                        <h4 style="margin: 0; color: #ffffff;">{row['Symbol']}</h4>
                        <h3 style="margin: 4px 0; color: #ef4444;">₹{row['LTP']:,.2f} ({row['Change (%)']:.2f}%)</h3>
                        <p style="font-size: 11px; color: #9ca3af; margin: 0;">Volume: {row['Volume']:,}</p>
                    </div>
                """, unsafe_allow_html=True)

# --- AUTO REFRESH LOOP ---
if enable_auto_refresh:
    time.sleep(refresh_rate)
    st.rerun()
