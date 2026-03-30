import ta

def add_indicators(df):
    df['rsi'] = ta.momentum.RSIIndicator(df['Close']).rsi()
    df['ema20'] = df['Close'].ewm(span=20).mean()
    df['ema50'] = df['Close'].ewm(span=50).mean()
    df['volume_avg'] = df['Volume'].rolling(20).mean()

    return df