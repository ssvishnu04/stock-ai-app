from data import get_stock_data, get_spy_data
from indicators import add_indicators
from strategy import score_stock, get_entry_price

# ---------------------------
# AI Explanation
# ---------------------------
def generate_explanation(score, diff_pct, df):
    reasons = []
    latest = df.iloc[-1]

    if latest['ema20'] > latest['ema50']:
        reasons.append("Strong uptrend")

    if latest['rsi'] > 60:
        reasons.append("High momentum")

    if latest['Volume'] > latest['volume_avg']:
        reasons.append("Above-average volume")

    if abs(diff_pct) <= 2:
        reasons.append("Near ideal entry zone")

    return ", ".join(reasons) if reasons else "Weak setup"


# ---------------------------
# Confidence Score
# ---------------------------
def calculate_confidence(score, diff_pct):
    confidence = score

    if abs(diff_pct) <= 2:
        confidence += 10
    elif abs(diff_pct) > 5:
        confidence -= 10

    return min(max(confidence, 0), 100)


# ---------------------------
# Risk Level
# ---------------------------
def calculate_risk(df):
    recent_range = (df['High'].iloc[-10:].max() - df['Low'].iloc[-10:].min())

    if recent_range < 2:
        return "LOW 🟢"
    elif recent_range < 5:
        return "MEDIUM 🟡"
    else:
        return "HIGH 🔴"


# ---------------------------
# Stop Loss & Target
# ---------------------------
def calculate_trade_levels(entry, df):
    ema50 = df['ema50'].iloc[-1]

    stop_loss = round(min(entry * 0.97, ema50), 2)

    risk = entry - stop_loss
    target = round(entry + (risk * 2), 2)

    return stop_loss, target


# ---------------------------
# Main Screener
# ---------------------------
def run_screener(tickers, limit=20):
    spy_df = get_spy_data()
    results = []

    for ticker in tickers[:limit]:
        try:
            df = get_stock_data(ticker)

            if df is None or df.empty:
                continue

            if df['Volume'].mean() < 1_000_000:
                continue

            df = add_indicators(df)

            score = score_stock(df, spy_df)
            entry = get_entry_price(df)

            latest_price = round(df['Close'].iloc[-1], 2)

            diff_pct = ((latest_price - entry) / entry) * 100

            # Signals
            if score >= 75 and abs(diff_pct) <= 1.5:
                signal = "STRONG BUY 🟢🔥"
            elif score >= 60 and abs(diff_pct) <= 2:
                signal = "BUY 🟢"
            elif score >= 50:
                signal = "HOLD 🟡"
            elif diff_pct > 3:
                signal = "WAIT 🟡"
            else:
                signal = "AVOID 🔴"

            # Metrics
            confidence = calculate_confidence(score, diff_pct)
            risk = calculate_risk(df)
            stop_loss, target = calculate_trade_levels(entry, df)
            explanation = generate_explanation(score, diff_pct, df)

            # 52-week range
            week_52_high = round(df['High'].rolling(252).max().iloc[-1], 2)
            week_52_low = round(df['Low'].rolling(252).min().iloc[-1], 2)

            results.append({
                "ticker": ticker,
                "score": score,
                "entry": round(entry, 2),
                "current_price": latest_price,
                "signal": signal,
                "confidence": confidence,
                "risk": risk,
                "stop_loss": stop_loss,
                "target": target,
                "52w_high": week_52_high,
                "52w_low": week_52_low,
                "explanation": explanation
            })

        except Exception:
            continue

    results = sorted(results, key=lambda x: x['score'], reverse=True)

    return results
