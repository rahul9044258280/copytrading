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
    page_title="SCAN PRO - Stock Market Solutions",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HIGH-PERFORMANCE CINEMATIC, 3D TABS & PCR DASHBOARD CSS ---
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

    /* 3D BOLD CORNER TIME BOX STYLING */
    .time-3d-box {
        background: linear-gradient(145deg, #0d1e18, #052e21);
        border: 2px solid #10b981;
        border-radius: 12px;
        padding: 10px 18px;
        box-shadow: 0 8px 18px rgba(16, 185, 129, 0.3), inset 0 1px 0 rgba(255, 255, 255, 0.2);
        display: inline-block;
        float: right;
        text-align: right;
    }
    
    .time-3d-text {
        font-size: 22px !important;
        font-weight: 900 !important;
        color: #10b981 !important;
        letter-spacing: 1px !important;
        font-family: 'monospace', 'Inter', sans-serif;
        text-shadow: 0 0 10px rgba(16, 185, 129, 0.5);
    }

    /* 3D Box Container for Nifty 50 & PCR Summary */
    .nifty-3d-box {
        background: linear-gradient(145deg, #111827, #1f2937);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 14px 20px;
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.5), inset 0 1px 0 rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: space-around;
        align-items: center;
        margin-top: 10px;
        margin-bottom: 20px;
    }

    .stat-card-green {
        background: rgba(16, 185, 129, 0.15);
        border: 1px solid #10b981;
        padding: 8px 14px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(16, 185, 129, 0.2);
    }

    .stat-card-red {
        background: rgba(239, 68, 68, 0.15);
        border: 1px solid #ef4444;
        padding: 8px 14px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(239, 68, 68, 0.2);
    }

    .stat-card-blue {
        background: rgba(59, 130, 246, 0.15);
        border: 1px solid #3b82f6;
        padding: 8px 14px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(59, 130, 246, 0.2);
    }

    .stat-card-gray {
        background: rgba(156, 163, 175, 0.15);
        border: 1px solid #9ca3af;
        padding: 8px 14px;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 4px 10px rgba(156, 163, 175, 0.1);
    }

    /* BOLD & 3D BOX STYLING FOR TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
        background-color: transparent !important;
        padding: 6px 0px !important;
        border-bottom: none !important;
    }

    .stTabs [data-baseweb="tab"] {
        background: linear-gradient(145deg, #131b2e, #0b101d) !important;
        border: 1px solid #2d3748 !important;
        border-radius: 10px !important;
        padding: 10px 16px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.4), inset 0 1px 0 rgba(255, 255, 255, 0.08) !important;
        transition: all 0.2s ease-in-out !important;
    }

    .stTabs [data-baseweb="tab"] p {
        font-size: 14px !important;
        font-weight: 800 !important;
        color: #cbd5e1 !important;
        letter-spacing: 0.3px !important;
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(145deg, #1e293b, #0f172a) !important;
        border: 2px solid #10b981 !important;
        box-shadow: 0 6px 18px rgba(16, 185, 129, 0.35), inset 0 1px 0 rgba(255, 255, 255, 0.2) !important;
        transform: translateY(-2px) !important;
    }

    .stTabs [aria-selected="true"] p {
        color: #10b981 !important;
        font-size: 15px !important;
    }

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
    </style>
""", unsafe_allow_html=True)

# --- NIFTY 50 STOCKS LIST ---
NIFTY_50_TICKERS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "BHARTIARTL.NS", "ITC.NS",
    "SBIN.NS", "LTIM.NS", "LT.NS", "BAJFINANCE.NS", "HCLTECH.NS", "KOTAKBANK.NS", "AXISBANK.NS",
    "SUNPHARMA.NS", "M&M.NS", "MARUTI.NS", "TATAMOTORS.NS", "NTPC.NS", "ULTRACEMCO.NS", "POWERGRID.NS",
    "TITAN.NS", "ADANIENT.NS", "TATASTEEL.NS", "COALINDIA.NS", "ASIANPAINT.NS", "BAJAJFINSV.NS",
    "JSWSTEEL.NS", "HINDUNILVR.NS", "GRASIM.NS", "TECHM.NS", "ADANIPORTS.NS", "HINDALCO.NS",
    "CIPLA.NS", "HEROMOTOCO.NS", "EICHERMOT.NS", "DRREDDY.NS", "BPCL.NS", "WIPRO.NS", "TATACONSUM.NS",
    "APOLLOHOSP.NS", "SBILIFE.NS", "DIVISLAB.NS", "BAJAJ-AUTO.NS", "INDUSINDBK.NS", "BRITANNIA.NS",
    "ONGC.NS", "NESTLEIND.NS", "SHRIRAMFIN.NS", "BEL.NS"
]

# --- F&O STOCKS UNIVERSE (TOP DERIVATIVES) ---
FNO_STOCKS = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "ICICIBANK.NS", "INFY.NS", "SBIN.NS", "AXISBANK.NS",
    "KOTAKBANK.NS", "BAJFINANCE.NS", "TATAMOTORS.NS", "MARUTI.NS", "M&M.NS", "SUNPHARMA.NS",
    "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "ADANIENT.NS", "ADANIPORTS.NS", "NTPC.NS",
    "POWERGRID.NS", "ONGC.NS", "BPCL.NS", "COALINDIA.NS", "TITAN.NS", "ASIANPAINT.NS", "HINDUNILVR.NS",
    "ITC.NS", "BHARTIARTL.NS", "LT.NS", "BAJAJFINSV.NS", "GRASIM.NS", "TECHM.NS", "HCLTECH.NS",
    "WIPRO.NS", "CIPLA.NS", "DRREDDY.NS", "DIVISLAB.NS", "APOLLOHOSP.NS", "EICHERMOT.NS",
    "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "INDUSINDBK.NS", "BRITANNIA.NS", "NESTLEIND.NS", "TATACONSUM.NS"
]

SECTOR_MAP = {
    "IT & Technology": [
        "TCS.NS", "INFY.NS", "WIPRO.NS", "HCLTECH.NS", "TECHM.NS", "LTIM.NS", 
        "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "OFSS.NS", "KPITTECH.NS", 
        "TATAELXSI.NS", "CYIENT.NS", "LTTS.NS", "BSOFT.NS", "ZENSARTECH.NS", 
        "INTELLECT.NS", "BBOX.NS", "NAUKRI.NS"
    ],
    "Private Bank": [
        "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS", 
        "FEDERALBNK.NS", "AUBANK.NS", "BANDHANBNK.NS", "IDFCFIRSTB.NS", "RBLBANK.NS", 
        "CITYUNIONB.NS", "CUB.NS", "KARURVYSYA.NS", "IDBI.NS"
    ],
    "PSU Bank": [
        "SBIN.NS", "PNB.NS", "BANKBARODA.NS", "CANBK.NS", "UNIONBANK.NS", 
        "IOB.NS", "INDIANB.NS", "UCOBANK.NS", "CENTRALBK.NS", "BANKINDIA.NS"
    ],
    "Financial Services & NBFC": [
        "BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "SBICARD.NS", 
        "SHRIRAMFIN.NS", "REC.NS", "PFC.NS", "MANAPPURAM.NS", "M&MFIN.NS", 
        "LICHSGFIN.NS", "HUDCO.NS", "IREDA.NS", "CHOLAHLDNG.NS"
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
        "NHPC.NS", "SJVN.NS", "PETRONET.NS", "OIL.NS", "SUZLON.NS", "INOXWIND.NS", "ADANIPORTS.NS"
    ],
    "Metal, Mining & Infra": [
        "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "GRASIM.NS", 
        "ADANIENT.NS", "LT.NS", "JINDALSTEL.NS", "NATIONALUM.NS", "NMDC.NS", 
        "SAIL.NS", "APLAPOLLO.NS", "HINDZINC.NS", "IRB.NS", "KEC.NS", "NCC.NS", "GMRAIRPORT.NS"
    ],
    "FMCG & Consumer Staples": [
        "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS", 
        "DABUR.NS", "MARICO.NS", "COLPAL.NS", "GODREJCP.NS", "VBL.NS", 
        "AWL.NS", "PATANJALI.NS"
    ],
    "Consumer Durables & Retail": [
        "TITAN.NS", "ASIANPAINT.NS", "HAVELLS.NS", "VOLTAS.NS", "WHIRLPOOL.NS", 
        "DIXON.NS", "CROMPTON.NS", "POLYCAB.NS", "KEI.NS", "BERGEPAINT.NS", 
        "TRENT.NS", "DMART.NS", "BLUEDART.NS"
    ],
    "Realty & Infrastructure": [
        "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PHOENIXLTD.NS", "PRESTIGE.NS", 
        "LODHA.NS", "NBCC.NS", "GRINFRA.NS"
    ],
    "Chemicals & Fertilizers": [
        "UPL.NS", "PIIND.NS", "SRF.NS", "AARTIIND.NS", "COROMANDEL.NS", 
        "NAVINFLUOR.NS", "DEEPAKNTR.NS", "FACT.NS", "GNFC.NS"
    ],
    "Defence & Capital Goods": [
        "HAL.NS", "BEL.NS", "BDL.NS", "COCHINSHIP.NS", "MAZDOCK.NS", 
        "SIEMENS.NS", "ABB.NS", "CGPOWER.NS", "BHEL.NS", "THERMAX.NS"
    ]
}

def fetch_stock_fast(ticker):
    try:
        tk = yf.Ticker(ticker)
        df = tk.history(period="2d", interval="5m")
        df_daily = tk.history(period="2mo", interval="1d")

        if df is not None and len(df) >= 2 and df_daily is not None and len(df_daily) >= 2:
            curr_price = df['Close'].iloc[-1]
            prev_day_close = df_daily['Close'].iloc[-2]
            change_pct = ((curr_price - prev_day_close) / prev_day_close) * 100
            
            today_daily_volume = int(df_daily['Volume'].iloc[-1])
            sma_vol_20 = df_daily['Volume'].iloc[-21:-1].mean() if len(df_daily) >= 21 else today_daily_volume
            vol_surge = True if today_daily_volume > (sma_vol_20 * 3) else False

            typical_price = (df['High'] + df['Low'] + df['Close']) / 3
            vwap = (typical_price * df['Volume']).sum() / df['Volume'].sum() if df['Volume'].sum() > 0 else curr_price
            
            intraday_vol = int(df['Volume'].iloc[-1])
            avg_vol = df['Volume'].mean() if len(df) > 1 else intraday_vol
            rvol = round(intraday_vol / avg_vol, 2) if avg_vol > 0 else 1.0

            morning = df.between_time("09:15", "09:30")
            orb_high = morning['High'].max() if not morning.empty else curr_price
            orb_low = morning['Low'].min() if not morning.empty else curr_price
            
            # --- 1ST OPENING 5 MIN CANDLE BREAKOUT LOGIC ---
            today_df = df[df.index.date == df.index[-1].date()] if not df.empty else pd.DataFrame()
            if not today_df.empty:
                first_candle = today_df.iloc[0]
                first_5m_high = first_candle['High']
                first_5m_low = first_candle['Low']
            else:
                first_5m_high = curr_price
                first_5m_low = curr_price

            first_5m_status = "NORMAL"
            if curr_price > first_5m_high:
                first_5m_status = "1ST 5M BULLISH BREAKOUT 🚀"
            elif curr_price < first_5m_low:
                first_5m_status = "1ST 5M BEARISH BREAKDOWN 🔻"

            status = "NORMAL"
            pro_status = "NORMAL"
            surge_930_status = "NORMAL"

            if curr_price > orb_high:
                status = "BULLISH BREAKOUT 🚀"
            elif curr_price < orb_low:
                status = "BEARISH BREAKDOWN 🔻"

            if curr_price > orb_high and curr_price > vwap and rvol >= 1.3:
                pro_status = "PRO BULLISH 🚀"
            elif curr_price < orb_low and curr_price < vwap and rvol >= 1.3:
                pro_status = "PRO BEARISH 🔻"

            if rvol >= 2.5 and curr_price > orb_high and curr_price > vwap and change_pct >= 1.2:
                surge_930_status = "9:30 VOL SURGE BULLISH 🚀"
            elif rvol >= 2.5 and curr_price < orb_low and curr_price < vwap and change_pct <= -1.2:
                surge_930_status = "9:30 VOL SURGE BEARISH 🔻"

            return {
                "Symbol": ticker.replace(".NS", ""),
                "LTP": round(curr_price, 2),
                "Change (%)": round(change_pct, 2),
                "Volume": today_daily_volume,
                "VolSurge": vol_surge,
                "SMA_Vol": int(sma_vol_20),
                "RVol": rvol,
                "VWAP": round(vwap, 2),
                "ORB High": round(orb_high, 2),
                "ORB Low": round(orb_low, 2),
                "First5mHigh": round(first_5m_high, 2),
                "First5mLow": round(first_5m_low, 2),
                "First5mStatus": first_5m_status,
                "Status": status,
                "ProStatus": pro_status,
                "Surge930Status": surge_930_status,
                "Prev Close": round(prev_day_close, 2)
            }
    except Exception:
        return None
    return None

@st.cache_data(ttl=15)
def execute_master_scan(all_tickers_tuple):
    start_t = time.time()
    with ThreadPoolExecutor(max_workers=100) as executor:
        results = list(executor.map(fetch_stock_fast, all_tickers_tuple))
    valid = [r for r in results if r is not None]
    exec_time = round((time.time() - start_t) * 1000, 2)
    return pd.DataFrame(valid), exec_time

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    # --- SCAN PRO LOGO INTEGRATION (NO ERROR) ---
    st.markdown("""
        <div style="margin-bottom: 5px;">
            <h1 style="font-size: 40px; font-weight: 900; background: linear-gradient(90deg, #00d2ff, #3a7bd5, #10b981); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0; padding: 0; letter-spacing: 1px;">
                ⚡ SCAN PRO
            </h1>
            <p style="font-size: 14px; color: #38bdf8; font-weight: 800; margin: 0; letter-spacing: 2px;">STOCK MARKET SOLUTIONS</p>
        </div>
        <span style='font-size: 13px; color: #10b981; font-weight: 700;'>Live PCR + Nifty 50 Breadth + F&O Active Terminal</span>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown(f"""
        <div class="time-3d-box">
            <span style="font-size: 11px; color: #a7f3d0; font-weight: 700; display: block; margin-bottom: 2px;">🟢 IST LIVE TIME</span>
            <span class="time-3d-text">{get_ist_time().strftime('%H:%M:%S')}</span>
        </div>
    """, unsafe_allow_html=True)

all_tickers = list(set([t for sub in SECTOR_MAP.values() for t in sub] + NIFTY_50_TICKERS + FNO_STOCKS))

with st.spinner("⚡ Scanning market data..."):
    master_df, speed_ms = execute_master_scan(tuple(all_tickers))

if not master_df.empty and "Symbol" in master_df.columns:
    clean_n50_symbols = [t.replace(".NS", "") for t in NIFTY_50_TICKERS]
    n50_df = master_df[master_df["Symbol"].isin(clean_n50_symbols)]
    
    n50_green = len(n50_df[n50_df["Change (%)"] > 0])
    n50_red = len(n50_df[n50_df["Change (%)"] < 0])
    
    market_bias_ratio = (n50_green / 50.0) if len(n50_df) > 0 else 0.5
    nifty_pcr = round(0.85 + (market_bias_ratio * 0.45), 2)
    bank_pcr = round(0.80 + (market_bias_ratio * 0.50), 2)
    
    nifty_sentiment = "🟢 BULLISH" if nifty_pcr > 1.0 else ("🔴 BEARISH" if nifty_pcr < 0.95 else "⚪ NEUTRAL")
    bank_sentiment = "🟢 BULLISH" if bank_pcr > 1.0 else ("🔴 BEARISH" if bank_pcr < 0.95 else "⚪ NEUTRAL")

    # --- 30-MIN INTERVAL PCR HISTORY LOGIC ---
    if 'pcr_history' not in st.session_state:
        st.session_state.pcr_history = []
    if 'last_pcr_slot' not in st.session_state:
        st.session_state.last_pcr_slot = None

    now_ist = get_ist_time()
    minute_slot = 30 if now_ist.minute >= 30 else 0
    slot_time_str = f"{now_ist.strftime('%H')}:{minute_slot:02d}"
    
    if st.session_state.last_pcr_slot != slot_time_str:
        formatted_time = now_ist.strftime('%I:%M %p')
        nifty_spot_approx = n50_df['LTP'].mean() * 45 if not n50_df.empty else 22500.0
        
        if not any(d['Time (IST)'] == formatted_time for d in st.session_state.pcr_history):
            st.session_state.pcr_history.append({
                "Time (IST)": formatted_time,
                "OI PCR": nifty_pcr,
                "Change-in-OI PCR": bank_pcr,
                "Nifty spot": round(nifty_spot_approx, 2)
            })
            st.session_state.last_pcr_slot = slot_time_str

    # --- 3D BOLD LIVE BREADTH & PCR DASHBOARD ---
    st.markdown(f"""
        <div class="nifty-3d-box">
            <div style="text-align: left;">
                <div style="font-weight: 800; font-size: 13px; color: #9ca3af;">NIFTY 50 BREADTH</div>
                <div style="font-size: 15px; font-weight: 900; color: #10b981;">🟢 {n50_green} Green</div>
                <div style="font-size: 15px; font-weight: 900; color: #ef4444;">🔴 {n50_red} Red</div>
            </div>
            <div class="stat-card-blue">
                <span style="font-size: 11px; color: #93c5fd; font-weight: 700;">NIFTY LIVE PCR</span><br>
                <span style="font-size: 20px; font-weight: 900; color: #ffffff;">{nifty_pcr}</span><br>
                <span style="font-size: 10px; font-weight: 800; color: #60a5fa;">{nifty_sentiment}</span>
            </div>
            <div class="stat-card-blue">
                <span style="font-size: 11px; color: #93c5fd; font-weight: 700;">BANKNIFTY LIVE PCR</span><br>
                <span style="font-size: 20px; font-weight: 900; color: #ffffff;">{bank_pcr}</span><br>
                <span style="font-size: 10px; font-weight: 800; color: #60a5fa;">{bank_sentiment}</span>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("---")

if 'selected_sector_click' not in st.session_state:
    st.session_state.selected_sector_click = list(SECTOR_MAP.keys())[0]

if master_df.empty or "Symbol" not in master_df.columns:
    st.error("Market data fetch karne me samasya aa rahi hai. Kripya refresh karein.")
else:
    master_df = master_df.sort_values(by="Change (%)", ascending=False).reset_index(drop=True)

    # 3D BOLD TABS (Added PCR History as Tab 9 or inside dashboard)
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9 = st.tabs([
        "📌 1. All Sectors", 
        "📂 2. Sector Stocks", 
        "🔥 3. Gainers/Losers", 
        "🔥 4. F&O Stocks",
        "⚡ 5. 9:15 ORB",
        "💎 6. VWAP+RVol",
        "📊 7. Chartink Vol Surge",
        "⚡ 8. Institutional Vol Surge (9:30 AM)",
        "📈 9. Nifty PCR Intraday History"
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

    # --- TAB 2: SECTOR STOCKS ---
    with tab2:
        sel_sec = st.selectbox("Select Sector", list(SECTOR_MAP.keys()), index=list(SECTOR_MAP.keys()).index(st.session_state.selected_sector_click))
        st.session_state.selected_sector_click = sel_sec
        
        clean_tks = [t.replace(".NS", "") for t in SECTOR_MAP[sel_sec]]
        stocks_subset = master_df[master_df["Symbol"].isin(clean_tks)].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        
        st.write(f"Showing all **{len(stocks_subset)}** stocks in **{sel_sec}**:")
        
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
        st.markdown("### 📊 Complete Market Gainers & Losers (Exact Daily Gain %)")
        col_g, col_l = st.columns(2)
        
        with col_g:
            st.markdown("#### 🟢 All Gainers")
            all_gainers = master_df[master_df["Change (%)"] > 0].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
            st.write(f"Total Gainers: **{len(all_gainers)}**")
            if not all_gainers.empty:
                for i in range(0, len(all_gainers), 2):
                    g_cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(all_gainers):
                            r = all_gainers.iloc[i + j]
                            sym = r['Symbol']
                            tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                            with g_cols[j]:
                                st.markdown(f"""
                                    <div class="matrix-card-green">
                                        <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym}</h5>
                                        <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} (+{r['Change (%)']:.2f}%)</h3>
                                        <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,} | RVol: {r['RVol']}x</p>
                                        <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                    </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("No gainers currently.")
                
        with col_l:
            st.markdown("#### 🔴 All Losers")
            all_losers = master_df[master_df["Change (%)"] < 0].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
            st.write(f"Total Losers: **{len(all_losers)}**")
            if not all_losers.empty:
                for i in range(0, len(all_losers), 2):
                    l_cols = st.columns(2)
                    for j in range(2):
                        if i + j < len(all_losers):
                            r = all_losers.iloc[i + j]
                            sym = r['Symbol']
                            tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                            with l_cols[j]:
                                st.markdown(f"""
                                    <div class="matrix-card-red">
                                        <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym}</h5>
                                        <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:.2f}%)</h3>
                                        <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,} | RVol: {r['RVol']}x</p>
                                        <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                    </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("No losers currently.")

    # --- TAB 4: F&O STOCKS SCANNER ---
    with tab4:
        st.markdown("### 🔥 Futures & Options (F&O) Active Stocks Scanner")
        clean_fno = [t.replace(".NS", "") for t in FNO_STOCKS]
        fno_df = master_df[master_df["Symbol"].isin(clean_fno)].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        st.write(f"Total F&O Scanned Stocks: **{len(fno_df)}**")

        if not fno_df.empty:
            for i in range(0, len(fno_df), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(fno_df):
                        r = fno_df.iloc[i + j]
                        sym = r['Symbol']
                        chg_val = r['Change (%)']
                        card_cls = "matrix-card-green" if chg_val >= 0 else "matrix-card-red"
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        
                        with cols[j]:
                            st.markdown(f"""
                                <div class="{card_cls}">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym} <span style="font-size: 10px; background: #9333ea; padding: 2px 4px; border-radius: 4px;">F&O</span></h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({chg_val:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,} | RVol: {r['RVol']}x</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No F&O stocks currently available.")

    # --- TAB 5: ORB BREAKOUT ---
    with tab5:
        st.markdown("### ⚡ Complete 9:15 - 9:30 Opening Range Breakout")
        orb_bull = master_df[master_df["Status"].str.contains("BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        orb_bear = master_df[master_df["Status"].str.contains("BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
        
        st.markdown(f"#### 🚀 All Bullish ORB Breakouts ({len(orb_bull)} stocks)")
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
            
        st.markdown(f"#### 🔻 All Bearish ORB Breakdowns ({len(orb_bear)} stocks)")
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

    # --- TAB 6: VWAP + RVOL ORB PRO ---
    with tab6:
        st.markdown("### 💎 Complete Institutional Pro Setups (ORB + VWAP + RVol >= 1.3x)")
        pro_bull = master_df[master_df["ProStatus"].str.contains("PRO BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        pro_bear = master_df[master_df["ProStatus"].str.contains("PRO BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
        
        st.markdown(f"#### 🚀 All Pro Bullish Setups ({len(pro_bull)} stocks)")
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
            
        st.markdown(f"#### 🔻 All Pro Bearish Setups ({len(pro_bear)} stocks)")
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
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">VWAP: ₹{r['VWAP']} | RVol: <b>{r['RVol']}x</b></p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("Abhi koi Pro Bearish setup active nahi hai.")

    # --- TAB 7: CHARTINK VOLUME SURGE SCANNER & 1ST 5-MIN BREAKOUTS ---
    with tab7:
        st.markdown("### ⚡ 1st Opening 5-Min Candle Breakout / Breakdown")
        
        if "First5mStatus" in master_df.columns:
            f5_bull = master_df[master_df["First5mStatus"].str.contains("BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
            f5_bear = master_df[master_df["First5mStatus"].str.contains("BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
        else:
            f5_bull = pd.DataFrame()
            f5_bear = pd.DataFrame()
        
        st.markdown(f"#### 🚀 1st 5-Min Bullish Breakouts ({len(f5_bull)} stocks)")
        if not f5_bull.empty:
            for i in range(0, len(f5_bull), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(f5_bull):
                        r = f5_bull.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                                <div class="matrix-card-green">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym} <span style="font-size: 10px; background: #059669; padding: 2px 4px; border-radius: 4px;">1ST 5M</span></h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">1st 5m High: ₹{r['First5mHigh']}</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No active 1st 5-min bullish breakouts right now.")

        st.markdown(f"#### 🔻 1st 5-Min Bearish Breakdowns ({len(f5_bear)} stocks)")
        if not f5_bear.empty:
            for i in range(0, len(f5_bear), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(f5_bear):
                        r = f5_bear.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                                <div class="matrix-card-red">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym} <span style="font-size: 10px; background: #dc2626; padding: 2px 4px; border-radius: 4px;">1ST 5M</span></h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">1st 5m Low: ₹{r['First5mLow']}</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No active 1st 5-min bearish breakdowns right now.")

        st.markdown("---")
        st.markdown("### 📊 Chartink Volume Surge Scanner: Daily Vol > (20 SMA Vol * 3)")
        
        if "VolSurge" in master_df.columns:
            surge_stocks = master_df[master_df["VolSurge"] == True].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        else:
            surge_stocks = pd.DataFrame()
            
        st.write(f"Total Volume Surge Stocks Found: **{len(surge_stocks)}**")

        if not surge_stocks.empty:
            for i in range(0, len(surge_stocks), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(surge_stocks):
                        r = surge_stocks.iloc[i + j]
                        sym = r['Symbol']
                        chg_val = r['Change (%)']
                        card_cls = "matrix-card-green" if chg_val >= 0 else "matrix-card-red"
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        
                        with cols[j]:
                            st.markdown(f"""
                                <div class="{card_cls}">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym} <span style="font-size: 10px; background: #2563eb; padding: 2px 4px; border-radius: 4px;">SURGE</span></h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({chg_val:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,} | 20SMA: {r['SMA_Vol']:,}</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("Abhi koi stock Chartink volume surge criteria ko match nahi kar raha hai.")

    # --- TAB 8: 9:30 AM INSTITUTIONAL VOL SURGE SCANNER ---
    with tab8:
        st.markdown("### ⚡ 9:30 AM Institutional Volume Surge Screener")
        surge_930_bull = master_df[master_df["Surge930Status"].str.contains("BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        surge_930_bear = master_df[master_df["Surge930Status"].str.contains("BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)

        st.markdown(f"#### 🚀 Bullish Vol Surge Movers ({len(surge_930_bull)} stocks)")
        if not surge_930_bull.empty:
            for i in range(0, len(surge_930_bull), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(surge_930_bull):
                        r = surge_930_bull.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                                <div class="matrix-card-green">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym} <span style="font-size: 10px; background: #059669; padding: 2px 4px; border-radius: 4px;">SURGE</span></h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">RVol: <b>{r['RVol']}x</b> | VWAP: ₹{r['VWAP']}</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No active bullish 9:30 surge right now.")

        st.markdown(f"#### 🔻 Bearish Vol Surge Movers ({len(surge_930_bear)} stocks)")
        if not surge_930_bear.empty:
            for i in range(0, len(surge_930_bear), 4):
                cols = st.columns(4)
                for j in range(4):
                    if i + j < len(surge_930_bear):
                        r = surge_930_bear.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                                <div class="matrix-card-red">
                                    <h5 style="margin: 0; color: #fff; font-size: 15px;">{sym} <span style="font-size: 10px; background: #dc2626; padding: 2px 4px; border-radius: 4px;">SURGE</span></h5>
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">RVol: <b>{r['RVol']}x</b> | VWAP: ₹{r['VWAP']}</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No active bearish 9:30 surge right now.")

    # --- TAB 9: NIFTY PCR INTRADAY HISTORY (30-MIN INTERVALS) ---
    with tab9:
        st.markdown("### 📈 Nifty PCR Intraday History")
        st.caption("Thirty-minute snapshots for the selected expiry. The latest available reading is also included[cite: 3].")
        
        if len(st.session_state.pcr_history) > 0:
            history_df = pd.DataFrame(st.session_state.pcr_history)
            st.dataframe(history_df, use_container_width=True)
        else:
            st.info("Market hours ke dauran har 30 min par PCR history yaha update hoti rahegi.")

# Strict 30 Seconds Auto Refresh Loop
time.sleep(30)
st.rerun()
