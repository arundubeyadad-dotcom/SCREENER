import streamlit as st
import yfinance as yf
import pandas as pd

st.set_page_config(page_title="Intraday Volume Acceleration Screener", layout="wide")
st.title("⚡ Intraday RVOL & Volume Surge Screener")

TICKERS = [
    "RESPONIND.NS", "MASTERT.NS", "HBLPOWER.NS", "EXICOM.NS", 
    "RADHIKAJEW.NS", "JAINIRRIG.NS", "MMTC.NS", "ACME.NS"
]

@st.cache_data(ttl=60)
def fetch_screener_data():
    results = []
    for ticker in TICKERS:
        try:
            df = yf.download(ticker, period="5d", interval="1m", progress=False)
            if df.empty or len(df) < 20:
                continue
            
            last_close = float(df['Close'].iloc[-1])
            prev_close = float(df['Close'].iloc[-2])
            curr_vol = float(df['Volume'].iloc[-1])
            avg_vol = float(df['Volume'].iloc[-20:].mean())
            
            rvol = curr_vol / avg_vol if avg_vol > 0 else 0
            pct_change = ((last_close - prev_close) / prev_close) * 100
            
            results.append({
                "Stock": ticker.replace(".NS", ""),
                "Price (₹)": round(last_close, 2),
                "1M Change (%)": round(pct_change, 2),
                "Current 1M Vol": int(curr_vol),
                "RVOL Surge": round(rvol, 2),
                "Status": "🔥 HIGH ACCELERATION" if rvol >= 3.0 else "NORMAL"
            })
        except Exception:
            continue
    return pd.DataFrame(results)

if st.button("🔄 Refresh Data"):
    st.cache_data.clear()

data = fetch_screener_data()

if not data.empty:
    st.dataframe(
        data.style.highlight_between(subset=["RVOL Surge"], left=3.0, right=100.0, color="#1b5e20"),
        use_container_width=True,
        height=500
    )
