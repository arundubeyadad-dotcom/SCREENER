import streamlit as st
import pandas as pd

# Streamlit Page Config (Samsung Fold & Mobile Friendly)
st.set_page_config(page_title="Multi-Tier Momentum & Short Scanner", layout="wide")

# Page Title
st.title("⚡ Multi-Tier Momentum & Short Scanner")
st.caption("Real-Time Institutional Engine | Samsung Fold Screen Optimized")

# Audio Alert Function (HTML5 Web Audio API)
def play_beep_alert():
    sound_html = """
    <audio autoplay style="display:none;">
        <source src="data:audio/wav;base64,UklGRl9vT19XQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YU1vT18AAAAA//8AAAMACQAPABUAGwAgACYAKgAvADMANwA7AD8AQwBHAEsATgBSAFYAWgBkAG4AdgCBAIUAkACaAKIAqwCzA7sAvwLEAM0A1QDdAOEA5wDsAPEAAAAAAA==" type="audio/wav">
    </audio>
    """
    st.components.v1.html(sound_html, height=0, width=0)

# Browser Autoplay Permission Note
st.info("💡 **Tip:** Tap/Click anywhere on the app page once when opening in the morning to grant browser audio permissions.")

# Top Refresh Bar
if st.button("🔄 Refresh Data"):
    st.rerun()

# --- MOCK / DATA ENGINE SECTION ---
# (Replace this dictionary with your live Dhan/ScanX data pipeline)
data = {
    'Symbol': ['RESPONIND', 'INDOCO', 'IMFA', 'KRBL'],
    'LTP': [151.99, 266.50, 1288.00, 423.40],
    'Day Gain %': ['+0.08%', '-2.22%', '+0.49%', '-0.35%'],
    'RVOL': ['0.5x', '3.2x', '3.3x', '3.9x'],
    'VWAP': [168.53, 266.39, 1288.33, 421.40],
    'Turnover (1m)': ['₹92.2L', '₹17.2L', '₹19.7L', '₹20.7L'],
    'Tier 1 (TBZ)': ['-', '-', '-', '-'],
    'Tier 2 (Stealth)': ['-', '⚡ STEALTH', '⚡ STEALTH', '⚡ STEALTH'],
    'Tier 3 (Pump Short)': ['🔴 COLLAPSE', '-', '-', '-'],
    'Tier 4 (Shock Dump)': ['-', '-', '-', '-']
}

df = pd.DataFrame(data)

# --- DISPLAY MAIN DASHBOARD ---
st.subheader("🎯 Active Setups Dashboard")
st.dataframe(df, use_container_width=True)

# --- SMART "NEW ARRIVAL" SOUND ALERT LOGIC ---
# Identify all symbols currently present in ANY tier
tier_columns = ['Tier 1 (TBZ)', 'Tier 2 (Stealth)', 'Tier 3 (Pump Short)', 'Tier 4 (Shock Dump)']

# Filter rows where at least one tier column has an active signal (not '-')
active_signals_df = df[df[tier_columns].ne('-').any(axis=1)]
current_active_symbols = set(active_signals_df['Symbol'].tolist())

# Initialize session state memory for tracked symbols
if 'previous_active_symbols' not in st.session_state:
    st.session_state['previous_active_symbols'] = set()

# Check if there are any NEW symbols that were not in the previous scan
new_symbols = current_active_symbols - st.session_state['previous_active_symbols']

if new_symbols:
    play_beep_alert()
    new_stocks_str = ", ".join(new_symbols)
    st.toast(f"🔔 NEW SIGNAL: {new_stocks_str} entered scanner!", icon="⚠️")

# Update memory for the next refresh cycle
st.session_state['previous_active_symbols'] = current_active_symbols
