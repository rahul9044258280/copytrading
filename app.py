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
        padding: 14px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(16, 185, 129, 0.2);
        margin-bottom: 10px;
        transition: transform 0.15s ease;
    }
    .matrix-card-green:hover {
        transform: translateY(-2px);
    }

    .matrix-card-red {
        background: linear-gradient(135deg, #7f1d1d 0%, #991b1b 100%);
        border: 1px solid #ef4444;
        padding: 14px;
        border-radius: 10px;
        box-shadow: 0 4px 14px rgba(239, 68, 68, 0.2);
        margin-bottom: 10px;
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
        padding: 6px;
        font-size: 12px;
    }
    .stButton>button:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    .tv-link {
        display: inline-block;
        margin-top: 6px;
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

# --- EXPANDED NIFTY 500 & LIQUID CASH UNIVERSE ---
SECTOR_MAP = {
    "IT & Technology": [
        "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", 
        "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "OFSS.NS", "KPITTECH.NS", 
        "TATAELXSI.NS", "CYIENT.NS", "LTTS.NS", "BSOFT.NS", "ZENSARTECH.NS"
    ],
    "Private Bank": [
        "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS", 
        "FEDERALBNK.NS", "AUBANK.NS", "BANDHANBNK.NS", "IDFCFIRSTB.NS", "RBLBANK.NS", 
        "CITYUNIONB.NS", "CUB.NS", "KARURVYSYA.NS"
    ],
    "PSU Bank": [
        "SBIN.NS", "PNB.NS", "BANKBARODA.NS", "CANBK.NS", "UNIONBANK.NS", 
        "IOB.NS", "IDBI.NS", "INDIANB.NS", "UCOBANK.NS", "CENTRALBK.NS", "BANKINDIA.NS"
    ],
    "Financial Services & NBFC": [
        "BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "SBICARD.NS", 
        "SHRIRAMFIN.NS", "REC.NS", "PFC.NS", "MANAPPURAM.NS", "M&MFIN.NS", 
        "LICHSGFIN.NS", "HUDCO.NS", "IREDA.NS"
    ],
    "Automobile & Auto Ancillary": [
        "TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS", 
        "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "MOTHERSON.NS", 
        "BOSCHLTD.NS", "MRF.NS", "BALKRISIND.NS", "TIINDIA.NS"
    ],
    "Pharmaceuticals & Biotech": [
        "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "DIVISLAB.NS", 
        "LUPIN.NS", "ALKEM.NS", "TORNTPHARM.NS", "MANKIND.NS", "ZYDUSLIFE.NS", 
        "GLENMARK.NS", "GRANULES.NS", "AUROPHARMA.NS", "IPCALAB.NS", "BIOCON.NS"
    ],
    "Energy, Oil & Power": [
        "RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "POWERGRID.NS", 
        "NTPC.NS", "TATAPOWER.NS", "ADANIGREEN.NS", "GAIL.NS", "COALINDIA.NS", 
        "NHPC.NS", "SJVN.NS", "PETRONET.NS", "OIL.NS", "SUZLON.NS"
    ],
    "Metal, Mining & Infra": [
        "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "GRASIM.NS", 
        "ADANIENT.NS", "LT.NS", "JINDALSTEL.NS", "NATIONALUM.NS", "NMDC.NS", 
        "SAIL.NS", "APLAPOLLO.NS", "HINDZINC.NS", "IRB.NS"
    ],
    "FMCG & Consumer Staples": [
        "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", 
        "DABUR.NS", "MARICO.NS", "COLPAL.NS", "GODREJCP.NS", "VBL.NS", 
        "AWL.NS", "PATANJALI.NS", "EMAMILTD.NS"
    ],
    "Consumer Durables & Retail": [
        "TITAN.NS", "ASIANPAINT.NS", "HAVELLS.NS", "VOLTAS.NS", "WHIRLPOOL.NS", 
        "DIXON.NS", "CROMPTON.NS", "POLYCAB.NS", "KEI.NS", "BERGEPAINT.NS", 
        "TRENT.NS", "DMART.NS"
    ],
    "Realty & Infrastructure": [
        "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PHOENIXLTD.NS", "PRESTIGE.NS", 
        "LODHA.NS", "NBCC.NS", "NCC.NS", "GRINFRA.NS"
    ],
    "Chemicals & Fertilizers": [
        "UPL.NS", "PIIND.NS", "SRF.NS", "AARTIIND.NS", "COROMANDEL.NS", 
        "NAVINFLUOR.NS", "DEEPAKNTR.NS", "FACT.NS", "RCFL.NS", "GNFC.NS"
    ],
    "Defence & Capital Goods": [
        "HAL.NS", "BEL.NS", "BDL.NS", "COCHINSHIP.NS", "MAZDOCK.NS", 
        "SIEMENS.NS", "ABB.NS", "CGPOWER.NS", "BHEL.NS"
    ]
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
            
            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            vwap = (typical_price * df['Volume']).sum() / df['Volume'].sum() if df['Volume'].sum() > 0 else curr_price
            
            avg_vol = df['Volume'].mean() if len(df) > 1 else volume
            rvol = round(volume / avg_vol, 2) if avg_vol > 0 else 1.0

            morning = df.between_time("09:15", "09:30")
            orb_high = morning['High'].max() if not morning.empty else curr_price
            orb_low = morning['Low'].min() if not morning.empty else curr_price
            
            status = "NORMAL"
            pro_status = "NORMAL"

            if curr_price > orb_high:
                status = "BULLISH BREAKOUT 🚀"
            elif curr_price < orb_low:
                status = "BEARISH BREAKDOWN 🔻"

            if curr_price > orb_high and curr_price > vwap and rvol >= 1.3:
                pro_status = "PRO BULLISH 🚀"
            elif curr_price < orb_low and curr_price < vwap and rvol >= 1.3:
                pro_status = "PRO BEARISH 🔻"

            return {
                "Symbol": ticker.replace(".NS", ""),
                "LTP": round(curr_price, 2),
                "Change (%)": round(change_pct, 2),
                "Volume": volume,
                "RVol": rvol,
                "VWAP": round(vwap, 2),
                "ORB High": round(orb_high, 2),
                "ORB Low": round(orb_low, 2),
                "Status": status,
                "ProStatus": pro_status,
                "Prev Close": round(prev_close, 2)
            }
    except Exception:
        return None
    return None

@st.cache_data(ttl=25)
def execute_master_scan(all_tickers_tuple):
    start_t = time.time()
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = list(executor.map(fetch_stock_fast, all_tickers_tuple))
    valid = [r for r in results if r is not None]
    exec_time = round((time.time() - start_t) * 1000, 2)
    return pd.DataFrame(valid), exec_time

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("### ⚡ Master Institutional Pro Terminal")
    st.markdown("<span style='font-size: 12px; color: #10b981;'>Strict Sorted Feed | 30s Auto Refresh Active</span>", unsafe_allow_html=True)
with col_h2:
    st.markdown(f"<div style='text-align: right; color: #10b981; font-weight: 600; font-size: 13px;'>🟢 IST: {get_ist_time().strftime('%H:%M:%S')}</div>", unsafe_allow_html=True)

st.markdown("---")

all_tickers = [t for sub in SECTOR_MAP.values() for t in sub]

with st.spinner("⚡ Scanning & sorting market universe..."):
    master_df, speed_ms = execute_master_scan(tuple(all_tickers))

if 'selected_sector_click' not in st.session_state:
    st.session_state.selected_sector_click = list(SECTOR_MAP.keys())[0]

# --- SAFETY CHECK & GLOBAL SORTING ---
if master_df.empty or "Symbol" not in master_df.columns:
    st.error("Market data fetch karne me samasya aa rahi hai. Kripya thodi der baad refresh karein.")
else:
    # Always sort master dataframe by Change (%) in descending order
    master_df = master_df.sort_values(by="Change (%)", ascending=False).reset_index(drop=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📌 1. All Sectors Matrix", 
        "📂 2. Sector Stocks", 
        "🔥 3. Gainers & Losers", 
        "⚡ 4. 9:15-9:30 ORB",
        "💎 5. VWAP + RVol ORB Pro"
    ])

    # --- TAB 1: ALL SECTORS MATRIX ---
    with tab1:
        st.caption(f"⚡ Feed Latency: {speed_ms} ms | Monitored Stocks: {len(master_df)} | Auto-Refresh: 30s")
        
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
                
        sec_summary_df = pd.DataFrame(sector_summary).sort_values(by="Avg Change (%)", ascending=False).reset_index(drop=True)
        
        if not sec_summary_df.empty:
            for i in range(0, len(sec_summary_df), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(sec_summary_df):
                        row = sec_summary_df.iloc[i + j]
                        avg_val = row["Avg Change (%)"]
                        card_class = "matrix-card-green" if avg_val >= 0 else "matrix-card-red"
                        arrow = "🚀" if avg_val >= 0 else "🔻"
                        
                        with cols[j]:
                            st.markdown(f"""
                                <div class="{card_class}">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{row['Sector']}</h5>
                                    <h3 style="margin: 4px 0; color: #ffffff;">{avg_val:+.2f}% {arrow}</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Stocks: {row['Total']} | 🟢 {row['Gainers']} 🔴 {row['Losers']}</p>
                                </div>
                            """, unsafe_allow_html=True)
                            if st.button(f"🔍 Inspect {row['Sector']}", key=f"s_{row['Sector']}"):
                                st.session_state.selected_sector_click = row['Sector']
                                st.rerun()

    # --- TAB 2: SECTOR STOCKS (STRICT DECREASING SORT) ---
    with tab2:
        sel_sec = st.selectbox("Select Sector", list(SECTOR_MAP.keys()), index=list(SECTOR_MAP.keys()).index(st.session_state.selected_sector_click))
        st.session_state.selected_sector_click = sel_sec
        
        clean_tks = [t.replace(".NS", "") for t in SECTOR_MAP[sel_sec]]
        # Strict sorting: Highest gainers to lowest
        stocks_subset = master_df[master_df["Symbol"].isin(clean_tks)].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        
        st.write(f"Showing **{len(stocks_subset)}** stocks in **{sel_sec}** (Sorted by Highest to Lowest % Change):")
        
        if not stocks_subset.empty:
            for i in range(0, len(stocks_subset), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(stocks_subset):
                        stk = stocks_subset.iloc[i + j]
                        chg_val = stk["Change (%)"]
                        card_cls = "matrix-card-green" if chg_val >= 0 else "matrix-card-red"
                        sym = stk["Symbol"]
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        
                        with cols[j]:
                            st.markdown(f"""
                                <div class="{card_cls}">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym}</h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{stk['LTP']:,.2f} ({chg_val:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {stk['Volume']:,} | RVol: {stk['RVol']}x</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)

    # --- TAB 3: GAINERS & LOSERS ---
    with tab3:
        st.markdown("### 📊 Standard Market Gainers & Losers")
        col_g, col_l = st.columns(2)
        with col_g:
            st.markdown("#### 🟢 Top Gainers (Highest % Change)")
            top_g = master_df.sort_values(by="Change (%)", ascending=False).head(4).reset_index(drop=True)
            g_cols = st.columns(2)
            for idx, (_, r) in enumerate(top_g.iterrows()):
                sym = r['Symbol']
                tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                with g_cols[idx % 2]:
                    st.markdown(f"""
                        <div class="matrix-card-green">
                            <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym}</h5>
                            <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} (+{r['Change (%)']:.2f}%)</h3>
                            <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,} | RVol: {r['RVol']}x</p>
                            <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                        </div>
                    """, unsafe_allow_html=True)
                
        with col_l:
            st.markdown("#### 🔴 Top Losers (Lowest % Change)")
            top_l = master_df.sort_values(by="Change (%)", ascending=True).head(4).reset_index(drop=True)
            l_cols = st.columns(2)
            for idx, (_, r) in enumerate(top_l.iterrows()):
                sym = r['Symbol']
                tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                with l_cols[idx % 2]:
                    st.markdown(f"""
                        <div class="matrix-card-red">
                            <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym}</h5>
                            <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:.2f}%)</h3>
                            <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,} | RVol: {r['RVol']}x</p>
                            <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                        </div>
                    """, unsafe_allow_html=True)

    # --- TAB 4: ORB BREAKOUT (STRICTLY SORTED) ---
    with tab4:
        st.markdown("### ⚡ Standard 9:15 - 9:30 Opening Range Breakout")
        orb_bull = master_df[master_df["Status"].str.contains("BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        orb_bear = master_df[master_df["Status"].str.contains("BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
        
        st.markdown("#### 🚀 Bullish ORB Breakouts (Decreasing Order)")
        if not orb_bull.empty:
            for i in range(0, len(orb_bull), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(orb_bull):
                        r = orb_bull.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                                <div class="matrix-card-green">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym}</h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">ORB High: ₹{r['ORB High']}</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No active bullish breakout right now.")
            
        st.markdown("#### 🔻 Bearish ORB Breakdowns")
        if not orb_bear.empty:
            for i in range(0, len(orb_bear), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(orb_bear):
                        r = orb_bear.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                                <div class="matrix-card-red">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym}</h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">ORB Low: ₹{r['ORB Low']}</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No active bearish breakdown right now.")

    # --- TAB 5: VWAP + RVOL ORB PRO (STRICTLY SORTED) ---
    with tab5:
        st.markdown("### 💎 Institutional Pro Filter: ORB + VWAP + RVol Spike (>= 1.3x)")
        
        pro_bull = master_df[master_df["ProStatus"].str.contains("PRO BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        pro_bear = master_df[master_df["ProStatus"].str.contains("PRO BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
        
        st.markdown("#### 🚀 Pro Institutional Bullish Setups (Highest % Change First)")
        if not pro_bull.empty:
            for i in range(0, len(pro_bull), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(pro_bull):
                        r = pro_bull.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                                <div class="matrix-card-green">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym} <span style="font-size: 10px; background: #047857; padding: 2px 4px; border-radius: 4px;">PRO</span></h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">VWAP: ₹{r['VWAP']} | RVol: <b>{r['RVol']}x</b></p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("Abhi koi Pro Bullish setup active nahi hai.")
            
        st.markdown("#### 🔻 Pro Institutional Bearish Setups")
        if not pro_bear.empty:
            for i in range(0, len(pro_bear), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(pro_bear):
                        r = pro_bear.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                                <div class="matrix-card-red">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym} <span style="font-size: 10px; background: #b91c1c; padding: 2px 4px; border-radius: 4px;">PRO</span></h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">VWAP: ₹{r['VWAP']} | RVol: <b>{r['RVol']}x</b></p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("Abhi koi Pro Bearish setup active nahi hai.")

# Strict 30 Seconds Auto Refresh Loop
time.sleep(30)
st.rerun()
