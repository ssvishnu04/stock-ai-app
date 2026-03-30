import streamlit as st
import pandas as pd
import yfinance as yf

from screener import run_screener
from market import get_most_active

# ---------------------------
# Page Config
# ---------------------------
st.set_page_config(
    page_title="AI Stock Scanner",
    page_icon="📈",
    layout="wide"
)

# ---------------------------
# HEADER
# ---------------------------
st.markdown("""
# 📊 Stock Signal Engine
### AI Trading Assistant
""")

# ---------------------------
# MODE + VIEW
# ---------------------------
col1, col2 = st.columns(2)

with col1:
    option = st.selectbox(
        "Select Mode",
        ["🔥 Best Opportunities", "📊 All Signals"]
    )

with col2:
    view_mode = st.selectbox(
        "View Mode",
        ["📱 Mobile Cards", "📋 Table"]
    )

# ---------------------------
# DATA
# ---------------------------
tickers = get_most_active()

# ---------------------------
# RUN ANALYSIS
# ---------------------------
if st.button("🚀 Run Analysis"):

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

        # ---------------------------
        # SIGNAL PRIORITY
        # ---------------------------
        signal_priority = {
            "STRONG BUY 🟢🔥": 5,
            "BUY 🟢": 4,
            "HOLD 🟡": 3,
            "WAIT 🟡": 2,
            "AVOID 🔴": 1
        }

        df["Priority"] = df["Signal"].map(signal_priority)

        df = df.sort_values(by=["Priority", "Score"], ascending=[False, False])

        # ---------------------------
        # FILTER
        # ---------------------------
        if option == "🔥 Best Opportunities":
            df = df[df["Signal"].str.contains("BUY")]

        if df.empty:
            st.warning("No BUY signals found.")
        else:
            best = df.iloc[0]

            # ---------------------------
            # BEST PICK
            # ---------------------------
            st.markdown("## 🔥 Best Trade Opportunity")

            col1, col2 = st.columns(2)

            with col1:
                st.metric("Ticker", best["Ticker"])
                st.metric("Signal", best["Signal"])

            with col2:
                st.metric("Entry", f"${best['Entry Price']}")
                st.metric("Current", f"${best['Current Price']}")

            st.markdown(f"""
**🎯 Target:** ${best['Target Price']}  
**🛑 Stop Loss:** ${best['Stop Loss']}  

**📊 Confidence:** {best['Confidence']}%  
**⚠️ Risk:** {best['Risk']}  

**🧠 Why:** {best['Explanation']}
""")

            # ---------------------------
            # STOCK DISPLAY
            # ---------------------------
            st.markdown("## 📊 Stock Signals")

            if view_mode == "📱 Mobile Cards":
                for _, row in df.iterrows():
                    st.markdown("---")
                    st.markdown(f"### {row['Ticker']} — {row['Signal']}")

                    col1, col2 = st.columns(2)

                    with col1:
                        st.write(f"💰 Entry: ${row['Entry Price']}")
                        st.write(f"📈 Current: ${row['Current Price']}")

                    with col2:
                        st.write(f"🎯 Target: ${row['Target Price']}")
                        st.write(f"🛑 Stop: ${row['Stop Loss']}")

                    st.write(f"📊 Confidence: {row['Confidence']}%")
                    st.write(f"⚠️ Risk: {row['Risk']}")
                    st.write(f"🧠 {row['Explanation']}")

            else:
                display_df = df.drop(columns=["Priority"])
                st.dataframe(display_df, use_container_width=True)

            # ---------------------------
            # 🔥 SELECTABLE CHART (FIX)
            # ---------------------------
            st.markdown("## 📈 Select Stock for Chart")

            selected_ticker = st.selectbox(
                "Choose a stock",
                df["Ticker"].tolist()
            )

            st.markdown(f"## 📈 Chart: {selected_ticker}")

            chart_data = yf.download(selected_ticker, period="3mo", progress=False)

            if not chart_data.empty:
                st.line_chart(chart_data['Close'], height=300)
            else:
                st.warning("Chart data not available.")
