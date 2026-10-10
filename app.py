import streamlit as st
import pandas as pd
import asyncio
import aiohttp
from datetime import datetime, timezone, timedelta
import time
from concurrent.futures import ThreadPoolExecutor

# --- IST TIMEZONE (UTC +5:30) ---
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_time():
    return datetime.now(IST)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="Institutional Pro Intraday Terminal",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HIGH-PERFORMANCE CINEMATIC CSS ---
st.markdown("""
    <style>
    .stApp {
        background-color: #07090e;
        color: #f3f4f6;
        font-family: 'Inter', sans-serif;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .matrix-card {
        background: linear-gradient(135deg, #0d1322 0%, #161f33 100%);
        border: 1px solid #1f293d;
        padding: 14px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(0,0,0,0.5);
        margin-bottom: 10px;
        transition: all 0.15s ease;
    }
    .matrix-card:hover {
        border-color: #10b981;
        transform: translateY(-1px);
    }
    
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        font-weight: 700;
        border-radius: 6px;
        border: none;
        padding: 8px;
        box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #059669 0%, #047857 100%);
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #0d1322;
        padding: 4px;
        border-radius: 8px;
        border: 1px solid #1f293d;
    }
    .stTabs [aria-selected="true"] {
        background-color: #161f33 !important;
        color: #10b981 !important;
        border: 1px solid #374151;
    }
    </style>
""", unsafe_allow_html=True)

# --- COMPENSIVE SECTOR UNIVERSE ---
SECTOR_MAP = {
    "IT & Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "OFSS.NS"],
    "Banking & Financials": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS", "BAJFINANCE.NS", "BAJAJFINSV.NS", "PNB.NS", "BANKBARODA.NS"],
    "Automobile": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS"],
    "Pharmaceuticals": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "LUPIN.NS", "ALKEM.NS", "TORNTPHARM.NS"],
    "Energy & Oil/Gas": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "POWERGRID.NS", "NTPC.NS", "TATAPOWER.NS", "ADANIGREEN.NS"],
    "Metal & Infrastructure": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "GRASIM.NS", "ADANIENT.NS", "LT.NS", "JINDALSTEL.NS"]
}

# --- ULTRA-FAST MULTI-THREADED MARKET FETCH ENGINE ---
import yfinance as yf

def fetch_stock_fast(ticker):
    try:
        # Fast query optimization using yfinance fast_info or 2d history
        tk = yf.Ticker(ticker)
        df = tk.history(period="2d", interval="5m")
        if df is not None and len(df) >= 2:
            curr_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2] # simplified prev reference
            change_pct = ((curr_price - prev_close) / prev_close) * 100
            volume = int(df['Volume'].iloc[-1])
            
            # ORB calculation (9:15 to 9:30)
            morning = df.between_time("09:15", "09:30")
            orb_high = morning['High'].max() if not morning.empty else curr_price
            orb_low = morning['Low'].min() if not morning.empty else curr_price
            
            status = "NORMAL"
            if curr_price > orb_high:
                status = "BULLISH BREAKOUT 🚀"
            elif curr_price < orb_low:
                status = "BEARISH BREAKDOWN 🔻"

            return {
                "Symbol": ticker.replace(".NS", ""),
                "LTP": round(curr_price, 2),
                "Change (%)": round(change_pct, 2),
                "Volume": volume,
                "ORB High": round(orb_high, 2),
                "ORB Low": round(orb_low, 2),
                "Status": status,
                "Prev Close": round(prev_close, 2)
            }
    except Exception:
        return None
    return None

@st.cache_data(ttl=15) # 15 seconds aggressive cache to ensure zero lag on switching
def execute_master_scan(all_tickers_tuple):
    start_t = time.time()
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(fetch_stock_fast, all_tickers_tuple))
    valid = [r for r in results if r is not None]
    exec_time = round((time.time() - start_t) * 1000, 2)
    return pd.DataFrame(valid), exec_time

# --- HEADER & STATUS BAR ---
col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("### ⚡ Institutional Pro Intraday Terminal")
    st.markdown("<span style='font-size: 12px; color: #10b981;'>Zero-Lag Multi-Threaded Engine Active | Instant Tab Switching</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align: right; color: #10b981; font-weight: 600; font-size: 13px;'>🟢 IST: {get_ist_time().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

st.markdown("---")

# Flatten all tickers
all_tickers = [t for sub in SECTOR_MAP.values() for t in sub]

# Run Master Scan with cache optimization
with st.spinner("⚡ High-speed market synchronization..."):
    master_df, speed_ms = execute_master_scan(tuple(all_tickers))

if 'selected_sector_click' not in st.session_state:
    st.session_state.selected_sector_click = list(SECTOR_MAP.keys())[0]

# --- TABS CREATION ---
tab1, tab2, tab3, tab4 = st.tabs([
    "📌 1. Sector Matrix", 
    "📂 2. Sector Stocks", 
    "🔥 3. Gainers & Losers", 
    "⚡ 4. 9:15-9:30 ORB Breakout"
])

# --- TAB 1: SECTOR MATRIX ---
with tab1:
    st.caption(f"⚡ Scan Latency: {speed_ms} ms (Ultra-Fast)")
    
    sector_summary = []
    for sec, tks in SECTOR_MAP.items():
        clean_tks = [t.replace(".NS", "") for t in tks]
        sec_df = master_df[master_df["Symbol"].isin(clean_tks)]
        if not sec_df.empty:
            avg_chg = sec_df["Change (%)"].mean()
            sector_summary.append({
                "Sector": sec,
                "Avg Change (%)": round(avg_chg, 2),
                "Total": len(sec_df),
                "Gainers": len(sec_df[sec_df["Change (%)"] > 0]),
                "Losers": len(sec_df[sec_df["Change (%)"] < 0])
            })
            
    sec_summary_df = pd.DataFrame(sector_summary).sort_values(by="Avg Change (%)", ascending=False)
    
    if not sec_summary_df.empty:
        for i in range(0, len(sec_summary_df), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(sec_summary_df):
                    row = sec_summary_df.iloc[i + j]
                    c_col = "#10b981" if row["Avg Change (%)"] >= 0 else "#ef4444"
                    with cols[j]:
                        st.markdown(f"""
                            <div class="matrix-card">
                                <h4 style="margin: 0; color: #fff;">{row['Sector']}</h4>
                                <h2 style="margin: 4px 0; color: {c_col};">{row['Avg Change (%)']:+.2f}%</h2>
                                <p style="font-size: 11px; color: #9ca3af; margin: 0;">Stocks: {row['Total']} | 🟢 {row['Gainers']} 🔴 {row['Losers']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"🔍 Inspect {row['Sector']}", key=f"s_{row['Sector']}"):
                            st.session_state.selected_sector_click = row['Sector']
                            st.rerun()

# --- TAB 2: SECTOR STOCKS ---
with tab2:
    sel_sec = st.selectbox("Select Sector", list(SECTOR_MAP.keys()), index=list(SECTOR_MAP.keys()).index(st.session_state.selected_sector_click))
    st.session_state.selected_sector_click = sel_sec
    
    clean_tks = [t.replace(".NS", "") for t in SECTOR_MAP[sel_sec]]
    stocks_subset = master_df[master_df["Symbol"].isin(clean_tks)].sort_values(by="Change (%)", ascending=False)
    
    if not stocks_subset.empty:
        for i in range(0, len(stocks_subset), 3):
            cols = st.columns(3)
            for j in range(3):
                if i + j < len(stocks_subset):
                    stk = stocks_subset.iloc[i + j]
                    c_col = "#10b981" if stk["Change (%)"] >= 0 else "#ef4444"
                    with cols[j]:
                        st.markdown(f"""
                            <div class="matrix-card">
                                <h4 style="margin: 0; color: #fff;">{stk['Symbol']}</h4>
                                <h3 style="margin: 4px 0; color: {c_col};">₹{stk['LTP']:,.2f} ({stk['Change (%)']:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #9ca3af; margin: 0;">Vol: {stk['Volume']:,}</p>
                            </div>
                        """, unsafe_allow_html=True)

# --- TAB 3: GAINERS & LOSERS ---
with tab3:
    col_g, col_l = st.columns(2)
    with col_g:
        st.markdown("### 🟢 Top Gainers")
        top_g = master_df.sort_values(by="Change (%)", ascending=False).head(6)
        for _, r in top_g.iterrows():
            st.markdown(f"""
                <div class="matrix-card">
                    <h4 style="margin: 0; color: #fff;">{r['Symbol']}</h4>
                    <h3 style="margin: 4px 0; color: #10b981;">₹{r['LTP']:,.2f} (+{r['Change (%)']:.2f}%)</h3>
                    <p style="font-size: 11px; color: #9ca3af; margin: 0;">Vol: {r['Volume']:,}</p>
                </div>
            """, unsafe_allow_html=True)
            
    with col_l:
        st.markdown("### 🔴 Top Losers")
        top_l = master_df.sort_values(by="Change (%)", ascending=True).head(6)
        for _, r in top_l.iterrows():
            st.markdown(f"""
                <div class="matrix-card">
                    <h4 style="margin: 0; color: #fff;">{r['Symbol']}</h4>
                    <h3 style="margin: 4px 0; color: #ef4444;">₹{r['LTP']:,.2f} ({r['Change (%)']:.2f}%)</h3>
                    <p style="font-size: 11px; color: #9ca3af; margin: 0;">Vol: {r['Volume']:,}</p>
                </div>
            """, unsafe_allow_html=True)

# --- TAB 4: ORB BREAKOUT ---
with tab4:
    st.markdown("### ⚡ 9:15 - 9:30 Opening Range Breakout (ORB)")
    orb_bull = master_df[master_df["Status"].str.contains("BULLISH")]
    orb_bear = master_df[master_df["Status"].str.contains("BEARISH")]
    
    col_ob1, col_ob2 = st.columns(2)
    with col_ob1:
        st.markdown("#### 🚀 Bullish ORB Breakouts")
        if not orb_bull.empty:
            for _, r in orb_bull.iterrows():
                st.markdown(f"""
                    <div class="matrix-card" style="border-color: #10b981;">
                        <h4 style="margin: 0; color: #fff;">{r['Symbol']} <span style="font-size: 11px; color: #10b981;">[BREAKOUT]</span></h4>
                        <h3 style="margin: 4px 0; color: #10b981;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                        <p style="font-size: 11px; color: #9ca3af; margin: 0;">ORB High: ₹{r['ORB High']} | Vol: {r['Volume']:,}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active bullish breakout right now.")
            
    with col_ob2:
        st.markdown("#### 🔻 Bearish ORB Breakdowns")
        if not orb_bear.empty:
            for _, r in orb_bear.iterrows():
                st.markdown(f"""
                    <div class="matrix-card" style="border-color: #ef4444;">
                        <h4 style="margin: 0; color: #fff;">{r['Symbol']} <span style="font-size: 11px; color: #ef4444;">[BREAKDOWN]</span></h4>
                        <h3 style="margin: 4px 0; color: #ef4444;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                        <p style="font-size: 11px; color: #9ca3af; margin: 0;">ORB Low: ₹{r['ORB Low']} | Vol: {r['Volume']:,}</p>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active bearish breakdown right now.")

# Auto-refresh loop for live continuous scanning
time.sleep(20)
st.rerun()
