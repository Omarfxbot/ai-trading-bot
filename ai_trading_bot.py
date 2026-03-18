import os
import requests
import pandas as pd
import psycopg2
from datetime import datetime
from telegram.ext import ApplicationBuilder, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
DATABASE_URL = os.getenv("DATABASE_URL")

VIP_CHANNEL = "@OmarSwingVIP"

MAX_SIGNALS = 3
signals_today = 0
today_date = datetime.utcnow().date()

# ---------- DB ----------
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS signals_ai (
id SERIAL PRIMARY KEY,
symbol TEXT,
direction TEXT,
entry FLOAT,
sl FLOAT,
tp FLOAT,
result TEXT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")
conn.commit()


# ---------- GET DATA ----------
def get_data(symbol, interval):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=200&apikey={TWELVEDATA_API_KEY}"
        r = requests.get(url, timeout=10)
        data = r.json()

        if "values" not in data:
            return None

        df = pd.DataFrame(data["values"])

        for col in ["open","high","low","close"]:
            df[col] = df[col].astype(float)

        df = df.iloc[::-1]
        return df
    except:
        return None


# ---------- TREND ----------
def trend(df):
    ema50 = df["close"].ewm(span=50).mean().iloc[-1]
    ema200 = df["close"].ewm(span=200).mean().iloc[-1]

    if ema50 > ema200:
        return "BUY"
    if ema50 < ema200:
        return "SELL"
    return None


# ---------- MOMENTUM ----------
def strong_candle(df):
    last = df.iloc[-1]
    body = abs(last["close"] - last["open"])
    rng = last["high"] - last["low"]

    if rng == 0:
        return False

    return (body / rng) > 0.6


# ---------- STRUCTURE ----------
def break_structure(df):
    high_prev = df["high"].iloc[-20:-1].max()
    low_prev = df["low"].iloc[-20:-1].min()

    last = df.iloc[-1]

    if last["close"] > high_prev:
        return "BUY"
    if last["close"] < low_prev:
        return "SELL"

    return None


# ---------- BUILD ----------
def build_signal(symbol, direction, price):

    if symbol == "EUR/USD":
        sl_dist = 0.002
        tp_dist = 0.004
    else:
        sl_dist = 10
        tp_dist = 12

    if direction == "BUY":
        sl = price - sl_dist
        tp = price + tp_dist
    else:
        sl = price + sl_dist
        tp = price - tp_dist

    text = f"""
📊 {symbol} – {direction}

Entry: {round(price,5)}
SL: {round(sl,5)}
TP: {round(tp,5)}

🔥 Strong Setup
"""

    return text, sl, tp


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

        df_m5 = get_data(pair, "5min")
        df_h1 = get_data(pair, "1h")

        if df_m5 is None or df_h1 is None:
            continue

        trend_m5 = trend(df_m5)
        trend_h1 = trend(df_h1)

        if trend_m5 != trend_h1:
            continue

        structure = break_structure(df_m5)

        if structure != trend_m5:
            continue

        if not strong_candle(df_m5):
            continue

        price = df_m5["close"].iloc[-1]

        text, sl, tp = build_signal(pair, trend_m5, price)

        # إرسال Telegram
        await context.bot.send_message(
            chat_id=VIP_CHANNEL,
            text=text
        )

        # تخزين ف database
        cur.execute("""
        INSERT INTO signals_ai (symbol, direction, entry, sl, tp)
        VALUES (%s, %s, %s, %s, %s)
        """, (pair, trend_m5, price, sl, tp))

        conn.commit()

        signals_today += 1

        print("Saved & Sent:", pair, trend_m5)

        if signals_today >= MAX_SIGNALS:
            break


# ---------- BOT ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.job_queue.run_repeating(
    check_signal,
    interval=300,
    first=10
)

print("AI BOT + STORAGE STARTED")

app.run_polling()
