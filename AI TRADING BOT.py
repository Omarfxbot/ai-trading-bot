import os
import requests
import pandas as pd
from datetime import datetime
from telegram.ext import ApplicationBuilder, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

VIP_CHANNEL = "@OmarSwingVIP"

MAX_SIGNALS = 4
signals_today = 0
today_date = datetime.utcnow().date()


# ---------- GET GOLD DATA ----------
def get_gold_data():

    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=5min&outputsize=200&apikey={TWELVEDATA_API_KEY}"

    r = requests.get(url)
    data = r.json()

    df = pd.DataFrame(data["values"])

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)

    df = df.iloc[::-1]

    return df


# ---------- TREND FILTER ----------
def trend_filter(df):

    ema50 = df["close"].ewm(span=50).mean().iloc[-1]
    ema200 = df["close"].ewm(span=200).mean().iloc[-1]

    if ema50 > ema200:
        return "BUY"

    if ema50 < ema200:
        return "SELL"

    return None


# ---------- ATR VOLATILITY ----------
def atr_filter(df):

    df["tr"] = df["high"] - df["low"]
    atr = df["tr"].rolling(14).mean().iloc[-1]

    if atr < 1.5:
        return False

    return True


# ---------- SPREAD FILTER ----------
def spread_filter(df):

    spread = abs(df["high"].iloc[-1] - df["low"].iloc[-1])

    if spread > 3:
        return False

    return True


# ---------- LIQUIDITY SWEEP ----------
def liquidity_sweep(df):

    high_prev = df["high"].iloc[-20:-1].max()
    low_prev = df["low"].iloc[-20:-1].min()

    last = df.iloc[-1]

    if last["high"] > high_prev and last["close"] < last["open"]:
        return "SELL"

    if last["low"] < low_prev and last["close"] > last["open"]:
        return "BUY"

    return None


# ---------- MOMENTUM CANDLE ----------
def momentum_candle(df):

    last = df.iloc[-1]

    body = abs(last["close"] - last["open"])
    candle_range = last["high"] - last["low"]

    if candle_range == 0:
        return False

    strength = body / candle_range

    return strength > 0.6


# ---------- SMART MONEY ORDER BLOCK ----------
def order_block(df):

    impulse = df.iloc[-2]
    base = df.iloc[-3]

    body = abs(impulse["close"] - impulse["open"])
    range_candle = impulse["high"] - impulse["low"]

    if range_candle == 0:
        return None

    strength = body / range_candle

    if strength < 0.6:
        return None

    if impulse["close"] > impulse["open"]:
        if base["close"] < base["open"]:
            return "BUY"

    if impulse["close"] < impulse["open"]:
        if base["close"] > base["open"]:
            return "SELL"

    return None


# ---------- NEWS FILTER ----------
def news_filter():

    try:

        news = requests.get(
            "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
            timeout=5
        ).json()

        now = datetime.utcnow()

        for event in news:

            if event.get("impact") != "High":
                continue

            event_time = datetime.fromisoformat(
                event["date"].replace("Z", "+00:00")
            ).replace(tzinfo=None)

            diff = abs((event_time - now).total_seconds())

            if diff < 1800:
                return False

    except:
        pass

    return True


# ---------- BUILD SIGNAL ----------
def build_signal(direction, price):

    if direction == "BUY":

        sl = price - 8
        tp1 = price + 6
        tp2 = price + 12
        tp3 = price + 18

    else:

        sl = price + 8
        tp1 = price - 6
        tp2 = price - 12
        tp3 = price - 18

    text = f"""
📊 XAUUSD – {direction}

Entry: {price:.2f}
SL: {sl:.2f}

TP1: {tp1:.2f}
TP2: {tp2:.2f}
TP3: {tp3:.2f}

⚡ Quick Copy:
XAUUSD {direction} SL {sl:.2f} TP {tp1:.2f}
"""

    return text


# ---------- MAIN SIGNAL ENGINE ----------
async def check_signal(context: ContextTypes.DEFAULT_TYPE):

    global signals_today
    global today_date

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

    if not news_filter():
        return

    print("Checking: XAU/USD")

    try:

        df = get_gold_data()

    except Exception as e:

        print("Data error:", e)
        return

    if not atr_filter(df):
        return

    if not spread_filter(df):
        return

    trend = trend_filter(df)
    sweep = liquidity_sweep(df)
    momentum = momentum_candle(df)
    ob = order_block(df)

    if trend is None:
        return

    if sweep != trend:
        return

    if not momentum:
        return

    if ob != trend:
        return

    price = df["close"].iloc[-1]

    text = build_signal(trend, price)

    await context.bot.send_message(
        chat_id=VIP_CHANNEL,
        text=text
    )

    signals_today += 1

    print("Signal sent:", trend)


# ---------- BOT ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.job_queue.run_repeating(
    check_signal,
    interval=300,
    first=10
)

print("AI GOLD BOT ELITE STARTED")

app.run_polling()
