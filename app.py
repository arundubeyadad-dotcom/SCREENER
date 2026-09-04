import streamlit as st
import pandas as pd
import yfinance as yf
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, time

# Set Page Layout for Mobile / Samsung Fold
st.set_page_config(
    page_title="Institutional Stealth & Catalyst Engine",
    page_icon="⚡",
    layout="wide"
)

# Custom CSS for Mobile Optimization
st.markdown("""
<style>
    .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    .stMetric { background-color: #1e222d; padding: 10px; border-radius: 8px; }
    h3 { font-size: 1.2rem !important; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# STOCK UNIVERSE: High-Beta, MidSmall 400 & MicroCap watchlist (NSE)
# -------------------------------------------------------------------
WATCHLIST = [
    "TBZ.NS", "RESPONIND.NS", "WONDERLA.NS", "KALYANKJIL.NS", "SUZLON.NS", 
    "IRFC.NS", "RVNL.NS", "RAILTEL.NS", "BSOFT.NS", "HFCL.NS", "MAZDOCK.NS", 
    "COCHINSHIP.NS", "FACT.NS", "HUDCO.NS", "NBCC.NS", "ENGINERSIN.NS",
    "IOC.NS", "BPCL.NS", "RELIANCE.NS", "TATASTEEL.NS", "JPPOWER.NS"
]

# -------------------------------------------------------------------
# CORE ANALYSIS FUNCTION FOR INDIVIDUAL TICKER
# -------------------------------------------------------------------
def analyze_ticker(symbol):
    try:
        # Fetch 1-minute intraday data for today + 5-day daily data for baseline metrics
        ticker = yf.Ticker(symbol)
        df_1m = ticker.history(period="1d", interval="1m")
        df_daily = ticker.history(period="10d", interval="1d")

        if df_1m.empty or len(df_daily) < 6:
            return None

        # Data Points Extraction
        ltp = df_1m['Close'].iloc[-1]
        day_open = df_1m['Open'].iloc[0]
        day_high = df_1m['High'].max()
        day_low = df_1m['Low'].min()
        pdc = df_daily['Close'].iloc[-2]
        
        # Volume Baselines
        pdc_volume = df_daily['Volume'].iloc[-2]
        vol_5d_sma = df_daily['Volume'].iloc[-6:-1].mean()
        vol_10d_sma = df_daily['Volume'].iloc[-11:-1].mean()
        
        # 1-Minute Current Bar Metrics
        curr_1m_vol = df_1m['Volume'].iloc[-1]
        avg_1m_vol = df_1m['Volume'].tail(20).mean()
        rvol = curr_1m_vol / avg_1m_vol if avg_1m_vol > 0 else 0
        
        # 1-Min Turnover Safeguard (Min ₹10 Lakhs)
        turnover_1m = ltp * curr_1m_vol
        
        # Candle Body Ratio (Filters out weak wicks/fake spikes)
        candle_open = df_1m['Open'].iloc[-1]
        candle_close = df_1m['Close'].iloc[-1]
        candle_high = df_1m['High'].iloc[-1]
        candle_low = df_1m['Low'].iloc[-1]
        range_hl = candle_high - candle_low
        body_ratio = abs(candle_close - candle_open) / range_hl if range_hl > 0 else 0

        # Intraday VWAP Calculation
        v_sum = df_1m['Volume'].sum()
        vwap = (df_1m['Close'] * df_1m['Volume']).sum() / v_sum if v_sum > 0 else ltp

        # Return Percentage Calculations
        open_gap_pct = ((day_open - pdc) / pdc) * 100
        candle1_change_pct = ((df_1m['Close'].iloc[0] - df_1m['Open'].iloc[0]) / df_1m['Open'].iloc[0]) * 100
        day_gain_pct = ((ltp - pdc) / pdc) * 100
        max_gain_pct = ((day_high - day_open) / day_open) * 100

        # ---------------------------------------------------------------
        # STRATEGY TIER EVALUATION & INSTITUTIONAL SAFEGUARDS
        # ---------------------------------------------------------------
        
        # TIER 1: News & Catalyst High-Gap Surge (TBZ Setup)
        tier1_signal = (
            (1.0 <= open_gap_pct <= 4.0) and
            (candle1_change_pct >= 3.0) and
            (rvol >= 5.0) and
            (body_ratio >= 0.65) and
            (turnover_1m >= 1_000_000)
        )

        # TIER 2: Dry Liquidity Stealth Surge (Responsive Industries Setup)
        tier2_signal = (
            (pdc_volume < 500_000 or pdc_volume < vol_5d_sma) and
            (rvol >= 3.0) and
            (turnover_1m >= 1_000_000)
        )

        # TIER 3: Early Morning Pump & Collapse Short
        tier3_signal = (
            (max_gain_pct >= 10.0) and
            (ltp < vwap * 0.99) and
            (datetime.now().time() <= time(10, 30))
        )

        # TIER 4: High RVOL Shock Reversal to Lower Circuit (Wonderla Setup)
        tier4_signal = (
            (pdc_volume < vol_10d_sma) and
            (rvol >= 4.0) and
            (ltp < day_open * 0.975)
        )

        # Collect and return stock data if any Tier triggers
        if tier1_signal or tier2_signal or tier3_signal or tier4_signal:
            return {
                "Symbol": symbol.replace(".NS", ""),
                "LTP": round(ltp, 2),
                "Day Gain %": f"{day_gain_pct:+.2f}%",
                "RVOL": f"{rvol:.1f}x",
                "VWAP": round(vwap, 2),
                "Turnover (1m)": f"₹{turnover_1m / 100000:.1f}L",
                "Tier 1 (TBZ)": "🟢 TRIGGERED" if tier1_signal else "-",
                "Tier 2 (RESPONIND)": "⚡ STEALTH" if tier2_signal else "-",
                "Tier 3 (Pump Short)": "🔴 COLLAPSE" if tier3_signal else "-",
                "Tier 4 (Wonderla)": "🚨 SHOCK DUMP" if tier4_signal else "-"
            }
    except Exception:
        return None

# -------------------------------------------------------------------
# STREAMLIT UI & PARALLEL EXECUTION ENGINE
# -------------------------------------------------------------------
st.title("⚡ Multi-Tier Momentum & Short Scanner")
st.caption("Real-Time Institutional Engine for Samsung Fold Execution")

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()

with col2:
    st.info("Status: Scanning Live Market Data (Multi-Threaded)")

# Fetch stock data in parallel (ThreadPool)
triggered_stocks = []
with ThreadPoolExecutor(max_workers=10) as executor:
    results = executor.map(analyze_ticker, WATCHLIST)
    for res in results:
        if res:
            triggered_stocks.append(res)

# Display Results Table
if triggered_stocks:
    df_results = pd.DataFrame(triggered_stocks)
    st.subheader("🎯 High-Probability Setups Detected")
    st.dataframe(df_results, use_container_width=True)
else:
    st.warning("Market is closed or no stocks currently match Tier 1-4 criteria.")
