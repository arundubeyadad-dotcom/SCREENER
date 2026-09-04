import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Stealth Momentum RVOL Screener", layout="wide")
st.title("⚡ Stealth Momentum & Volume Surge Engine")

# Broad Momentum Watchlist (Expandable to Nifty 500 / MicroCap 250)
WATCHLIST = [
    "RESPONIND.NS", "MASTERT.NS", "HBLPOWER.NS", "EXICOM.NS", 
    "RADHIKAJEW.NS", "JAINIRRIG.NS", "MMTC.NS", "ACME.NS",
    "GMRINFRA.NS", "SUZLON.NS", "IRFC.NS", "RVNL.NS", "IDEA.NS"
]

@st.cache_data(ttl=30)
def scan_stealth_stocks():
    screener_output = []
    
    for ticker in WATCHLIST:
        try:
            # Fetch intraday 1-min data + daily data for PDC
            stock = yf.Ticker(ticker)
            df_min = stock.history(period="2d", interval="1m")
            df_day = stock.history(period="5d", interval="1d")
            
            if df_min.empty or len(df_min) < 20 or len(df_day) < 2:
                continue
                
            pdc = float(df_day['Close'].iloc[-2])
            open_price = float(df_min['Open'].iloc[0])
            last_price = float(df_min['Close'].iloc[-1])
            
            # 1. Flat Open Condition (Within -1.5% to +1.5% of PDC)
            open_gap_pct = ((open_price - pdc) / pdc) * 100
            is_flat_open = abs(open_gap_pct) <= 1.5
            
            # 2. RVOL Surge Calculation (Current 1m Vol vs 20m Avg Vol)
            curr_vol = float(df_min['Volume'].iloc[-1])
            avg_vol = float(df_min['Volume'].iloc[-20:-1].mean())
            rvol = curr_vol / avg_vol if avg_vol > 0 else 0.0
            
            # 3. Price Acceleration
            day_high = float(df_min['High'].max())
            day_low = float(df_min['Low'].min())
            pct_change_from_pdc = ((last_price - pdc) / pdc) * 100
            
            # Filter: Show stocks with RVOL > 3.0x
            if rvol >= 3.0:
                screener_output.append({
                    "Stock": ticker.replace(".NS", ""),
                    "LTP (₹)": round(last_price, 2),
                    "Flat Open Gap (%)": round(open_gap_pct, 2),
                    "Move from PDC (%)": round(pct_change_from_pdc, 2),
                    "1M RVOL Surge": round(rvol, 2),
                    "1M Vol": int(curr_vol),
                    "Setup Signal": "🔥 STEALTH BREAKOUT" if last_price >= day_high * 0.998 else "⚡ HIGH RVOL SURGE"
                })
        except Exception:
            continue
            
    return pd.DataFrame(screener_output)

if st.button("🔄 Live Scan (30s Cache)"):
    st.cache_data.clear()

data = scan_stealth_stocks()

if not data.empty:
    st.dataframe(
        data.style.highlight_between(subset=["1M RVOL Surge"], left=3.0, right=100.0, color="#1b5e20"),
        use_container_width=True,
        height=600
    )
else:
    st.info("Market is closed or no stock currently meets the RVOL >= 3.0x acceleration criteria.")
