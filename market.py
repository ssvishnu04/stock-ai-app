import requests
import pandas as pd

headers = {
    "User-Agent": "Mozilla/5.0"
}

# 🔥 Top Gainers
def get_top_gainers():
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=25&scrIds=day_gainers"
    data = requests.get(url, headers=headers).json()

    quotes = data['finance']['result'][0]['quotes']
    return [q['symbol'] for q in quotes]


# 🔥 Most Active
def get_most_active():
    url = "https://query1.finance.yahoo.com/v1/finance/screener/predefined/saved?count=25&scrIds=most_actives"
    data = requests.get(url, headers=headers).json()

    quotes = data['finance']['result'][0]['quotes']
    return [q['symbol'] for q in quotes]


# 🔥 Trending (fallback = tech leaders)
def get_trending():
    return ["AAPL", "NVDA", "TSLA", "AMD", "META", "AMZN"]