import os
import httpx
import pandas as pd
from datetime import datetime
from telegram.ext import ApplicationBuilder, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

VIP_CHANNEL = "@OmarSwingVIP"

MAX_SIGNALS = 3
signals_today = 0
today_date = datetime.utcnow().date()

# منع تكرار نفس الصفقة
last_signal = {}

# ---------- GET DATA ----------
async def get_data(symbol, interval="5min"):

    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=200&apikey={TWELVEDATA_API_KEY}"

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()

    df = pd.DataFrame(data["values"])

    df["open"] = df["open"].astype(float)
    df["high"] = df["high"].astype(float)
    df["low"] = df["low"].astype(float)
    df["close"] = df["close"].astype(float)

    return df.iloc[::-1]


# ---------- TREND ----------
def trend_filter(df):

    ema50 = df["close"].ewm(span=50).mean().iloc[-1]
    ema200 = df["close"].ewm(span=200).mean().iloc[-1]

    if ema50 > ema200:
        return "BUY"
    elif ema50 < ema200:
        return "SELL"

    return None


# ---------- ATR ----------
def atr_filter(df):

    df["tr"] = df["high"] - df["low"]
    atr = df["tr"].rolling(14).mean().iloc[-1]
    avg_atr = df["tr"].rolling(50).mean().iloc[-1]

    return atr > avg_atr


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

    return (body / candle_range) > 0.6  # رفعنا الجودة


# ---------- NEWS FILTER ----------
def news_filter():

    hour = datetime.utcnow().hour

    if hour in [12, 13, 14]:
        return False

    return True


# ---------- BUILD SIGNAL ----------
def build_signal(symbol, direction, price, df):

    atr = (df["high"] - df["low"]).rolling(14).mean().iloc[-1]

    # 🔥 SL أذكى (أقل)
    sl_distance = atr * 1.5

    if direction == "BUY":
        sl = price - sl_distance
        tp1 = price + sl_distance
        tp2 = price + (sl_distance * 2)
        tp3 = price + (sl_distance * 3)
    else:
        sl = price + sl_distance
        tp1 = price - sl_distance
        tp2 = price - (sl_distance * 2)
        tp3 = price - (sl_distance * 3)

    symbol = symbol.replace("/", "")

    return f"""{symbol} {direction}
Entry: {round(price,5)}
SL: {round(sl,5)}
TP1: {round(tp1,5)}
TP2: {round(tp2,5)}
TP3: {round(tp3,5)}"""


# ---------- ENGINE ----------
async def check_signal(context: ContextTypes.DEFAULT_TYPE):

    global signals_today, today_date, last_signal

    print("🔄 RUNNING CHECK...")

    now = datetime.utcnow()
    today = now.date()

    if today_date != today:
        signals_today = 0
        today_date = today

    if signals_today >= MAX_SIGNALS:
        return

    if now.hour < 7 or now.hour > 22:
        return

    if not news_filter():
        print("⛔ News time")
        return

    symbols = ["XAU/USD", "EUR/USD"]

    for symbol in symbols:

        print(f"Checking: {symbol}")

        try:
            df_m5 = await get_data(symbol, "5min")
            df_m15 = await get_data(symbol, "15min")
        except Exception as e:
            print("ERROR:", symbol, e)
            continue

        trend_m5 = trend_filter(df_m5)
        trend_m15 = trend_filter(df_m15)

        if trend_m5 != trend_m15:
            continue

        trend = trend_m5
        df = df_m5

        sweep = liquidity_sweep(df)
        momentum = momentum_candle(df)

        score = 0

        if trend:
            score += 2
        if sweep == trend:
            score += 2
        if momentum:
            score += 1
        if atr_filter(df):
            score += 1

        if score < 4:
            continue

        price = df["close"].iloc[-1]

        # ❌ منع التكرار
        key = f"{symbol}_{trend}"
        if last_signal.get(key) == today:
            print("Duplicate skipped")
            continue

        text = build_signal(symbol, trend, price, df)

        try:
            await context.bot.send_message(
                chat_id=VIP_CHANNEL,
                text=text
            )
        except Exception as e:
            print("TELEGRAM ERROR:", e)
            continue

        last_signal[key] = today
        signals_today += 1

        print("✅ Signal sent:", symbol, trend)

        if signals_today >= MAX_SIGNALS:
            break


# ---------- BOT ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.job_queue.run_repeating(
    check_signal,
    interval=60,   # 🔥 أسرع
    first=10
)

print("🔥 AI BOT PRO V2 STARTED")

app.run_polling()
