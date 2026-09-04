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
    .stMetric { background-color: #1e222d; padding: 8px; border-radius: 8px; }
    div[data-testid="stTable"] { font-size: 0.85rem; }
</style>
""", unsafe_allow_html=True)

# -------------------------------------------------------------------
# BROAD UNIVERSE: Focused on MidSmall 400, MicroCap 250 & High-Beta Movers
# NO Large-Cap Heavyweights included to avoid false triggers
# -------------------------------------------------------------------
WATCHLIST = [
    # Core Strategy Examples
    "TBZ.NS", "RESPONIND.NS", "WONDERLA.NS",
    
    # High-Beta Momentum / Breakout Names
    "KALYANKJIL.NS", "SUZLON.NS", "IRFC.NS", "RVNL.NS", "RAILTEL.NS", 
    "BSOFT.NS", "HFCL.NS", "MAZDOCK.NS", "COCHINSHIP.NS", "FACT.NS", 
    "HUDCO.NS", "NBCC.NS", "ENGINERSIN.NS", "JPPOWER.NS", "IDEA.NS",
    
    # Nifty MidSmall & MicroCap Explosive Trackers
    "CUPID.NS", "AEROFLEX.NS", "SANSERA.NS", "SKYGOLD.NS", "TDPOWERSYS.NS",
    "AVALON.NS", "HAPPYFORGE.NS", "GARFIBRES.NS", "DIAMONDYD.NS", "BLACKBOX.NS",
    "INDIAGLYCO.NS", "SUBROS.NS", "JAMNAAUTO.NS", "FINPIPE.NS", "INDOCO.NS",
    "MSTCLTD.NS", "RCF.NS", "MASTEK.NS", "AARTIDRUGS.NS", "ASHAPURMIN.NS",
    "RATNAMANI.NS", "MARKSANS.NS", "TILAK.NS", "PRAJIND.NS", "AVANTIFEED.NS",
    "HERITGFOOD.NS", "ASTRAMICRO.NS", "OPTiemus.NS", "SHILPAMED.NS", "BALAMINES.NS",
    "CSBBANK.NS", "JKPAPER.NS", "IMFA.NS", "KTKBANK.NS", "BALUFORGE.NS",
    "KRBL.NS", "SOUTHBANK.NS", "SHAKTIPUMP.NS", "SHAILY.NS", "AHLUCONT.NS",
    "AURIONPRO.NS", "SIRCA.NS", "HGINFRA.NS", "KOLTEPATIL.NS", "JWL.NS"
]

# -------------------------------------------------------------------
# CORE TICKER ANALYSIS
# -------------------------------------------------------------------
def analyze_ticker(symbol):
    try:
        ticker = yf.Ticker(symbol)
        df_1m = ticker.history(period="1d", interval="1m")
        df_daily = ticker.history(period="15d", interval="1d")

        if df_1m.empty or len(df_daily) < 11:
            return None

        # Data Points Extraction
        ltp = df_1m['Close'].iloc[-1]
        day_open = df_1m['Open'].iloc[0]
        day_high = df_1m['High'].max()
        day_low = df_1m['Low'].min()
        pdc = df_daily['Close'].iloc[-2]
        
        # Historical Volume Metrics
        pdc_volume = df_daily['Volume'].iloc[-2]
        vol_5d_sma = df_daily['Volume'].iloc[-7:-2].mean()
        vol_10d_sma = df_daily['Volume'].iloc[-12:-2].mean()
        
        # Real-time 1-Minute Metrics
        curr_1m_vol = df_1m['Volume'].iloc[-1]
        avg_1m_vol = df_1m['Volume'].tail(20).mean()
        rvol = curr_1m_vol / avg_1m_vol if avg_1m_vol > 0 else 0
        
        # 1-Min Turnover Safeguard (Min ₹10 Lakhs)
        turnover_1m = ltp * curr_1m_vol
        
        # Candle Body Ratio (Filters out manipulation wicks/fake spikes)
        candle_open = df_1m['Open'].iloc[-1]
        candle_close = df_1m['Close'].iloc[-1]
        candle_high = df_1m['High'].iloc[-1]
        candle_low = df_1m['Low'].iloc[-1]
        range_hl = candle_high - candle_low
        body_ratio = abs(candle_close - candle_open) / range_hl if range_hl > 0 else 0

        # Intraday VWAP Calculation
        v_sum = df_1m['Volume'].sum()
        vwap = (df_1m['Close'] * df_1m['Volume']).sum() / v_sum if v_sum > 0 else ltp

        # Percentage Dynamics
        open_gap_pct = ((day_open - pdc) / pdc) * 100
        candle1_change_pct = ((df_1m['Close'].iloc[0] - df_1m['Open'].iloc[0]) / df_1m['Open'].iloc[0]) * 100
        day_gain_pct = ((ltp - pdc) / pdc) * 100
        max_gain_pct = ((day_high - day_open) / day_open) * 100

        # Dynamic Circuit Proximity Estimates (+20% Upper, -20% Lower Band Caps)
        approx_upper_circuit = pdc * 1.195
        approx_lower_circuit = pdc * 0.805

        # ---------------------------------------------------------------
        # STRATEGY TIERS (STRICT INSTITUTIONAL MATH)
        # ---------------------------------------------------------------
        
        # TIER 1: Catalyst High-Gap Surge (TBZ Setup)
        # Target: Gap +1% to +4%, 1st-min surge >3%, RVOL >= 5.0x, Body >= 0.65
        # Safeguard: Hide if already locked in Upper Circuit (LTP >= 97% of UC)
        tier1_signal = (
            (1.0 <= open_gap_pct <= 4.0) and
            (candle1_change_pct >= 3.0) and
            (rvol >= 5.0) and
            (body_ratio >= 0.65) and
            (turnover_1m >= 1_000_000) and
            (ltp < approx_upper_circuit * 0.97)
        )

        # TIER 2: Dry Liquidity Stealth Surge (Responsive Industries Setup)
        # Target: Dry prior volume (PDC < 5 Lakhs OR PDC < 5-Day SMA)
        # STRICT FIX: Max hard cap on PDC Volume (< 15 Lakhs) to eliminate index heavyweights
        tier2_signal = (
            (pdc_volume < 500_000 or pdc_volume < vol_5d_sma) and
            (pdc_volume < 1_500_000) and  # Excludes large caps
            (rvol >= 3.0) and
            (turnover_1m >= 1_000_000)
        )

        # TIER 3: Early Morning Pump & Collapse Short
        # Target: Early surge >= +10%, breakdown below VWAP by 10:30 AM
        tier3_signal = (
            (max_gain_pct >= 10.0) and
            (ltp < vwap * 0.99) and
            (datetime.now().time() <= time(10, 30))
        )

        # TIER 4: High RVOL Shock Reversal (Wonderla Setup)
        # Target: Prior Vol < 10D SMA, high RVOL dump, price < 2.5% below Open
        # Safeguard: Hide if already locked at Lower Circuit floor
        tier4_signal = (
            (pdc_volume < vol_10d_sma) and
            (rvol >= 4.0) and
            (ltp < day_open * 0.975) and
            (ltp > approx_lower_circuit * 1.03)
        )

        # Return matching stocks
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
# STREAMLIT INTERFACE & EXECUTOR
# -------------------------------------------------------------------
st.title("⚡ Multi-Tier Momentum & Short Scanner")
st.caption("Real-Time Institutional Engine | Samsung Fold Screen Optimized")

col1, col2 = st.columns([1, 3])
with col1:
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()

with col2:
    st.info("Status: Scanning MidSmall 400 & MicroCap 250 Watchlist")

# Parallel Execution using ThreadPoolExecutor
triggered_stocks = []
with ThreadPoolExecutor(max_workers=15) as executor:
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
