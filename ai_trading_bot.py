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

    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=5min&outputsize=200&apikey={TWELVEDATA_API_KEY}"

    r = requests.get(url)
    data = r.json()

    df = pd.DataFrame(data["values"])

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)

    df = df.iloc[::-1]

    return df


# ---------- TREND ----------
def trend_filter(df):

    ema50 = df["close"].ewm(span=50).mean().iloc[-1]
    ema200 = df["close"].ewm(span=200).mean().iloc[-1]

    if ema50 > ema200:
        return "BUY"

    if ema50 < ema200:
        return "SELL"

    return None


# ---------- ATR ----------
def atr_filter(df):

    df["tr"] = df["high"] - df["low"]
    atr = df["tr"].rolling(14).mean().iloc[-1]

    return atr > 0.5


# ---------- SWEEP ----------
def liquidity_sweep(df):

    high_prev = df["high"].iloc[-20:-1].max()
    low_prev = df["low"].iloc[-20:-1].min()

    last = df.iloc[-1]

    if last["high"] > high_prev and last["close"] < last["open"]:
        return "SELL"

    if last["low"] < low_prev and last["close"] > last["open"]:
        return "BUY"

    return None


# ---------- MOMENTUM ----------
def momentum_candle(df):

    last = df.iloc[-1]

    body = abs(last["close"] - last["open"])
    candle_range = last["high"] - last["low"]

    if candle_range == 0:
        return False

    return (body / candle_range) > 0.5


# ---------- SIGNAL ----------
def build_signal(symbol, direction, price):

    if symbol == "XAU/USD":
        sl_dist = 8
        tp_dist = [6, 12, 18]
    else:
        sl_dist = 0.0020
        tp_dist = [0.0015, 0.0030, 0.0045]

    if direction == "BUY":
        sl = price - sl_dist
        tp1 = price + tp_dist[0]
        tp2 = price + tp_dist[1]
        tp3 = price + tp_dist[2]
    else:
        sl = price + sl_dist
        tp1 = price - tp_dist[0]
        tp2 = price - tp_dist[1]
        tp3 = price - tp_dist[2]

    return f"""
📊 {symbol} – {direction}

Entry: {price:.5f}
SL: {sl:.5f}

TP1: {tp1:.5f}
TP2: {tp2:.5f}
TP3: {tp3:.5f}
"""


# ---------- ENGINE ----------
async def check_signal(context: ContextTypes.DEFAULT_TYPE):

    global signals_today, today_date

    now = datetime.utcnow()
    hour = now.hour
    today = now.date()

    if today_date != today:
        signals_today = 0
        today_date = today

    if signals_today >= MAX_SIGNALS:
        return

    if hour < 7 or hour > 22:
        return

    symbols = ["XAU/USD", "EUR/USD"]

    for symbol in symbols:

        print(f"Checking: {symbol}")

        try:
            df = get_data(symbol)
        except:
            continue

        if not atr_filter(df):
            continue

        trend = trend_filter(df)
        sweep = liquidity_sweep(df)
        momentum = momentum_candle(df)

        if trend is None:
            continue

        if sweep != trend:
            continue

        # ⚡ خففنا الشرط هنا
        if not momentum:
            pass  # ما نوقفوش السيگنال

        price = df["close"].iloc[-1]

        text = build_signal(symbol, trend, price)

        await context.bot.send_message(
            chat_id=VIP_CHANNEL,
            text=text
        )

        signals_today += 1

        print("Signal sent:", symbol, trend)

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
