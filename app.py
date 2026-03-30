import streamlit as st
import pandas as pd
import yfinance as yf

from screener import run_screener
from market import get_most_active

st.set_page_config(page_title="AI Stock Scanner", page_icon="📈", layout="wide")

st.markdown("# 📊 Stock Signal Engine\n### AI Trading Assistant")

col1, col2 = st.columns(2)

with col1:
    option = st.selectbox("Select Mode", ["🔥 Best Opportunities", "📊 All Signals"])

with col2:
    view_mode = st.selectbox("View Mode", ["📱 Mobile Cards", "📋 Table"])

tickers = get_most_active()

# Run Analysis
if st.button("🚀 Run Analysis"):
    with st.spinner("Analyzing stocks..."):
        st.session_state.results = run_screener(tickers, limit=25)

# Load results
if "results" in st.session_state:

    df = pd.DataFrame(st.session_state.results)

    df.columns = [
        "Ticker", "Score", "Entry Price", "Current Price", "Signal",
        "Confidence", "Risk", "Stop Loss", "Target Price",
        "52W High", "52W Low", "Explanation"
    ]

    df["% Difference"] = ((df["Current Price"] - df["Entry Price"]) / df["Entry Price"]) * 100
    df["% Difference"] = df["% Difference"].round(2)

    signal_priority = {
        "STRONG BUY 🟢🔥": 5,
        "BUY 🟢": 4,
        "HOLD 🟡": 3,
        "WAIT 🟡": 2,
        "AVOID 🔴": 1
    }

    df["Priority"] = df["Signal"].map(signal_priority)
    df = df.sort_values(by=["Priority", "Score"], ascending=[False, False])

    if option == "🔥 Best Opportunities":
        df = df[df["Signal"].str.contains("BUY")]

    if not df.empty:

        best = df.iloc[0]

        st.markdown("## 🔥 Best Trade Opportunity")

        col1, col2 = st.columns(2)
        col1.metric("Ticker", best["Ticker"])
        col1.metric("Signal", best["Signal"])
        col2.metric("Entry", f"${best['Entry Price']}")
        col2.metric("Current", f"${best['Current Price']}")

        st.markdown(f"""
**🎯 Target:** ${best['Target Price']}  
**🛑 Stop Loss:** ${best['Stop Loss']}  

**📊 Confidence:** {best['Confidence']}%  
**⚠️ Risk:** {best['Risk']}  

**📈 52W High:** ${best['52W High']}  
**📉 52W Low:** ${best['52W Low']}  

**🧠 {best['Explanation']}
""")

        st.markdown("## 📊 Stock Signals")

        if view_mode == "📱 Mobile Cards":
            for _, row in df.iterrows():
                st.markdown("---")
                st.markdown(f"### {row['Ticker']} — {row['Signal']}")
                st.write(f"Entry: ${row['Entry Price']} | Current: ${row['Current Price']}")
                st.write(f"Target: ${row['Target Price']} | Stop: ${row['Stop Loss']}")
                st.write(f"Confidence: {row['Confidence']}% | Risk: {row['Risk']}")
                st.write(f"52W High: ${row['52W High']} | 52W Low: ${row['52W Low']}")
                st.write(f"{row['Explanation']}")
        else:
            st.dataframe(df.drop(columns=["Priority"]), use_container_width=True)

        # Clickable tickers
        st.markdown("## 📈 Click a Ticker")

        if "selected_ticker" not in st.session_state:
            st.session_state.selected_ticker = df.iloc[0]["Ticker"]

        cols = st.columns(4)

        for i, ticker in enumerate(df["Ticker"].tolist()):
            label = f"✅ {ticker}" if ticker == st.session_state.selected_ticker else ticker
            if cols[i % 4].button(label):
                st.session_state.selected_ticker = ticker

        selected_ticker = st.session_state.selected_ticker

        st.markdown(f"## 📈 Chart: {selected_ticker}")

        chart_data = yf.download(selected_ticker, period="3mo", progress=False)

        if not chart_data.empty:
            st.line_chart(chart_data["Close"], height=300)
