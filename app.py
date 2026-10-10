import streamlit as st
import pandas as pd
import yfinance as yf
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

    .matrix-card-green {
        background: linear-gradient(135deg, #064e3b 0%, #065f46 100%);
        border: 1px solid #10b981;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.2);
        margin-bottom: 12px;
        transition: transform 0.15s ease;
    }
    .matrix-card-green:hover {
        transform: translateY(-2px);
    }

    .matrix-card-red {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        border: 1px solid #ef4444;
        padding: 16px;
        border-radius: 12px;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.2);
        margin-bottom: 12px;
        transition: transform 0.15s ease;
    }
    .matrix-card-red:hover {
        transform: translateY(-2px);
    }
    
    .stButton>button {
        width: 100%;
        background: rgba(255, 255, 255, 0.1);
        color: white;
        font-weight: 700;
        border-radius: 6px;
        border: 1px solid rgba(255, 255, 255, 0.2);
        padding: 8px;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    /* TradingView Link Styling inside Cards */
    .tv-link {
        display: inline-block;
        margin-top: 8px;
        font-size: 11px;
        color: #6ee7b7;
        text-decoration: none;
        font-weight: 600;
    }
    .tv-link:hover {
        text-decoration: underline;
        color: #ffffff;
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

# --- COMPLETE ALL-SECTOR UNIVERSE ---
SECTOR_MAP = {
    "IT & Technology": ["TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", "MPHASIS.NS", "COFORGE.NS"],
    "Banking & Financials": ["HDFCBANK.NS", "ICICIBANK.NS", "SBIN.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS", "BAJFINANCE.NS"],
    "Automobile": ["TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "TVSMOTOR.NS"],
    "Pharmaceuticals": ["SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", "LUPIN.NS", "ALKEM.NS"],
    "Energy & Oil/Gas": ["RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "POWERGRID.NS", "NTPC.NS", "TATAPOWER.NS"],
    "Metal & Infrastructure": ["TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "GRASIM.NS", "ADANIENT.NS", "LT.NS"],
    "FMCG": ["HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", "DABUR.NS", "MARICO.NS"],
    "Media & Entertainment": ["SUNTV.NS", "PVRINOX.NS", "ZEEL.NS", "NETWORK18.NS"],
    "Realty & Construction": ["DLF.NS", "GodrejProp.NS", "OBEROIRLTY.NS", "PHOENIXLTD.NS", "PRESTIGE.NS"]
}

def fetch_stock_fast(ticker):
    try:
        tk = yf.Ticker(ticker)
        df = tk.history(period="2d", interval="5m")
        if df is not None and len(df) >= 2:
            curr_price = df['Close'].iloc[-1]
            prev_close = df['Close'].iloc[-2]
            change_pct = ((curr_price - prev_close) / prev_close) * 100
            volume = int(df['Volume'].iloc[-1])
            
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

@st.cache_data(ttl=15)
def execute_master_scan(all_tickers_tuple):
    start_t = time.time()
    with ThreadPoolExecutor(max_workers=50) as executor:
        results = list(executor.map(fetch_stock_fast, all_tickers_tuple))
    valid = [r for r in results if r is not None]
    exec_time = round((time.time() - start_t) * 1000, 2)
    return pd.DataFrame(valid), exec_time

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("### ⚡ Institutional Pro Intraday Terminal")
    st.markdown("<span style='font-size: 12px; color: #10b981;'>All Sectors Live Matrix | TradingView Direct Integration</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align: right; color: #10b981; font-weight: 600; font-size: 13px;'>🟢 IST: {get_ist_time().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

st.markdown("---")

all_tickers = [t for sub in SECTOR_MAP.values() for t in sub]

with st.spinner("⚡ Synchronizing all sectors in milliseconds..."):
    master_df, speed_ms = execute_master_scan(tuple(all_tickers))

if 'selected_sector_click' not in st.session_state:
    st.session_state.selected_sector_click = list(SECTOR_MAP.keys())[0]

tab1, tab2, tab3, tab4 = st.tabs([
    "📌 1. All Sectors Matrix", 
    "📂 2. Sector Stocks", 
    "🔥 3. Gainers & Losers", 
    "⚡ 4. 9:15-9:30 ORB Breakout"
])

# --- TAB 1: ALL SECTORS MATRIX ---
with tab1:
    st.caption(f"⚡ Scan Latency: {speed_ms} ms | Click any sector inspect button")
    
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
                    avg_val = row["Avg Change (%)"]
                    card_class = "matrix-card-green" if avg_val >= 0 else "matrix-card-red"
                    arrow = "🚀" if avg_val >= 0 else "🔻"
                    
                    with cols[j]:
                        st.markdown(f"""
                            <div class="{card_class}">
                                <h4 style="margin: 0; color: #fff;">{row['Sector']}</h4>
                                <h2 style="margin: 4px 0; color: #ffffff;">{avg_val:+.2f}% {arrow}</h2>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Stocks: {row['Total']} | 🟢 {row['Gainers']} 🔴 {row['Losers']}</p>
                            </div>
                        """, unsafe_allow_html=True)
                        if st.button(f"🔍 Inspect {row['Sector']}", key=f"s_{row['Sector']}"):
                            st.session_state.selected_sector_click = row['Sector']
                            st.rerun()

# --- TAB 2: SECTOR STOCKS WITH TRADINGVIEW LINK ---
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
                    chg_val = stk["Change (%)"]
                    card_cls = "matrix-card-green" if chg_val >= 0 else "matrix-card-red"
                    sym = stk["Symbol"]
                    tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}"
                    
                    with cols[j]:
                        st.markdown(f"""
                            <div class="{card_cls}">
                                <h4 style="margin: 0; color: #fff;">{sym}</h4>
                                <h3 style="margin: 4px 0; color: #fff;">₹{stk['LTP']:,.2f} ({chg_val:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {stk['Volume']:,}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 Open TradingView Chart ↗</a>
                            </div>
                        """, unsafe_allow_html=True)

# --- TAB 3: GAINERS & LOSERS WITH TRADINGVIEW LINK ---
with tab3:
    col_g, col_l = st.columns(2)
    with col_g:
        st.markdown("### 🟢 Top Gainers")
        top_g = master_df.sort_values(by="Change (%)", ascending=False).head(6)
        for _, r in top_g.iterrows():
            sym = r['Symbol']
            tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}"
            st.markdown(f"""
                <div class="matrix-card-green">
                    <h4 style="margin: 0; color: #fff;">{sym}</h4>
                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} (+{r['Change (%)']:.2f}%)</h3>
                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,}</p>
                    <a href="{tv_url}" target="_blank" class="tv-link">📈 Open TradingView Chart ↗</a>
                </div>
            """, unsafe_allow_html=True)
            
    with col_l:
        st.markdown("### 🔴 Top Losers")
        top_l = master_df.sort_values(by="Change (%)", ascending=True).head(6)
        for _, r in top_l.iterrows():
            sym = r['Symbol']
            tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}"
            st.markdown(f"""
                <div class="matrix-card-red">
                    <h4 style="margin: 0; color: #fff;">{sym}</h4>
                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:.2f}%)</h3>
                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,}</p>
                    <a href="{tv_url}" target="_blank" class="tv-link">📈 Open TradingView Chart ↗</a>
                </div>
            """, unsafe_allow_html=True)

# --- TAB 4: ORB BREAKOUT WITH TRADINGVIEW LINK ---
with tab4:
    st.markdown("### ⚡ 9:15 - 9:30 Opening Range Breakout (ORB)")
    orb_bull = master_df[master_df["Status"].str.contains("BULLISH")]
    orb_bear = master_df[master_df["Status"].str.contains("BEARISH")]
    
    col_ob1, col_ob2 = st.columns(2)
    with col_ob1:
        st.markdown("#### 🚀 Bullish ORB Breakouts")
        if not orb_bull.empty:
            for _, r in orb_bull.iterrows():
                sym = r['Symbol']
                tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}"
                st.markdown(f"""
                    <div class="matrix-card-green">
                        <h4 style="margin: 0; color: #fff;">{sym} <span style="font-size: 11px; color: #fff;">[BREAKOUT]</span></h4>
                        <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                        <p style="font-size: 11px; color: #e2e8f0; margin: 0;">ORB High: ₹{r['ORB High']} | Vol: {r['Volume']:,}</p>
                        <a href="{tv_url}" target="_blank" class="tv-link">📈 Open TradingView Chart ↗</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active bullish breakout right now.")
            
    with col_ob2:
        st.markdown("#### 🔻 Bearish ORB Breakdowns")
        if not orb_bear.empty:
            for _, r in orb_bear.iterrows():
                sym = r['Symbol']
                tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}"
                st.markdown(f"""
                    <div class="matrix-card-red">
                        <h4 style="margin: 0; color: #fff;">{sym} <span style="font-size: 11px; color: #fff;">[BREAKDOWN]</span></h4>
                        <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                        <p style="font-size: 11px; color: #e2e8f0; margin: 0;">ORB Low: ₹{r['ORB Low']} | Vol: {r['Volume']:,}</p>
                        <a href="{tv_url}" target="_blank" class="tv-link">📈 Open TradingView Chart ↗</a>
                    </div>
                """, unsafe_allow_html=True)
        else:
            st.info("No active bearish breakdown right now.")

time.sleep(20)
st.rerun()
