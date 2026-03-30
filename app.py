import streamlit as st
import pandas as pd
import yfinance as yf

from screener import run_screener
from market import get_most_active

st.set_page_config(page_title="Stock AI App", layout="wide")

st.title("📊 Stock Signal Engine")
st.write("AI-powered trading assistant with risk & confidence insights")

option = st.selectbox(
    "Select Mode",
    ["🔥 Best Opportunities", "📊 All Signals"]
)

tickers = get_most_active()

st.write(f"Scanning {len(tickers)} active stocks...")

if st.button("Run Analysis"):

    with st.spinner("Analyzing stocks..."):
        results = run_screener(tickers, limit=25)

    df = pd.DataFrame(results)

    if df.empty:
        st.warning("No results found.")
    else:
        df.columns = [
            "Ticker",
            "Score",
            "Entry Price",
            "Current Price",
            "Signal",
            "Confidence",
            "Risk",
            "Stop Loss",
            "Target Price",
            "Explanation"
        ]

        # % Difference
        df["% Difference"] = (
            (df["Current Price"] - df["Entry Price"]) / df["Entry Price"]
        ) * 100
        df["% Difference"] = df["% Difference"].round(2)

        # Priority ranking
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

        if df.empty:
            st.warning("No BUY signals found.")
        else:
            best = df.iloc[0]

            st.success(
                f"🔥 BEST PICK: {best['Ticker']} | {best['Signal']}\n\n"
                f"Entry: ${best['Entry Price']} | Current: ${best['Current Price']}\n"
                f"🎯 Target: ${best['Target Price']} | 🛑 Stop: ${best['Stop Loss']}\n"
                f"📊 Confidence: {best['Confidence']}% | ⚠️ Risk: {best['Risk']}\n\n"
                f"🧠 {best['Explanation']}"
            )

            # Clean display
            display_df = df.drop(columns=["Priority"])

            st.subheader("📋 Stock Rankings")
            st.dataframe(display_df, use_container_width=True)

            # Chart
            st.subheader(f"📈 Chart: {best['Ticker']}")

            chart_data = yf.download(best['Ticker'], period="3mo", progress=False)

            if not chart_data.empty:
                st.line_chart(chart_data['Close'])