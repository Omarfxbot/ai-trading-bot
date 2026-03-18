import os
import requests
import pandas as pd
from datetime import datetime
from telegram.ext import ApplicationBuilder, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

VIP_CHANNEL = "@OmarSwingVIP"

MAX_SIGNALS = 3
signals_today = 0
today_date = datetime.utcnow().date()


# ---------- GET DATA ----------
def get_data(symbol):

    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=5min&outputsize=200&apikey={TWELVEDATA_API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()

        if "values" not in data:
            return None

        df = pd.DataFrame(data["values"])

        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)

        df = df.iloc[::-1]

        return df

    except:
        return None


# ---------- TREND ----------
def trend_filter(df):
    ema50 = df["close"].ewm(span=50).mean().iloc[-1]
    ema200 = df["close"].ewm(span=200).mean().iloc[-1]

    if ema50 > ema200:
        return "BUY"
    if ema50 < ema200:
        return "SELL"

    return None


# ---------- VOLATILITY ----------
def atr_filter(df):
    df["tr"] = df["high"] - df["low"]
    atr = df["tr"].rolling(14).mean().iloc[-1]
    return atr > 1


# ---------- MOMENTUM ----------
def momentum(df):
    last = df.iloc[-1]
    body = abs(last["close"] - last["open"])
    rng = last["high"] - last["low"]

    if rng == 0:
        return False

    return (body / rng) > 0.5


# ---------- BUILD SIGNAL ----------
def build_signal(symbol, direction, price):

    if symbol == "EUR/USD":
        sl_dist = 0.002
        tp_dist = 0.003
    else:
        sl_dist = 8
        tp_dist = 6

    if direction == "BUY":
        sl = price - sl_dist
        tp = price + tp_dist
    else:
        sl = price + sl_dist
        tp = price - tp_dist

    return f"""
📊 {symbol} – {direction}

Entry: {round(price,5)}
SL: {round(sl,5)}
TP: {round(tp,5)}
"""


# ---------- ENGINE ----------
async def check_signal(context: ContextTypes.DEFAULT_TYPE):

    global signals_today, today_date

    now = datetime.utcnow()
    hour = now.hour
    today = now.date()

    if today != today_date:
        signals_today = 0
        today_date = today

    if signals_today >= MAX_SIGNALS:
        return

    if hour < 7 or hour > 22:
        return

    pairs = ["XAU/USD", "EUR/USD"]

    for pair in pairs:

        print(f"Checking: {pair}")

        df = get_data(pair)

        if df is None:
            continue

        if not atr_filter(df):
            continue

        if not momentum(df):
            continue

        trend = trend_filter(df)

        if trend is None:
            continue

        price = df["close"].iloc[-1]

        text = build_signal(pair, trend, price)

        await context.bot.send_message(
            chat_id=VIP_CHANNEL,
            text=text
        )

        signals_today += 1

        print("Signal sent:", pair, trend)

        if signals_today >= MAX_SIGNALS:
            break


# ---------- BOT ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.job_queue.run_repeating(
    check_signal,
    interval=300,
    first=10
)

print("AI BOT BALANCE MODE STARTED")

app.run_polling()
