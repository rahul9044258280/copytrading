import streamlit as st
import pandas as pd
import requests
from datetime import datetime, timezone, timedelta
import time
import html
from concurrent.futures import ThreadPoolExecutor, as_completed
from itertools import repeat
from threading import local
from requests.adapters import HTTPAdapter

# --- IST TIMEZONE (UTC +5:30) ---
IST = timezone(timedelta(hours=5, minutes=30))

def get_ist_time():
    return datetime.now(IST)

# --- PAGE CONFIGURATION ---
st.set_page_config(
    page_title="SCAN PRO Stock Market Solutions",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- HIGH-PERFORMANCE CINEMATIC, 3D TABS & MARKET DASHBOARD CSS ---
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

/* 3D Box Container for Nifty 50 Breadth Summary */
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
.matrix-card-green h5, .matrix-card-red h5 {
    font-size: 18px !important;
    line-height: 1.25 !important;
    font-weight: 900 !important;
    letter-spacing: 0.15px !important;
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

# --- F&O STOCKS UNIVERSE ---
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
        "INTELLECT.NS", "BBOX.NS", "NAUKRI.NS", "MINDTREE.NS", "SONATSOFTW.NS",
        "TANLA.NS", "RATEGAIN.NS", "FSL.NS", "CAMS.NS", "LATENTVIEW.NS", "HAPPYFORGE.NS"
    ],
    "Private Bank": [
        "HDFCBANK.NS", "ICICIBANK.NS", "KOTAKBANK.NS", "AXISBANK.NS", "INDUSINDBK.NS",
        "FEDERALBNK.NS", "AUBANK.NS", "BANDHANBNK.NS", "IDFCFIRSTB.NS", "RBLBANK.NS",
        "CITYUNIONB.NS", "CUB.NS", "KARURVYSYA.NS", "IDBI.NS", "SOUTHBANK.NS",
        "J&KBANK.NS", "CSBBANK.NS", "DCBBANK.NS", "NAINITALBK.NS"
    ],
    "PSU Bank": [
        "SBIN.NS", "PNB.NS", "BANKBARODA.NS", "CANBK.NS", "UNIONBANK.NS",
        "IOB.NS", "INDIANB.NS", "UCOBANK.NS", "CENTRALBK.NS", "BANKINDIA.NS",
        "MAHABANK.NS", "PSB.NS"
    ],
    "Financial Services & NBFC": [
        "BAJFINANCE.NS", "BAJAJFINSV.NS", "CHOLAFIN.NS", "MUTHOOTFIN.NS", "SBICARD.NS",
        "SHRIRAMFIN.NS", "REC.NS", "PFC.NS", "MANAPPURAM.NS", "M&MFIN.NS",
        "LICHSGFIN.NS", "HUDCO.NS", "IREDA.NS", "CHOLAHLDNG.NS", "NIACL.NS",
        "GICRE.NS", "POLICYBZR.NS", "MUTHOOTMF.NS", "POONAWALLA.NS", "SUNDARMFIN.NS",
        "CANFINHOME.NS", "AAVAS.NS", "HOMEFIRST.NS", "CREDITACC.NS", "MASFIN.NS",
        "SBFC.NS", "UTIAMC.NS", "HDFCAMC.NS", "NAM-INDIA.NS", "ANGELONE.NS",
        "MCX.NS", "BSE.NS", "CDSL.NS", "IEX.NS", "MOTILOSAL.NS", "ICICIGI.NS",
        "ICICIPRULI.NS", "SBILIFE.NS", "HDFCLIFE.NS", "STARHEALTH.NS", "NYKAA.NS"
    ],
    "Automobile & Auto Ancillary": [
        "TATAMOTORS.NS", "M&M.NS", "MARUTI.NS", "BAJAJ-AUTO.NS", "HEROMOTOCO.NS",
        "EICHERMOT.NS", "TVSMOTOR.NS", "ASHOKLEY.NS", "BHARATFORG.NS", "MOTHERSON.NS",
        "BOSCHLTD.NS", "MRF.NS", "BALKRISIND.NS", "TIINDIA.NS", "ENDURANCE.NS",
        "UNOMINDA.NS", "SONACOMS.NS", "EXIDEIND.NS", "AMARAJABAT.NS", "FORCEMOT.NS",
        "SMLISUZU.NS", "ATULAUTO.NS", "JKTYRE.NS", "CEATLTD.NS", "APOLLOTYRE.NS",
        "MAHSCOOTER.NS", "SUBROS.NS", "FIEMIND.NS", "GARFIBRES.NS"
    ],
    "Pharmaceuticals & Biotech": [
        "SUNPHARMA.NS", "DRREDDY.NS", "CIPLA.NS", "APOLLOHOSP.NS", "DIVISLAB.NS",
        "LUPIN.NS", "ALKEM.NS", "TORNTPHARM.NS", "MANKIND.NS", "ZYDUSLIFE.NS",
        "GLENMARK.NS", "GRANULES.NS", "AUROPHARMA.NS", "IPCALAB.NS", "BIOCON.NS",
        "AJANTPHARM.NS", "GLAXO.NS", "PFIZER.NS", "SANOFI.NS", "ABBOTINDIA.NS",
        "NATCOPHARM.NS", "LAURUSLABS.NS", "JBCHEPHARM.NS", "ERIS.NS", "LALPATHLAB.NS",
        "METROPOLIS.NS", "THYROCARE.NS", "POLYMED.NS", "STAR.NS", "FDC.NS"
    ],
    "Energy, Oil & Power": [
        "RELIANCE.NS", "ONGC.NS", "BPCL.NS", "IOC.NS", "POWERGRID.NS",
        "NTPC.NS", "TATAPOWER.NS", "ADANIGREEN.NS", "GAIL.NS", "COALINDIA.NS",
        "NHPC.NS", "SJVN.NS", "PETRONET.NS", "OIL.NS", "SUZLON.NS", "INOXWIND.NS",
        "ADANIPORTS.NS", "TORNTPOWER.NS", "CESC.NS", "JSWENERGY.NS", "ADANIPOWER.NS",
        "WAAREE.NS", "BORORENEW.NS", "IDEAFORGE.NS", "SWANENERGY.NS", "GIPCL.NS", "RPOWER.NS"
    ],
    "Metal, Mining & Infra": [
        "TATASTEEL.NS", "JSWSTEEL.NS", "HINDALCO.NS", "VEDL.NS", "GRASIM.NS",
        "ADANIENT.NS", "LT.NS", "JINDALSTEL.NS", "NATIONALUM.NS", "NMDC.NS",
        "SAIL.NS", "APLAPOLLO.NS", "HINDZINC.NS", "IRB.NS", "KEC.NS", "NCC.NS",
        "GMRAIRPORT.NS", "GALLANTT.NS", "JSL.NS", "RATNAMANI.NS", "WELCORP.NS",
        "JINDALSAW.NS", "ELECTCAST.NS", "GPIL.NS", "HIL.NS", "GRAVITA.NS",
        "MOIL.NS", "KALYANKJIL.NS", "HEG.NS", "GRAPHITE.NS", "SHARDACROP.NS",
        "GMRINFRA.NS", "PNCINFRA.NS", "HGINFRA.NS", "GRINFRA.NS", "IRCON.NS",
        "RVNL.NS", "NBCC.NS", "RITES.NS", "ITI.NS", "SCI.NS", "COCHINSHIP.NS",
        "MAZDOCK.NS", "GRSE.NS", "DATAPATTNS.NS", "PARAS.NS"
    ],
    "FMCG & Consumer Staples": [
        "HINDUNILVR.NS", "ITC.NS", "NESTLEIND.NS", "BRITANNIA.NS", "TATACONSUM.NS",
        "DABUR.NS", "MARICO.NS", "COLPAL.NS", "GODREJCP.NS", "VBL.NS",
        "AWL.NS", "PATANJALI.NS", "EMAMI.NS", "RADICO.NS", "UBL.NS", "MCDOWELL-N.NS",
        "GILLETTE.NS", "PGHH.NS", "JYOTHYLAB.NS", "BAJAJCON.NS", "BALRAMCHIN.NS", "TRIVENI.NS"
    ],
    "Consumer Durables & Retail": [
        "TITAN.NS", "ASIANPAINT.NS", "HAVELLS.NS", "VOLTAS.NS", "WHIRLPOOL.NS",
        "DIXON.NS", "CROMPTON.NS", "POLYCAB.NS", "KEI.NS", "BERGEPAINT.NS",
        "TRENT.NS", "DMART.NS", "BLUEDART.NS", "AMBER.NS", "BLUESTARCO.NS",
        "KAJARIACER.NS", "CERA.NS", "CENTURYPLY.NS", "GREENPANEL.NS", "CAMPUS.NS",
        "BATAINDIA.NS", "RELAXO.NS", "PAGEIND.NS", "ABFRL.NS", "VMART.NS"
    ],
    "Realty & Infrastructure": [
        "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PHOENIXLTD.NS", "PRESTIGE.NS",
        "LODHA.NS", "BRIGADE.NS", "SOBHA.NS", "MAHLIFE.NS", "ANANTRAJ.NS", "ASHIANA.NS"
    ],
    "Chemicals & Fertilizers": [
        "UPL.NS", "PIIND.NS", "SRF.NS", "AARTIIND.NS", "COROMANDEL.NS",
        "NAVINFLUOR.NS", "DEEPAKNTR.NS", "FACT.NS", "GNFC.NS", "CHAMBLFERT.NS",
        "GSFC.NS", "RCF.NS", "TATACHEM.NS", "ALKYLAMINE.NS", "BALAMINES.NS",
        "CLEAN.NS", "FINEORG.NS", "FLUOROCHEM.NS", "NEOGEN.NS", "SUDARSCHEM.NS",
        "ATUL.NS", "BASF.NS", "NOCIL.NS", "SUMICHEM.NS", "ANUP.NS"
    ],
    "Defence & Capital Goods": [
        "HAL.NS", "BEL.NS", "BDL.NS", "COCHINSHIP.NS", "MAZDOCK.NS",
        "SIEMENS.NS", "ABB.NS", "CGPOWER.NS", "BHEL.NS", "THERMAX.NS",
        "CUMMINSIND.NS", "ESCORTS.NS", "SCHAEFFLER.NS", "TIMKEN.NS", "SKFINDIA.NS",
        "VAIBHAVGBL.NS", "TRIDENT.NS", "KPRMILL.NS", "WELSPUNLIV.NS"
    ]
}


# --- EXPANDED NSE CASH-MARKET UNIVERSE (500+ TARGET) ---
# Additional listed NSE equity symbols grouped by theme. All are added to the
# shared master universe, so every scanner tab can use the same expanded data.
EXPANDED_SECTOR_MAP = {
    "Jio & Telecom Ecosystem": [
        "JIOFIN.NS", "RELIANCE.NS", "BHARTIARTL.NS", "IDEA.NS", "INDUSTOWER.NS",
        "BHARTIHEXA.NS", "STLTECH.NS", "TEJASNET.NS", "HFCL.NS", "ITI.NS",
        "RAILTEL.NS", "TATACOMM.NS", "ROUTE.NS", "TANLA.NS", "ONMOBILE.NS"
    ],
    "Railways & Transportation": [
        "RVNL.NS", "IRFC.NS", "IRCON.NS", "RITES.NS", "RAILTEL.NS", "TITAGARH.NS",
        "JWL.NS", "TEXRAIL.NS", "CONCOR.NS", "BLUEDART.NS", "TCI.NS", "GATEWAY.NS",
        "ALLCARGO.NS", "VRLLOG.NS", "MAHLOG.NS", "DELHIVERY.NS", "TRITURBINE.NS",
        "BEML.NS", "CONCORDBIO.NS", "SCI.NS", "GESHIP.NS", "GPPL.NS", "JSWINFRA.NS",
        "ADANIPORTS.NS", "EICHERMOT.NS", "ASHOKLEY.NS", "JAMNAAUTO.NS", "SCHNEIDER.NS"
    ],
    "Defence & Aerospace": [
        "HAL.NS", "BEL.NS", "BDL.NS", "MAZDOCK.NS", "GRSE.NS", "COCHINSHIP.NS",
        "DATAPATTNS.NS", "PARAS.NS", "MTARTECH.NS", "ZENTEC.NS", "IDEAFORGE.NS",
        "DCXINDIA.NS", "AEROFLEX.NS", "UNIMECH.NS", "SOLARINDS.NS", "MIDHANI.NS",
        "ASTRAMICRO.NS", "AVANTEL.NS", "BHEL.NS", "BEML.NS"
    ],
    "Power, Renewable & Utilities": [
        "TATAPOWER.NS", "ADANIGREEN.NS", "ADANIPOWER.NS", "JSWENERGY.NS", "NHPC.NS",
        "SJVN.NS", "CESC.NS", "TORNTPOWER.NS", "GVT&D.NS", "INOXWIND.NS", "SUZLON.NS",
        "WAAREEENER.NS", "KPIGREEN.NS", "BORORENEW.NS", "WEBELSOLAR.NS",
        "VIKRAMSOLR.NS", "ACMESOLAR.NS", "NTPCGREEN.NS", "INOXGREEN.NS", "GENUSPOWER.NS",
        "KALYANKJIL.NS", "TRANSRAILL.NS", "CGPOWER.NS", "HPL.NS", "ECLERX.NS"
    ],
    "Banks, Finance & Insurance": [
        "BANKINDIA.NS", "MAHABANK.NS", "UCOBANK.NS", "CENTRALBK.NS", "IOB.NS", "INDIANB.NS",
        "UNIONBANK.NS", "CANBK.NS", "PNB.NS", "BANKBARODA.NS", "IDFCFIRSTB.NS", "FEDERALBNK.NS",
        "BANDHANBNK.NS", "AUBANK.NS", "RBLBANK.NS", "YESBANK.NS", "J&KBANK.NS", "KARURVYSYA.NS",
        "CUB.NS", "SOUTHBANK.NS", "DCBBANK.NS", "CSBBANK.NS", "EQUITASBNK.NS", "UJJIVANSFB.NS",
        "CREDITACC.NS", "MUTHOOTFIN.NS", "MANAPPURAM.NS", "CHOLAFIN.NS", "POONAWALLA.NS",
        "SUNDARMFIN.NS", "M&MFIN.NS", "L&TFH.NS", "REC.NS", "PFC.NS", "HUDCO.NS", "IREDA.NS",
        "HDFCLIFE.NS", "ICICIPRULI.NS", "ICICIGI.NS", "NIACL.NS", "GICRE.NS", "STARHEALTH.NS"
    ],
    "Industrial, Engineering & Capital Goods": [
        "SIEMENS.NS", "ABB.NS", "THERMAX.NS", "CUMMINSIND.NS", "KEC.NS", "KALPATPOWR.NS",
        "PRAJIND.NS", "ELECON.NS", "GRINDWELL.NS", "AIAENG.NS", "TIMKEN.NS", "SCHAEFFLER.NS",
        "SKFINDIA.NS", "CARBORUNIV.NS", "TRIVENI.NS", "KIRloskar.NS", "KIRLOSBROS.NS",
        "VGUARD.NS", "FINCABLES.NS", "POLYCAB.NS", "KEI.NS", "APARINDS.NS", "RRKABEL.NS",
        "HAVELLS.NS", "VOLTAS.NS", "BLUESTARCO.NS", "DIXON.NS", "AMBER.NS", "KAYNES.NS",
        "NETWEB.NS", "E2E.NS", "LATENTVIEW.NS", "DATAMATICS.NS", "AFFLE.NS"
    ],
    "Healthcare, Pharma & Diagnostics": [
        "LUPIN.NS", "ALKEM.NS", "TORNTPHARM.NS", "MANKIND.NS", "ZYDUSLIFE.NS", "GLENMARK.NS",
        "GRANULES.NS", "AUROPHARMA.NS", "IPCALAB.NS", "BIOCON.NS", "AJANTPHARM.NS", "LAURUSLABS.NS",
        "JBCHEPHARM.NS", "NATCOPHARM.NS", "ERIS.NS", "ABBOTINDIA.NS", "PFIZER.NS", "SANOFI.NS",
        "GLAXO.NS", "LALPATHLAB.NS", "METROPOLIS.NS", "THYROCARE.NS", "VIJAYA.NS", "KIMS.NS",
        "RAINBOW.NS", "MAXHEALTH.NS", "FORTIS.NS", "MEDANTA.NS", "NH.NS", "ASTERDM.NS",
        "SYNGENE.NS", "SUVENPHAR.NS", "JUBLPHARMA.NS", "CAPLIPOINT.NS"
    ],
    "Consumer, Retail & Lifestyle": [
        "TRENT.NS", "DMART.NS", "NYKAA.NS", "ABFRL.NS", "VMART.NS", "SHOPERSTOP.NS",
        "KALYANKJIL.NS", "JUBLFOOD.NS", "DEVYANI.NS", "WESTLIFE.NS", "BIKAJI.NS", "PATANJALI.NS",
        "DABUR.NS", "MARICO.NS", "COLPAL.NS", "GODREJCP.NS", "VBL.NS", "EMAMILTD.NS",
        "RADICO.NS", "UBL.NS", "MCDOWELL-N.NS", "GILLETTE.NS", "PGHH.NS", "JYOTHYLAB.NS",
        "BATAINDIA.NS", "RELAXO.NS", "PAGEIND.NS", "CAMPUS.NS", "KPRMILL.NS", "TRIDENT.NS",
        "WELSPUNLIV.NS", "VTL.NS", "GOKEX.NS", "RAYMOND.NS", "ARVIND.NS", "JINDALWORLD.NS"
    ],
    "Metals, Materials & Chemicals": [
        "VEDL.NS", "JINDALSTEL.NS", "NATIONALUM.NS", "NMDC.NS", "SAIL.NS", "HINDZINC.NS",
        "APLAPOLLO.NS", "JSL.NS", "RATNAMANI.NS", "WELCORP.NS", "JINDALSAW.NS", "GRAVITA.NS",
        "MOIL.NS", "HEG.NS", "GRAPHITE.NS", "HINDCOPPER.NS", "HINDALCO.NS", "TATASTEEL.NS",
        "JSWSTEEL.NS", "UPL.NS", "PIIND.NS", "SRF.NS", "AARTIIND.NS", "COROMANDEL.NS",
        "NAVINFLUOR.NS", "DEEPAKNTR.NS", "FACT.NS", "GNFC.NS", "CHAMBLFERT.NS", "GSFC.NS",
        "RCF.NS", "TATACHEM.NS", "ATUL.NS", "CLEAN.NS", "FINEORG.NS", "FLUOROCHEM.NS",
        "NEOGEN.NS", "SUDARSCHEM.NS", "NOCIL.NS", "SUMICHEM.NS", "ANUP.NS", "BALAMINES.NS"
    ],
    "Realty, Construction & Infrastructure": [
        "DLF.NS", "GODREJPROP.NS", "OBEROIRLTY.NS", "PHOENIXLTD.NS", "PRESTIGE.NS", "LODHA.NS",
        "BRIGADE.NS", "SOBHA.NS", "MAHLIFE.NS", "ANANTRAJ.NS", "ASHIANA.NS", "NBCC.NS",
        "NCC.NS", "IRB.NS", "PNCINFRA.NS", "HGINFRA.NS", "GRINFRA.NS", "KNRCON.NS",
        "ASHOKA.NS", "JKIL.NS", "DBL.NS", "HCC.NS", "RAMKY.NS", "MANINFRA.NS", "GPTINFRA.NS",
        "CAPACITE.NS", "AHLUCONT.NS", "ENGINERSIN.NS", "RITES.NS"
    ],
    "Technology, Media & Digital": [
        "MPHASIS.NS", "COFORGE.NS", "PERSISTENT.NS", "OFSS.NS", "KPITTECH.NS", "TATAELXSI.NS",
        "CYIENT.NS", "LTTS.NS", "BSOFT.NS", "ZENSARTECH.NS", "INTELLECT.NS", "SONATSOFTW.NS",
        "FSL.NS", "CAMS.NS", "HAPPYFORGE.NS", "NAUKRI.NS", "PVRINOX.NS", "SUNTV.NS",
        "ZEEL.NS", "NETWORK18.NS", "SAREGAMA.NS", "TIPSMUSIC.NS", "HATHWAY.NS", "DEN.NS",
        "DBCORP.NS", "JAGRAN.NS", "TVTODAY.NS", "INOXWIND.NS", "EASEMYTRIP.NS", "YATRA.NS"
    ]
}


# Additional liquid and widely followed NSE cash-market names.
MORE_NSE_TICKERS = [
    "ABCAPITAL.NS", "ABSLAMC.NS", "ADITYABIRLA.NS", "ABFRL.NS", "AETHER.NS", "AFFLE.NS",
    "AJMERA.NS", "ALOKINDS.NS", "AMBUJACEM.NS", "ANANDRATHI.NS", "ANGELONE.NS", "APLLTD.NS",
    "APTUS.NS", "ARE&M.NS", "ASAHIINDIA.NS", "ASHOKA.NS", "ASTRAL.NS", "ATGL.NS", "AUBANK.NS",
    "AVANTIFEED.NS", "AWL.NS", "BAJAJHLDNG.NS", "BALAMINES.NS", "BALRAMCHIN.NS", "BANDHANBNK.NS",
    "BANKBARODA.NS", "BATAINDIA.NS", "BAYERCROP.NS", "BEML.NS", "BHARATFORG.NS", "BIRLACORPN.NS",
    "BLUEDART.NS", "BLS.NS", "BOMDYEING.NS", "BOSCHLTD.NS", "BPCL.NS", "CAMS.NS", "CANFINHOME.NS",
    "CARBORUNIV.NS", "CASTROLIND.NS", "CCL.NS", "CDSL.NS", "CEATLTD.NS", "CENTRALBK.NS",
    "CENTURYPLY.NS", "CERA.NS", "CHALET.NS", "CHAMBLFERT.NS", "CHOLAHLDNG.NS", "CIEINDIA.NS",
    "CLEAN.NS", "COCHINSHIP.NS", "CREDITACC.NS", "CROMPTON.NS", "CSBBANK.NS", "CYIENT.NS",
    "DALBHARAT.NS", "DATAMATICS.NS", "DEEPAKFERT.NS", "DEEPAKNTR.NS", "DELHIVERY.NS", "DEVYANI.NS",
    "ECLERX.NS", "EIDPARRY.NS", "ELGIEQUIP.NS", "EMAMILTD.NS", "ENDURANCE.NS", "ENGINERSIN.NS",
    "EQUITASBNK.NS", "ERIS.NS", "EXIDEIND.NS", "FACT.NS", "FDC.NS", "FINCABLES.NS", "FINPIPE.NS",
    "FIVESTAR.NS", "FLUOROCHEM.NS", "FORTIS.NS", "GAIL.NS", "GARFIBRES.NS", "GICRE.NS",
    "GILLETTE.NS", "GLAND.NS", "GLAXO.NS", "GMMPFAUDLR.NS", "GNFC.NS", "GODFRYPHLP.NS",
    "GODREJIND.NS", "GODREJAGRO.NS", "GPIL.NS", "GRANULES.NS", "GRAPHITE.NS", "GRINDWELL.NS",
    "GSFC.NS", "GSPL.NS", "GUJGASLTD.NS", "HAPPSTMNDS.NS", "HATHWAY.NS", "HEG.NS", "HINDCOPPER.NS",
    "HINDPETRO.NS", "HINDZINC.NS", "HOMEFIRST.NS", "HUDCO.NS", "IDBI.NS", "IDFCFIRSTB.NS",
    "IIFL.NS", "INDIACEM.NS", "INDIAMART.NS", "INDIANB.NS", "INDIGO.NS", "INDUSTOWER.NS",
    "INOXWIND.NS", "INTELLECT.NS", "IOC.NS", "IRB.NS", "JBCHEPHARM.NS", "JINDALSAW.NS",
    "JKCEMENT.NS", "JKLAKSHMI.NS", "JKPAPER.NS", "JKTYRE.NS", "JSL.NS", "JUBLFOOD.NS",
    "JUSTDIAL.NS", "KAJARIACER.NS", "KANSAINER.NS", "KARURVYSYA.NS", "KEC.NS", "KFINTECH.NS",
    "KNRCON.NS", "KPITTECH.NS", "KRBL.NS", "LATENTVIEW.NS", "LEMONTREE.NS", "LICHSGFIN.NS",
    "LINDEINDIA.NS", "LODHA.NS", "LTTS.NS", "M&MFIN.NS", "MAHABANK.NS", "MAHSEAMLES.NS",
    "MANAPPURAM.NS", "MAPMYINDIA.NS", "MARICO.NS", "MASTEK.NS", "MAXHEALTH.NS", "MCX.NS",
    "METROPOLIS.NS", "MGL.NS", "MHRIL.NS", "MOTILALOFS.NS", "MRPL.NS", "MTARTECH.NS",
    "NATCOPHARM.NS", "NATIONALUM.NS", "NAVINFLUOR.NS", "NBCC.NS", "NCC.NS", "NETWORK18.NS",
    "NH.NS", "NIACL.NS", "NLCINDIA.NS", "NMDC.NS", "NOCIL.NS", "OIL.NS", "PAYTM.NS",
    "PFIZER.NS", "POLICYBZR.NS", "POLYMED.NS", "POONAWALLA.NS", "PRAJIND.NS", "PRESTIGE.NS",
    "QUESS.NS", "RADICO.NS", "RAILTEL.NS", "RAIN.NS", "RALLIS.NS", "RAMCOCEM.NS", "RATNAMANI.NS",
    "RBLBANK.NS", "RCF.NS", "REDINGTON.NS", "RELAXO.NS", "ROUTE.NS", "SANOFI.NS", "SAREGAMA.NS",
    "SCHNEIDER.NS", "SHRIRAMFIN.NS", "SONATSOFTW.NS", "STARHEALTH.NS", "SUNTV.NS", "SUPREMEIND.NS",
    "SUVENPHAR.NS", "SYMPHONY.NS", "TATACOMM.NS", "TATAELXSI.NS", "TEAMLEASE.NS", "TEJASNET.NS",
    "THERMAX.NS", "THYROCARE.NS", "TIMKEN.NS", "TIPSMUSIC.NS", "TORNTPOWER.NS", "TVTODAY.NS",
    "UJJIVANSFB.NS", "UNOMINDA.NS", "UTIAMC.NS", "VGUARD.NS", "VIJAYA.NS", "VOLTAS.NS",
    "VTL.NS", "WELCORP.NS", "WELSPUNLIV.NS", "WESTLIFE.NS", "WHIRLPOOL.NS", "YESBANK.NS",
    "ZENSARTECH.NS", "ZFCVINDIA.NS", "ZOMATO.NS", "ZYDUSLIFE.NS"
]


# Further diversified NSE names to provide a buffer for symbols temporarily
# unavailable from the public quote provider.
MORE_NSE_TICKERS += [
    "AARTIDRUGS.NS", "AARTIIND.NS", "ADVENZYMES.NS", "AKZOINDIA.NS", "ALIVUS.NS",
    "APCOTEXIND.NS", "ASHIANA.NS", "ASIANHOTNR.NS", "ASTRAZEN.NS", "BANARISUG.NS",
    "BECTORFOOD.NS", "BIRLAMONEY.NS", "BLISSGVS.NS", "BOROLTD.NS", "BRIGADE.NS",
    "CAMLINFINE.NS", "CAPLIPOINT.NS", "CARERATING.NS", "CELEBRITY.NS", "CENTURYPLY.NS",
    "CHEMPLASTS.NS", "CIGNITITEC.NS", "CONCOR.NS", "DATAPATTNS.NS", "DCMSHRIRAM.NS",
    "DHANUKA.NS", "DODLA.NS", "EDELWEISS.NS", "EMCURE.NS", "ETHOSLTD.NS",
    "FINEORG.NS", "GABRIEL.NS", "GALLANTT.NS", "GESHIP.NS", "GMDCLTD.NS",
    "GMRP&UI.NS", "GRSE.NS", "HBLENGINE.NS", "HIKAL.NS", "HINDWAREAP.NS",
    "IBREALEST.NS", "ICRA.NS", "IFBIND.NS", "INDIGOPNTS.NS", "INOXINDIA.NS",
    "INTELLECT.NS", "J&KBANK.NS", "JINDALSAW.NS", "JSWINFRA.NS", "KIRLOSBROS.NS",
    "KOLTEPATIL.NS", "KOPRAN.NS", "LAXMIMACH.NS", "MAHLIFE.NS", "MAHSEAMLES.NS",
    "MAZDOCK.NS", "MINDACORP.NS", "MOLDTKPAC.NS", "MOREPENLAB.NS", "MOTILALOFS.NS",
    "NAVA.NS", "NFL.NS", "ORIENTCEM.NS", "ORIENTELEC.NS", "PCBL.NS",
    "PITTIENG.NS", "PRICOLLTD.NS", "PRINCEPIPE.NS", "PRSMJOHNSN.NS", "RAYMONDLSL.NS",
    "RBA.NS", "ROSSARI.NS", "SAFARI.NS", "SANSERA.NS", "SHILPAMED.NS",
    "SHYAMMETL.NS", "SIGNATURE.NS", "SIS.NS", "SJS.NS", "STARCEMENT.NS",
    "STYRENIX.NS", "SUBROS.NS", "SUDARSCHEM.NS", "SWSOLAR.NS", "TARSONS.NS",
    "TCI.NS", "TCIEXP.NS", "TDPOWERSYS.NS", "THANGAMAYL.NS", "THOMASCOOK.NS",
    "TITAGARH.NS", "TRITURBINE.NS", "UDEMY.NS", "UNIPARTS.NS", "UTTAMSUGAR.NS",
    "VAKRANGEE.NS", "VARROC.NS", "VSTIND.NS", "ZENTEC.NS", "ZODIACLOTH.NS"
]


# Extra liquid NSE universe: all tabs use this same shared pool.
MORE_NSE_TICKERS += [
    "AAVAS.NS","ABREL.NS","ACE.NS","AEGISLOG.NS","AGI.NS","AJANTSOY.NS","ALKYLAMINE.NS",
    "AMRUTANJAN.NS","ANUP.NS","APOLLOTYRE.NS","ARVSMART.NS","ATUL.NS","BAJAJCON.NS","BALPHARMA.NS",
    "BASF.NS","BECTORFOOD.NS","BINDALAGRO.NS","BLS.NS","BORORENEW.NS","CESC.NS","CESCVENT.NS",
    "CIPLA.NS","COFORGE.NS","COROMANDEL.NS","CUB.NS","CUMMINSIND.NS","CYBERTECH.NS","DBREALTY.NS",
    "DCBBANK.NS","DELTACORP.NS","DHANI.NS","DISHMAN.NS","EASEMYTRIP.NS","EDELWEISS.NS","EIDPARRY.NS",
    "ELGIEQUIP.NS","EMAMILTD.NS","EPL.NS","ESABINDIA.NS","EVEREADY.NS","EXCELINDUS.NS","FDC.NS",
    "FINPIPE.NS","FORCEMOT.NS","FSL.NS","GABRIEL.NS","GALAXYSURF.NS","GEPIL.NS","GESHIP.NS",
    "GICRE.NS","GODREJCP.NS","GPPL.NS","GRANULES.NS","GULFOILLUB.NS","HATSUN.NS","HAVELLS.NS",
    "HFCL.NS","HINDCOPPER.NS","HINDPETRO.NS","HLEGLAS.NS","IBULHSGFIN.NS","IFCI.NS","IIFLSEC.NS",
    "INDHOTEL.NS","INDIAGLYCO.NS","INDIANHUME.NS","INDIGO.NS","INDUSINDBK.NS","INFIBEAM.NS",
    "INOXWIND.NS","IRCTC.NS","IRFC.NS","IRCON.NS","ITC.NS","JAMNAAUTO.NS","JINDALPOLY.NS",
    "JKPAPER.NS","JSL.NS","JUBLINGREA.NS","JYOTHYLAB.NS","KALPATPOWR.NS","KAYNES.NS","KEC.NS",
    "KFINTECH.NS","KNRCON.NS","KPIGREEN.NS","KRBL.NS","LALPATHLAB.NS","LICI.NS","LUPIN.NS",
    "MAHLOG.NS","MANINFRA.NS","MAPMYINDIA.NS","MAXHEALTH.NS","MGL.NS","MINDACORP.NS","MOIL.NS",
    "MOTILALOFS.NS","NAVA.NS","NESCO.NS","NFL.NS","NHPC.NS","NLCINDIA.NS","OLECTRA.NS","ONGC.NS",
    "ORIENTELEC.NS","PAGEIND.NS","PERSISTENT.NS","PETRONET.NS","PFC.NS","PHOENIXLTD.NS","PNBHOUSING.NS",
    "POLYCAB.NS","POLYMED.NS","PRAJIND.NS","PRICOLLTD.NS","RALLIS.NS","RAMCOCEM.NS","RAYMOND.NS",
    "RITES.NS","RVNL.NS","SAIL.NS","SAREGAMA.NS","SBICARD.NS","SCI.NS","SJVN.NS","SOLARINDS.NS",
    "SONACOMS.NS","SRF.NS","SUNDRMFAST.NS","SUNTV.NS","SUPREMEIND.NS","TATACHEM.NS","TATACOMM.NS",
    "TATAELXSI.NS","TATAPOWER.NS","TATATECH.NS","TCI.NS","TEJASNET.NS","THERMAX.NS","TITAGARH.NS",
    "TORNTPOWER.NS","TRENT.NS","TRITURBINE.NS","TVSMOTOR.NS","UBL.NS","UNOMINDA.NS","VBL.NS",
    "VEDL.NS","VIJAYA.NS","VOLTAS.NS","WELCORP.NS","WHIRLPOOL.NS","ZEEL.NS","ZOMATO.NS"
]

# --- MARKET DATA: PUBLIC YAHOO FINANCE CHART DATA (NO DHAN) ---
# Public Yahoo chart endpoint; no broker credentials are used.
YAHOO_CHART_HOSTS = (
    "https://query1.finance.yahoo.com/v8/finance/chart",
    "https://query2.finance.yahoo.com/v8/finance/chart",
)
YAHOO_HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/125.0 Safari/537.36",
    "Accept": "application/json,text/plain,*/*",
    "Accept-Language": "en-US,en;q=0.9",
}

# Reuse HTTP connections per worker thread. This avoids repeatedly opening TLS
# connections for hundreds of symbols while keeping sessions thread-safe.
_HTTP_LOCAL = local()

def _get_yahoo_session():
    session = getattr(_HTTP_LOCAL, "session", None)
    if session is None:
        session = requests.Session()
        session.headers.update(YAHOO_HEADERS)
        adapter = HTTPAdapter(pool_connections=24, pool_maxsize=24, max_retries=0)
        session.mount("https://", adapter)
        _HTTP_LOCAL.session = session
    return session


@st.cache_data(ttl=300, show_spinner=False)
def fetch_yahoo_chart(ticker, interval, range_value):
    """Fetch Yahoo candles; reuse connections and fall back quickly to query2."""
    last_error = None
    session = _get_yahoo_session()
    for host in YAHOO_CHART_HOSTS:
        url = f"{host}/{ticker}"
        try:
            response = session.get(
                url,
                params={"interval": interval, "range": range_value, "includePrePost": "false"},
                timeout=(4, 9),
            )
            if response.status_code in (429, 500, 502, 503, 504):
                last_error = f"HTTP {response.status_code}"
                continue
            response.raise_for_status()
            body = response.json()
            chart = body.get("chart", {})
            if chart.get("error"):
                raise RuntimeError(str(chart["error"]))
            result = chart.get("result") or []
            if not result:
                return {}, pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
            item = result[0]
            timestamps = item.get("timestamp") or []
            quote = (item.get("indicators", {}).get("quote") or [{}])[0]
            if not timestamps:
                return item.get("meta", {}), pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
            frame = pd.DataFrame({
                "Open": quote.get("open", []), "High": quote.get("high", []),
                "Low": quote.get("low", []), "Close": quote.get("close", []),
                "Volume": quote.get("volume", []),
            }, index=pd.to_datetime(timestamps, unit="s", utc=True).tz_convert("Asia/Kolkata"))
            frame.index.name = "Datetime"
            frame = frame.dropna(subset=["Open", "High", "Low", "Close"], how="all")
            frame = frame.sort_index()
            frame = frame[~frame.index.duplicated(keep="last")]
            return item.get("meta", {}), frame
        except Exception as exc:
            last_error = f"{type(exc).__name__}: {exc}"
    raise RuntimeError(last_error or "Yahoo Finance request failed")


def _fetch_one_yahoo_symbol(ticker):
    """Download one symbol once and derive session/daily data from 5-minute candles.
    This keeps the expanded 500+ universe practical by avoiding a second Yahoo request
    for every symbol, reducing rate-limit failures substantially.
    """
    sym = str(ticker).replace(".NS", "").upper()
    meta, intraday = fetch_yahoo_chart(f"{sym}.NS", "5m", "5d")
    if intraday.empty:
        raise ValueError("No 5-minute candle history")

    intraday = intraday.dropna(subset=["Close"]).copy()
    if intraday.empty:
        raise ValueError("No valid intraday candles")
    current_price = meta.get("regularMarketPrice")
    if current_price is None:
        current_price = float(intraday["Close"].iloc[-1])

    session_date = intraday.index[-1].date()

    # Build daily OHLCV from the available 5-minute candles (latest 5 sessions).
    tmp = intraday.copy()
    tmp["SessionDate"] = pd.to_datetime(tmp.index).date
    daily = tmp.groupby("SessionDate").agg(
        Open=("Open", "first"), High=("High", "max"), Low=("Low", "min"),
        Close=("Close", "last"), Volume=("Volume", "sum")
    )
    daily.index = pd.to_datetime(daily.index)

    previous_sessions = daily[daily.index.date < session_date]["Close"].dropna()
    previous_close = float(previous_sessions.iloc[-1]) if not previous_sessions.empty else None
    if previous_close is None:
        previous_close = meta.get("chartPreviousClose") or meta.get("previousClose")
    if previous_close is None or float(previous_close) <= 0:
        raise ValueError("Previous close unavailable")

    session_intraday = intraday[intraday.index.date == session_date].copy()
    if session_intraday.empty:
        raise ValueError("Latest trading-session candles unavailable")
    day_volume = float(session_intraday["Volume"].fillna(0).sum())

    return sym, {
        "last_price": float(current_price),
        "previous_close": float(previous_close),
        "company_name": meta.get("longName") or meta.get("shortName") or sym,
        "volume": day_volume,
        "intraday": intraday,
        "daily": daily,
        "session_date": session_date,
    }

def fetch_bulk_quotes(tickers):
    """Fetch symbols concurrently; keep successful symbols if some requests fail."""
    quote_map = {}
    errors = []
    # Moderate parallelism plus connection reuse accelerates the first full scan.
    # 16 workers is a balance: faster than the old 8-worker pool without an
    # excessively aggressive burst against Yahoo's public endpoint.
    with ThreadPoolExecutor(max_workers=16, thread_name_prefix="scanpro-yahoo") as pool:
        futures = {pool.submit(_fetch_one_yahoo_symbol, ticker): ticker for ticker in tickers}
        for future in as_completed(futures):
            try:
                sym, quote = future.result()
                quote_map[sym] = quote
            except Exception as exc:
                errors.append(f"{str(futures[future]).replace('.NS', '')}: {exc}")
    if not quote_map:
        detail = "; ".join(errors[:5])
        return {}, (
            "Yahoo Finance se koi market data receive nahi hua. Ye Dhan error nahi hai. "
            "Yahoo public endpoint ne request reject/limit ki ho sakti hai, ya internet/data access unavailable hai. "
            f"Details: {detail}"
        )
    return quote_map, None


# --- STRICT PREVIOUS CLOSE, LIVE LTP & CONSISTENT SCANNER CALCULATIONS ---
def fetch_single_stock(ticker, quote_map):
    try:
        sym_clean = ticker.replace(".NS", "").upper()
        quote = quote_map.get(sym_clean)
        if not quote or quote.get("last_price") in (None, 0, "0"):
            return None
        curr_price = float(quote["last_price"])
        prev_day_close = float(quote.get("previous_close") or 0)
        if prev_day_close <= 0:
            return None
        # Use broker quote's live LTP and previous-session close, not the last 5-minute candle close.
        change_pct = ((curr_price - prev_day_close) / prev_day_close) * 100.0
        today_daily_volume = int(float(quote.get("volume") or 0))
        df_5m = quote.get("intraday")
        df_daily = quote.get("daily")
        if df_5m is None or df_5m.empty:
            return None
        # Select the latest available exchange session, including weekends/holidays.
        session_date = quote.get("session_date") or df_5m.index[-1].date()
        today_df = df_5m[df_5m.index.date == session_date].copy()
        if today_df.empty:
            return None

        # Calculate session VWAP from today's 5-minute candles.
        typical_price = (today_df["High"] + today_df["Low"] + today_df["Close"]) / 3
        vwap_volume = pd.to_numeric(today_df["Volume"], errors="coerce").fillna(0)
        total_vwap_volume = float(vwap_volume.sum())
        vwap = float((typical_price * vwap_volume).sum() / total_vwap_volume) if total_vwap_volume > 0 else curr_price

        # Exclude today's partial daily bar when calculating the 20-session average volume.
        if df_daily is not None and not df_daily.empty:
            completed_daily = df_daily[df_daily.index.date < session_date]
            recent_volumes = pd.to_numeric(completed_daily["Volume"], errors="coerce").dropna().tail(20)
            sma_vol_20 = float(recent_volumes.mean()) if not recent_volumes.empty else float(today_daily_volume)
        else:
            sma_vol_20 = float(today_daily_volume)
        vol_surge = bool(sma_vol_20 > 0 and today_daily_volume > sma_vol_20 * 3)

        # Relative volume compares the latest 5-minute bar with earlier 5-minute bars of this session.
        intraday_vol = float(today_df["Volume"].iloc[-1])
        previous_bar_volumes = pd.to_numeric(today_df["Volume"].iloc[:-1], errors="coerce").dropna()
        avg_vol = float(previous_bar_volumes.mean()) if not previous_bar_volumes.empty else intraday_vol
        rvol = round(intraday_vol / avg_vol, 2) if avg_vol > 0 else 1.0

        # Opening range: candles starting at 09:15, 09:20 and 09:25; available after 09:30.
        morning = today_df[(today_df.index.time >= datetime.strptime("09:15", "%H:%M").time()) &
                           (today_df.index.time < datetime.strptime("09:30", "%H:%M").time())]
        orb_ready = get_ist_time().time() >= datetime.strptime("09:30", "%H:%M").time() and len(morning) >= 3
        orb_high = float(morning["High"].max()) if not morning.empty else curr_price
        orb_low = float(morning["Low"].min()) if not morning.empty else curr_price

        # Exact NSE opening candle: 09:15-09:20 (5-minute interval).
        # Do not use the first available candle blindly; verify its timestamp is 09:15.
        opening_time = datetime.strptime("09:15", "%H:%M").time()
        opening_rows = today_df[today_df.index.time == opening_time]
        first_5m_complete = (
            session_date < get_ist_time().date()
            or get_ist_time().time() >= datetime.strptime("09:20", "%H:%M").time()
        )
        opening_candle_ready = not opening_rows.empty and first_5m_complete
        if not opening_rows.empty:
            first_c = opening_rows.iloc[0]
            first_5m_open = float(first_c["Open"])
            first_5m_high = float(first_c["High"])
            first_5m_low = float(first_c["Low"])
            first_5m_close = float(first_c["Close"])
            # NSE prices are quoted in paise/tick increments. A 1-paise tolerance
            # avoids floating-point representation errors without changing the rule.
            tick_tolerance = 0.01
            first_5m_open_low = abs(first_5m_open - first_5m_low) <= tick_tolerance
            first_5m_open_high = abs(first_5m_open - first_5m_high) <= tick_tolerance
        else:
            first_5m_open = first_5m_high = first_5m_low = first_5m_close = float("nan")
            first_5m_open_low = False
            first_5m_open_high = False

        # Intraday invalidation for Tab 3:
        # Once any later 5-minute candle trades beyond the opening candle's
        # low/high, permanently exclude that Open=Low/Open=High candidate
        # from the respective Tab 3 list for the rest of the session.
        later_rows = today_df[today_df.index.time > opening_time]
        first_5m_low_broken = bool(
            opening_candle_ready and not later_rows.empty and
            (pd.to_numeric(later_rows["Low"], errors="coerce") < first_5m_low - tick_tolerance).any()
        )
        first_5m_high_broken = bool(
            opening_candle_ready and not later_rows.empty and
            (pd.to_numeric(later_rows["High"], errors="coerce") > first_5m_high + tick_tolerance).any()
        )

        first_5m_status = "NORMAL"
        if opening_candle_ready and curr_price > first_5m_high:
            first_5m_status = "1ST 5M BULLISH BREAKOUT"
        elif opening_candle_ready and curr_price < first_5m_low:
            first_5m_status = "1ST 5M BEARISH BREAKDOWN"

        first_15m = today_df[today_df.index.time < datetime.strptime("09:30", "%H:%M").time()].head(3)
        if not first_15m.empty:
            first_15m_high = float(first_15m["High"].max())
            first_15m_low = float(first_15m["Low"].min())
        else:
            first_15m_high = curr_price
            first_15m_low = curr_price
        first_15m_status = "NORMAL"
        first_15m_complete = get_ist_time().time() >= datetime.strptime("09:30", "%H:%M").time() and len(first_15m) >= 3
        if first_15m_complete and curr_price > first_15m_high:
            first_15m_status = "1ST 15M BULLISH BREAKOUT"
        elif first_15m_complete and curr_price < first_15m_low:
            first_15m_status = "1ST 15M BEARISH BREAKDOWN"

        status = "NORMAL" if orb_ready else "WAIT ORB CLOSE"
        pro_status = "NORMAL" if orb_ready else "WAIT ORB CLOSE"
        surge_930_status = "NORMAL" if orb_ready else "WAIT ORB CLOSE"
        if orb_ready:
            if curr_price > orb_high:
                status = "BULLISH BREAKOUT"
            elif curr_price < orb_low:
                status = "BEARISH BREAKDOWN"
            if curr_price > orb_high and curr_price > vwap and rvol >= 1.3:
                pro_status = "PRO BULLISH"
            elif curr_price < orb_low and curr_price < vwap and rvol >= 1.3:
                pro_status = "PRO BEARISH"
            if rvol >= 2.5 and curr_price > orb_high and curr_price > vwap and change_pct >= 1.2:
                surge_930_status = "9:30 VOL SURGE BULLISH"
            elif rvol >= 2.5 and curr_price < orb_low and curr_price < vwap and change_pct <= -1.2:
                surge_930_status = "9:30 VOL SURGE BEARISH"

        fii_live_score = round(rvol * change_pct if change_pct > 0 and curr_price > vwap else 0.0, 2)
        dii_live_score = round(rvol * abs(change_pct) if rvol >= 1.5 and sma_vol_20 > 0 and today_daily_volume > sma_vol_20 else 0.0, 2)
        return {
            "Symbol": sym_clean, "Name": quote.get("company_name") or sym_clean,
            "LTP": round(curr_price, 2), "Change (%)": round(change_pct, 2),
            "Volume": today_daily_volume, "VolSurge": vol_surge, "SMA_Vol": int(sma_vol_20),
            "RVol": rvol, "VWAP": round(vwap, 2), "ORB High": round(orb_high, 2),
            "ORB Low": round(orb_low, 2), "First5mOpen": first_5m_open,
            "First5mHigh": first_5m_high, "First5mLow": first_5m_low,
            "First5mClose": first_5m_close, "First5mOpenLow": first_5m_open_low,
            "First5mOpenHigh": first_5m_open_high,
            "First5mLowBroken": first_5m_low_broken,
            "First5mHighBroken": first_5m_high_broken,
            "First5mMidpoint": round((first_5m_high + first_5m_low) / 2, 2) if pd.notna(first_5m_high) and pd.notna(first_5m_low) else float("nan"),
            "First5mCandleReady": opening_candle_ready, "First5mStatus": first_5m_status,
            "First15mHigh": round(first_15m_high, 2), "First15mLow": round(first_15m_low, 2),
            "First15mStatus": first_15m_status, "Status": status, "ProStatus": pro_status,
            "Surge930Status": surge_930_status, "Prev Close": round(prev_day_close, 2),
            "FII_Live_Score": fii_live_score, "DII_Live_Score": dii_live_score,
        }
    except Exception:
        return None


@st.cache_data(ttl=10, show_spinner=False)
def execute_master_scan(all_tickers_tuple):
    start_t = time.time()
    quote_map, quote_error = fetch_bulk_quotes(all_tickers_tuple)
    if quote_error:
        return pd.DataFrame(), round((time.time() - start_t) * 1000, 2), quote_error
    with ThreadPoolExecutor(max_workers=16, thread_name_prefix="scanpro-calc") as executor:
        results = list(executor.map(fetch_single_stock, all_tickers_tuple,
                                    repeat(quote_map)))
    valid = [r for r in results if r is not None]
    exec_time = round((time.time() - start_t) * 1000, 2)
    return pd.DataFrame(valid), exec_time, None

col_h1, col_h2 = st.columns([3, 1])
with col_h1:
    st.markdown("""
    <div style="margin-bottom: 5px;">
        <h1 style="font-size: 40px; font-weight: 900; background: linear-gradient(90deg, #00d2ff, #3a7bd5, #0072ff); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin: 0;">SCAN PRO</h1>
        <p style="font-size: 14px; color: #38bdf8; font-weight: 800; margin: 0; letter-spacing: 2px;">STOCK MARKET SOLUTIONS (LIVE TERMINAL)</p>
    </div>
    <span style='font-size: 13px; color: #10b981; font-weight: 700;'>⚡ Live Nifty 50 Breadth + Midcap & Smallcap Matrix</span>
    """, unsafe_allow_html=True)

with col_h2:
    st.markdown(f"""
    <div class="time-3d-box">
        <span style="font-size: 11px; color: #a7f3d0; font-weight: 700; display: block; margin-bottom: 2px;">IST MARKET TIME</span>
        <span class="time-3d-text">{get_ist_time().strftime('%H:%M:%S')}</span>
    </div>
    """, unsafe_allow_html=True)

# Merge the original sector map with the expanded theme universe. This shared
# master list feeds every tab; duplicate tickers are removed before downloading.
ALL_SECTOR_MAP = {**SECTOR_MAP, **EXPANDED_SECTOR_MAP}
all_tickers = sorted(set(
    [t for sub in ALL_SECTOR_MAP.values() for t in sub]
    + NIFTY_50_TICKERS + FNO_STOCKS + MORE_NSE_TICKERS
))

with st.spinner("⚡ Scanning market data (Microsecond speed)..."):
    master_df, speed_ms, scan_error = execute_master_scan(tuple(all_tickers))

if not master_df.empty and "Symbol" in master_df.columns:
    clean_n50_symbols = [t.replace(".NS", "") for t in NIFTY_50_TICKERS]
    n50_df = master_df[master_df["Symbol"].isin(clean_n50_symbols)]
    n50_green = len(n50_df[n50_df["Change (%)"] > 0])
    n50_red = len(n50_df[n50_df["Change (%)"] < 0])
    
    st.markdown(f"""
    <div class="nifty-3d-box">
        <div style="text-align: left;">
            <div style="font-weight: 800; font-size: 13px; color: #9ca3af;">NIFTY 50 BREADTH</div>
            <div style="font-size: 16px; font-weight: 900; color: #10b981;">🟢 {n50_green} Green Stocks</div>
            <div style="font-size: 16px; font-weight: 900; color: #ef4444;">🔴 {n50_red} Red Stocks</div>
        </div>
        <div class="stat-card-blue">
            <span style="font-size: 11px; color: #93c5fd; font-weight: 700;">TOTAL MONITORED</span><br>
            <span style="font-size: 20px; font-weight: 900; color: #ffffff;">{len(master_df)}</span><br>
            <span style="font-size: 10px; font-weight: 800; color: #60a5fa;">ACTIVE SYMBOLS</span>
        </div>
        <div class="stat-card-green">
            <span style="font-size: 11px; color: #a7f3d0; font-weight: 700;">SCAN SPEED</span><br>
            <span style="font-size: 20px; font-weight: 900; color: #ffffff;">{speed_ms}</span><br>
            <span style="font-size: 10px; font-weight: 800; color: #34d399;">MILLISECONDS</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

# DATA FEED note hidden from dashboard; feed logic remains unchanged.
st.markdown("---")

if 'selected_sector_click' not in st.session_state:
    st.session_state.selected_sector_click = list(ALL_SECTOR_MAP.keys())[0]

if master_df.empty or "Symbol" not in master_df.columns:
    if scan_error:
        st.error(scan_error)
    else:
        st.error("Market data abhi available nahi hai. Market hours aur internet connection check karke refresh karein.")
else:
    master_df = master_df.sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
    
    tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8, tab9, tab10, tab11 = st.tabs([
        "1. All Sectors",
        "2. Sector Stocks",
        "3. 9:15 Open=Low/High",
        "4. Gainers/Losers",
        "5. F&O Stocks",
        "6. 9:15 ORB",
        "7. VWAP+RVol",
        "8. Institutional Vol Surge (9:30 AM)",
        "9. FII, DII & Breakouts",
        "10. Chartink Vol Surge",
        "11. Combined 5m/15m Breakout"
    ])
    
    # TAB 1: ALL SECTORS MATRIX
    with tab1:
        st.caption(f"Feed Latency: {speed_ms} ms | Active scanned stocks: {len(master_df)} | Expanded universe: 500+ | Auto-Refresh: 30s")
        sector_summary = []
        for sec, tks in ALL_SECTOR_MAP.items():
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
            for i in range(0, len(sec_summary_df), 6):
                cols = st.columns(6)
                for j in range(6):
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
                            if st.button(f"Inspect {row['Sector']}", key=f"s_{row['Sector']}"):
                                st.session_state.selected_sector_click = row['Sector']
                                st.rerun()

    # TAB 2: SECTOR STOCKS
    with tab2:
        sel_sec = st.selectbox("Select Sector", list(ALL_SECTOR_MAP.keys()), index=list(ALL_SECTOR_MAP.keys()).index(st.session_state.selected_sector_click))
        st.session_state.selected_sector_click = sel_sec
        clean_tks = [t.replace(".NS", "") for t in ALL_SECTOR_MAP[sel_sec]]
        stocks_subset = master_df[master_df["Symbol"].isin(clean_tks)].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        st.write(f"Showing all **{len(stocks_subset)}** stocks in **{sel_sec}** (Descending order of %):")
        if not stocks_subset.empty:
            for i in range(0, len(stocks_subset), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(stocks_subset):
                        stk = stocks_subset.iloc[i + j]
                        chg_val = stk["Change (%)"]
                        card_cls = "matrix-card-green" if chg_val >= 0 else "matrix-card-red"
                        sym = stk["Symbol"]
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="{card_cls}">
                                <h5 style="margin: 0; color: #fff; font-size: 18px; font-weight: 900;">{html.escape(str(stk.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{stk['LTP']:,.2f} ({chg_val:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {stk['Volume']:,}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)

    # TAB 4: GAINERS & LOSERS
    with tab4:
        st.markdown("### Complete Market Gainers & Losers (Descending Order)")
        col_g, col_l = st.columns(2)
        with col_g:
            st.markdown("#### All Gainers")
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
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} (+{r['Change (%)']:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,}</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("No gainers currently.")
                
        with col_l:
            st.markdown("#### All Losers")
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
                                    <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                    <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,}</p>
                                    <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                                </div>
                                """, unsafe_allow_html=True)
            else:
                st.info("No losers currently.")

    # TAB 3: 09:15-09:20 OPEN = LOW / OPEN = HIGH SCANNER
    with tab3:
        st.markdown("### 9:15 AM – 9:20 AM Opening 5-Minute Candle Scanner")
        st.caption(
            "Rule: Sirf exact 09:15 timestamp wali 5-minute candle check hoti hai. "
            "Open = Low aur Open = High ko 1 paise tolerance ke saath match kiya gaya hai. "
            "Scanner candle complete hone ke baad (09:20 AM) results dikhata hai."
        )

        # TOP SECTION: Open=Low + discount-zone pullback candidates.
        st.markdown("### ⭐ OPEN = LOW + 5-Minute DISCOUNT ZONE (Bullish Watchlist)")
        st.caption(
            "Discount zone = 09:15–09:20 opening 5-minute candle ke High-Low range ka lower 50% "
            "(Low se midpoint tak). Sirf Open=Low stocks dikhte hain. Bullish checks sirf confluence ranking hain, "
            "profit/probability guarantee nahi; entry se pehle chart confirmation zaroor dekhein."
        )
        if not master_df.get("First5mCandleReady", pd.Series(False, index=master_df.index)).any():
            st.info("09:15–09:20 opening candle abhi available/complete nahi hai. 09:20 AM ke baad refresh karein.")
        else:
            discount_candidates = master_df[
                (master_df["First5mCandleReady"] == True) &
                (master_df["First5mOpenLow"] == True) &
                (~master_df["First5mLowBroken"].fillna(False)) &
                (master_df["LTP"] >= master_df["First5mLow"]) &
                (master_df["LTP"] <= master_df["First5mMidpoint"])
            ].copy()
            if not discount_candidates.empty:
                discount_candidates["Bullish Checks"] = (
                    (discount_candidates["First5mClose"] > discount_candidates["First5mOpen"]).astype(int) +
                    (discount_candidates["LTP"] > discount_candidates["VWAP"]).astype(int) +
                    (discount_candidates["RVol"] >= 1.3).astype(int) +
                    (discount_candidates["LTP"] > discount_candidates["First5mLow"] +
                     (discount_candidates["First5mHigh"] - discount_candidates["First5mLow"]) * 0.25).astype(int)
                )
                discount_candidates = discount_candidates.sort_values(
                    by=["Bullish Checks", "RVol", "Change (%)"], ascending=[False, False, False]
                ).reset_index(drop=True)
                st.markdown(f"#### Discount-zone Open=Low candidates ({len(discount_candidates)} stocks)")
                st.caption("Bullish checks (0–4): green opening candle, price above VWAP, RVol ≥ 1.3, and bounce at least 25% above opening low.")
                for row_start in range(0, len(discount_candidates), 6):
                    card_cols = st.columns(6)
                    for col_idx in range(6):
                        if row_start + col_idx >= len(discount_candidates):
                            continue
                        stock = discount_candidates.iloc[row_start + col_idx]
                        symbol = str(stock["Symbol"])
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{symbol}&interval=5"
                        checks = int(stock["Bullish Checks"])
                        with card_cols[col_idx]:
                            st.markdown(
                                f"<div class='matrix-card-green'><h5 style='margin:0;color:#fff;font-size:17px;font-weight:900;'>{html.escape(str(stock.get('Name', symbol)))}</h5>"
                                f"<h3 style='margin:5px 0;color:#fff;'>₹{float(stock['LTP']):,.2f}</h3>"
                                f"<p style='font-size:11px;color:#e2e8f0;margin:0;'>Discount: ₹{float(stock['First5mLow']):,.2f} – ₹{float(stock['First5mMidpoint']):,.2f}</p>"
                                f"<p style='font-size:11px;color:#e2e8f0;margin:0;'>VWAP: ₹{float(stock['VWAP']):,.2f} | RVol: {float(stock['RVol']):.2f}</p>"
                                f"<p style='font-size:12px;color:#a7f3d0;margin:2px 0;'>Bullish checks: {checks}/4</p>"
                                f"<a href='{tv_url}' target='_blank' class='tv-link'>📈 TradingView (5m) ↗</a></div>",
                                unsafe_allow_html=True,
                            )
            else:
                st.info("Abhi koi Open=Low stock opening 5-minute candle ke discount zone mein nahi hai.")

            st.markdown("---")
            st.markdown("### Existing Open=Low / Open=High Scanner")
            open_low_df = master_df[
                (master_df["First5mCandleReady"] == True) &
                (master_df["First5mOpenLow"] == True) &
                (~master_df["First5mLowBroken"].fillna(False))
            ].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
            open_high_df = master_df[
                (master_df["First5mCandleReady"] == True) &
                (master_df["First5mOpenHigh"] == True) &
                (~master_df["First5mHighBroken"].fillna(False))
            ].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)

            def render_opening_candle_cards(data, card_class, label):
                st.markdown(f"#### {label} ({len(data)} stocks)")
                if data.empty:
                    st.info("Is condition mein abhi koi stock nahi mila.")
                    return
                for row_start in range(0, len(data), 6):
                    card_cols = st.columns(6)
                    for col_idx in range(6):
                        if row_start + col_idx >= len(data):
                            continue
                        stock = data.iloc[row_start + col_idx]
                        symbol = str(stock["Symbol"])
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{symbol}&interval=5"
                        with card_cols[col_idx]:
                            st.markdown(f"""
                            <div class="{card_class}">
                                <h5 style="margin:0;color:#fff;font-size:15px;">{html.escape(str(stock.get('Name', symbol)))}</h5>
                                <h3 style="margin:5px 0;color:#fff;">₹{float(stock['LTP']):,.2f} ({float(stock['Change (%)']):+.2f}%)</h3>
                                <p style="font-size:11px;color:#e2e8f0;margin:0;">09:15 Open: ₹{float(stock['First5mOpen']):,.2f}</p>
                                <p style="font-size:11px;color:#e2e8f0;margin:0;">High: ₹{float(stock['First5mHigh']):,.2f} | Low: ₹{float(stock['First5mLow']):,.2f}</p>
                                <p style="font-size:11px;color:#e2e8f0;margin:0;">Close: ₹{float(stock['First5mClose']):,.2f}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)

            render_opening_candle_cards(
                open_low_df, "matrix-card-green", "PART 1 — OPEN = LOW (Bullish Opening Candle)"
            )
            st.markdown("---")
            render_opening_candle_cards(
                open_high_df, "matrix-card-red", "PART 2 — OPEN = HIGH (Bearish Opening Candle)"
            )

    # TAB 5: F&O STOCKS SCANNER
    with tab5:
        st.markdown("### Futures & Options (F&O) Active Stocks Scanner")
        clean_fno = [t.replace(".NS", "") for t in FNO_STOCKS]
        fno_df = master_df[master_df["Symbol"].isin(clean_fno)].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        st.write(f"Total F&O Scanned Stocks: **{len(fno_df)}** (Descending Order)")
        if not fno_df.empty:
            for i in range(0, len(fno_df), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(fno_df):
                        r = fno_df.iloc[i + j]
                        sym = r['Symbol']
                        chg_val = r['Change (%)']
                        card_cls = "matrix-card-green" if chg_val >= 0 else "matrix-card-red"
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="{card_cls}">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({chg_val:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No F&O stocks currently available.")

    # TAB 6: ORB BREAKOUT
    with tab6:
        st.markdown("### Complete 9:15 - 9:30 Opening Range Breakout (Descending Order)")
        orb_bull = master_df[master_df["Status"].str.contains("BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        orb_bear = master_df[master_df["Status"].str.contains("BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
        
        st.markdown(f"#### All Bullish ORB Breakouts ({len(orb_bull)} stocks)")
        if not orb_bull.empty:
            for i in range(0, len(orb_bull), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(orb_bull):
                        r = orb_bull.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="matrix-card-green">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">ORB High: ₹{r['ORB High']}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No active bullish breakout right now.")
            
        st.markdown(f"#### All Bearish ORB Breakdowns ({len(orb_bear)} stocks)")
        if not orb_bear.empty:
            for i in range(0, len(orb_bear), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(orb_bear):
                        r = orb_bear.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="matrix-card-red">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">ORB Low: ₹{r['ORB Low']}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No active bearish breakdown right now.")

    # TAB 7: VWAP RVOL ORB PRO
    with tab7:
        st.markdown("### Complete Institutional Pro Setups (Descending Order)")
        pro_bull = master_df[master_df["ProStatus"].str.contains("PRO BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        pro_bear = master_df[master_df["ProStatus"].str.contains("PRO BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
        
        st.markdown(f"#### All Pro Bullish Setups ({len(pro_bull)} stocks)")
        if not pro_bull.empty:
            for i in range(0, len(pro_bull), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(pro_bull):
                        r = pro_bull.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="matrix-card-green">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">VWAP: ₹{r['VWAP']}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("Abhi koi Pro Bullish setup active nahi hai.")
            
        st.markdown(f"#### All Pro Bearish Setups ({len(pro_bear)} stocks)")
        if not pro_bear.empty:
            for i in range(0, len(pro_bear), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(pro_bear):
                        r = pro_bear.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="matrix-card-red">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">VWAP: ₹{r['VWAP']}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("Abhi koi Pro Bearish setup active nahi hai.")

    # TAB 10: CHARTINK VOLUME SURGE SCANNER
    with tab10:
        st.markdown("### Chartink Volume Surge Scanner: Daily Vol > (20 SMA Vol * 3) (Descending)")
        if "VolSurge" in master_df.columns:
            surge_stocks = master_df[master_df["VolSurge"] == True].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        else:
            surge_stocks = pd.DataFrame()
        st.write(f"Total Volume Surge Stocks Found: **{len(surge_stocks)}**")
        if not surge_stocks.empty:
            for i in range(0, len(surge_stocks), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(surge_stocks):
                        r = surge_stocks.iloc[i + j]
                        sym = r['Symbol']
                        chg_val = r['Change (%)']
                        card_cls = "matrix-card-green" if chg_val >= 0 else "matrix-card-red"
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="{card_cls}">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({chg_val:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Vol: {r['Volume']:,}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("Abhi koi stock Chartink volume surge criteria ko match nahi kar raha hai.")

    # TAB 8: 9:30 AM INSTITUTIONAL VOL SURGE SCANNER
    with tab8:
        st.markdown("### 9:30 AM Institutional Volume Surge Screener (Descending Order)")
        surge_930_bull = master_df[master_df["Surge930Status"].str.contains("BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        surge_930_bear = master_df[master_df["Surge930Status"].str.contains("BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
        
        st.markdown(f"#### Bullish Vol Surge Movers ({len(surge_930_bull)} stocks)")
        if not surge_930_bull.empty:
            for i in range(0, len(surge_930_bull), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(surge_930_bull):
                        r = surge_930_bull.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="matrix-card-green">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">RVol: <b>{r['RVol']}x</b></p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No active bullish 9:30 surge right now.")
            
        st.markdown(f"#### Bearish Vol Surge Movers ({len(surge_930_bear)} stocks)")
        if not surge_930_bear.empty:
            for i in range(0, len(surge_930_bear), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(surge_930_bear):
                        r = surge_930_bear.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="matrix-card-red">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">RVol: <b>{r['RVol']}x</b></p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)
        else:
            st.info("No active bearish 9:30 surge right now.")

    # TAB 9: FII, DII & BREAKOUT SECTIONS (5-MIN, 15-MIN & LIVE ENTRY)
    with tab9:
        st.markdown("### Live Institutional & Opening Candle Breakout Scanner (Descending Order)")
        
        # SECTION 1: 5-MIN CANDLE BREAKOUT
        st.markdown("---")
        st.markdown("#### 11️⃣ Opening 5-Min Candle Breakout / Breakdown Stocks")
        f5_bull = master_df[master_df["First5mStatus"].str.contains("BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        f5_bear = master_df[master_df["First5mStatus"].str.contains("BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
        st.write(f"**Bullish 5m Breakouts:** {len(f5_bull)} | **Bearish 5m Breakdowns:** {len(f5_bear)}")
        
        if not f5_bull.empty:
            for i in range(0, len(f5_bull), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(f5_bull):
                        r = f5_bull.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="matrix-card-green">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">1st 5m High: ₹{r['First5mHigh']}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)

        # SECTION 2: 15-MIN CANDLE BREAKOUT
        st.markdown("---")
        st.markdown("#### 21️⃣ Opening 15-Min Candle Breakout / Breakdown Stocks")
        f15_bull = master_df[master_df["First15mStatus"].str.contains("BULLISH")].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        f15_bear = master_df[master_df["First15mStatus"].str.contains("BEARISH")].sort_values(by="Change (%)", ascending=True).reset_index(drop=True)
        st.write(f"**Bullish 15m Breakouts:** {len(f15_bull)} | **Bearish 15m Breakdowns:** {len(f15_bear)}")
        
        if not f15_bull.empty:
            for i in range(0, len(f15_bull), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(f15_bull):
                        r = f15_bull.iloc[i + j]
                        sym = r['Symbol']
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="matrix-card-green">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({r['Change (%)']:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">1st 15m High: ₹{r['First15mHigh']}</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)

        # SECTION 3: FII & DII LIVE ENTRY MOMENTUM
        st.markdown("---")
        st.markdown("#### 31️⃣ FII & DII Live Active Entry Momentum Scanner")
        fii_live_df = master_df[master_df["FII_Live_Score"] > 0].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        dii_live_df = master_df[master_df["DII_Live_Score"] > 0].sort_values(by="Change (%)", ascending=False).reset_index(drop=True)
        st.write(f"**FII Live Stocks:** {len(fii_live_df)} | **DII Live Stocks:** {len(dii_live_df)}")
        
        if not fii_live_df.empty:
            for i in range(0, len(fii_live_df), 6):
                cols = st.columns(6)
                for j in range(6):
                    if i + j < len(fii_live_df):
                        r = fii_live_df.iloc[i + j]
                        sym = r['Symbol']
                        chg_val = r['Change (%)']
                        card_cls = "matrix-card-green" if chg_val >= 0 else "matrix-card-red"
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval=5"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="{card_cls}">
                                <h5 style="margin: 0; color: #fff; font-size: 15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin: 4px 0; color: #fff;">₹{r['LTP']:,.2f} ({chg_val:+.2f}%)</h3>
                                <p style="font-size: 11px; color: #e2e8f0; margin: 0;">Live Score: <b>{r['FII_Live_Score']}</b></p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView (5m) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)

    # TAB 11: COMBINED CONFLUENCE BREAKOUT SCANNER
    with tab11:
        st.markdown("### Combined Rules Scanner — 5-Min & 15-Min Breakout")
        st.caption(
            "Is tab mein Tab 3, 6, 7, 8, 9 aur 10 ke rules ko ek saath AND condition mein check kiya gaya hai. "
            "Bullish ke liye opening 5m candle Open=Low aur bearish ke liye Open=High; saath hi ORB, VWAP+RVol, "
            "9:30 institutional surge, FII/DII live score aur daily volume surge sab match hona zaroori hai. "
            "Sirf sabhi conditions pass karne wale stocks dikhaye jayenge."
        )

        def render_combined_breakouts(timeframe_label, status_col, interval):
            st.markdown(f"#### {timeframe_label} Candle Breakout / Breakdown")
            bullish_mask = (
                master_df[status_col].fillna("").str.contains("BULLISH", case=False)
                & (master_df["First5mCandleReady"] == True)
                & (master_df["First5mOpenLow"] == True)
                & master_df["Status"].fillna("").str.contains("BULLISH", case=False)
                & master_df["ProStatus"].fillna("").str.contains("PRO BULLISH", case=False)
                & master_df["Surge930Status"].fillna("").str.contains("BULLISH", case=False)
                & ((master_df["FII_Live_Score"] > 0) | (master_df["DII_Live_Score"] > 0))
                & (master_df["VolSurge"] == True)
            )
            bearish_mask = (
                master_df[status_col].fillna("").str.contains("BEARISH|BREAKDOWN", case=False, regex=True)
                & (master_df["First5mCandleReady"] == True)
                & (master_df["First5mOpenHigh"] == True)
                & master_df["Status"].fillna("").str.contains("BEARISH|BREAKDOWN", case=False, regex=True)
                & master_df["ProStatus"].fillna("").str.contains("PRO BEARISH", case=False)
                & master_df["Surge930Status"].fillna("").str.contains("BEARISH", case=False)
                & ((master_df["FII_Live_Score"] > 0) | (master_df["DII_Live_Score"] > 0))
                & (master_df["VolSurge"] == True)
            )
            bullish = master_df[bullish_mask].sort_values("Change (%)", ascending=False).reset_index(drop=True)
            bearish = master_df[bearish_mask].sort_values("Change (%)", ascending=True).reset_index(drop=True)
            st.write(f"**Bullish all-rules match:** {len(bullish)} | **Bearish all-rules match:** {len(bearish)}")

            for label, data, card_class in (
                ("Bullish Breakouts", bullish, "matrix-card-green"),
                ("Bearish Breakdowns", bearish, "matrix-card-red"),
            ):
                st.markdown(f"##### {label} ({len(data)} stocks)")
                if data.empty:
                    st.info("Abhi koi stock sabhi combined rules ko match nahi kar raha hai.")
                    continue
                for start in range(0, len(data), 6):
                    cols = st.columns(6)
                    for j in range(6):
                        if start + j >= len(data):
                            continue
                        r = data.iloc[start + j]
                        sym = str(r["Symbol"])
                        tv_url = f"https://in.tradingview.com/chart/?symbol=NSE%3A{sym}&interval={interval}"
                        with cols[j]:
                            st.markdown(f"""
                            <div class="{card_class}">
                                <h5 style="margin:0;color:#fff;font-size:15px;">{html.escape(str(r.get('Name', sym)))}</h5>
                                <h3 style="margin:4px 0;color:#fff;">₹{float(r['LTP']):,.2f} ({float(r['Change (%)']):+.2f}%)</h3>
                                <p style="font-size:11px;color:#e2e8f0;margin:0;">VWAP: ₹{float(r['VWAP']):,.2f} | RVol: {float(r['RVol']):.2f}x</p>
                                <p style="font-size:11px;color:#e2e8f0;margin:0;">ORB: ₹{float(r['ORB Low']):,.2f}–₹{float(r['ORB High']):,.2f}</p>
                                <p style="font-size:11px;color:#e2e8f0;margin:0;">FII: {float(r['FII_Live_Score']):.2f} | DII: {float(r['DII_Live_Score']):.2f}</p>
                                <p style="font-size:11px;color:#e2e8f0;margin:0;">Daily Vol Surge: 3x+ 20-day average ✓</p>
                                <a href="{tv_url}" target="_blank" class="tv-link">📈 TradingView ({timeframe_label}) ↗</a>
                            </div>
                            """, unsafe_allow_html=True)

        render_combined_breakouts("5-Min", "First5mStatus", "5")
        st.markdown("---")
        render_combined_breakouts("15-Min", "First15mStatus", "15")

    # Strict 30 Seconds Auto Refresh Loop
    time.sleep(30)
    st.rerun()
