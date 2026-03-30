import pandas as pd
import yfinance as yf
import requests
from io import StringIO

# STEP 1: Get S&P 500 tickers
def get_sp500_tickers():
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)

    tables = pd.read_html(StringIO(response.text))
    df = tables[0]

    tickers = df['Symbol'].tolist()
    tickers = [t.replace('.', '-') for t in tickers]

    return tickers


# STEP 2: Download stock data

def get_stock_data(ticker):
    df = yf.download(ticker, period="6mo", interval="1d", progress=False)

    if df is None or df.empty:
        return None

    # 🔥 FIX: Flatten columns if MultiIndex
    if isinstance(df.columns, tuple) or hasattr(df.columns, "levels"):
        df.columns = df.columns.get_level_values(0)

    # 🔥 Ensure columns are 1D
    for col in df.columns:
        df[col] = df[col].squeeze()

    df.dropna(inplace=True)

    return df


# STEP 3: Get SPY data
def get_spy_data():
    return get_stock_data("SPY")