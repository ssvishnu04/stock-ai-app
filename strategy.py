def relative_strength(stock_df, spy_df):
    stock_return = stock_df['Close'].pct_change().mean()
    spy_return = spy_df['Close'].pct_change().mean()

    return float(stock_return - spy_return)


def get_value(x):
    """Safely extract scalar value"""
    try:
        return float(x.iloc[0]) if hasattr(x, "iloc") else float(x)
    except:
        return float(x)

def score_stock(df, spy_df):
    latest = df.iloc[-1]

    score = 0

    if latest['ema20'] > latest['ema50']:
        score += 20

    if latest['rsi'] > 40:
        score += 20

    if latest['Volume'] > 1.2 * latest['volume_avg']:
        score += 15

    rs = relative_strength(df, spy_df)
    if rs > 0:
        score += 20

    return score


def get_entry_price(df):
    latest = df.iloc[-1]
    return round(latest['ema20'], 2)