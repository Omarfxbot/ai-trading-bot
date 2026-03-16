import os
import requests
import pandas as pd
from datetime import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")

VIP_CHANNEL = "@OmarSwingVIP"

TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

MAX_SIGNALS = 4

signals_today = 0
today_date = datetime.utcnow().date()

# ---------- GET GOLD DATA ----------

def get_gold_data():

    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=5min&outputsize=200&apikey={TWELVEDATA_API_KEY}"

    r = requests.get(url)
    data = r.json()

    df = pd.DataFrame(data["values"])

    # نخلي غير أعمدة الأسعار
    df = df[['open', 'high', 'low', 'close']]

    # نحولهم لأرقام
    df['open'] = df['open'].astype(float)
    df['high'] = df['high'].astype(float)
    df['low'] = df['low'].astype(float)
    df['close'] = df['close'].astype(float)

    # نقلب الداتا باش يكون القديم الفوق والجديد التحت
    df = df.iloc[::-1].reset_index(drop=True)

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


# ---------- MOMENTUM CANDLE ----------

def momentum_candle(df):

    last = df.iloc[-1]

    size = abs(last["close"] - last["open"])

    if size > 1.5:
        return True

    return False


# ---------- LIQUIDITY ZONE ----------

def liquidity_zone(df):

    last_high = df["high"].rolling(20).max().iloc[-1]

    last_low = df["low"].rolling(20).min().iloc[-1]

    price = df.iloc[-1]["close"]

    if abs(price - last_high) < 1:
        return "SELL"

    if abs(price - last_low) < 1:
        return "BUY"

    return None


# ---------- SIGNAL ENGINE ----------

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

    print("Checking: XAU/USD")

    try:

        df = get_gold_data()

    except Exception as e:
        print("Data error:", e) 
       
        return

    trend = trend_filter(df)

    liquidity = liquidity_zone(df)

    momentum = momentum_candle(df)

    if trend is None:
        return

    if liquidity is None:
        return

    if momentum is False:
        print("Weak candle")
        return

    if trend != liquidity:
        return

    price = df.iloc[-1]["close"]

    if trend == "BUY":

        entry = price
        sl = price - 8
        tp1 = price + 8
        tp2 = price + 16
        tp3 = price + 24

    else:

        entry = price
        sl = price + 8
        tp1 = price - 8
        tp2 = price - 16
        tp3 = price - 24


    text = f"""
📊 XAUUSD – {trend}

Entry: {round(entry,2)}
SL: {round(sl,2)}

TP1: {round(tp1,2)}
TP2: {round(tp2,2)}
TP3: {round(tp3,2)}

⚡ Quick Copy:
XAUUSD {trend} SL {round(sl,2)} TP {round(tp1,2)}
"""

    await context.bot.send_message(
        chat_id=VIP_CHANNEL,
        text=text
    )

    signals_today += 1

    print("Signal sent", trend)


# ---------- BOT ----------

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.job_queue.run_repeating(
    check_signal,
    interval=60,
    first=10
)

print("AI GOLD BOT STARTED")

app.run_polling()
