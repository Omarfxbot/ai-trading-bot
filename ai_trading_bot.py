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
def parse_signal(text):

    # normalize
    text = text.replace("/", "").upper()

    # SYMBOL + ACTION
    symbol = re.search(r"(XAUUSD|EURUSD)", text)
    action = re.search(r"\b(BUY|SELL)\b", text)

    # SL
    sl = re.search(r"SL[:\s]*([\d.]+)", text)

    # TP واحد (ماشي TP1)
    tp = re.search(r"\bTP(?!\d)[:\s]*([\d.]+)", text)

    # TP متعدد
    tp1 = re.search(r"TP1[:\s]*([\d.]+)", text)
    tp2 = re.search(r"TP2[:\s]*([\d.]+)", text)
    tp3 = re.search(r"TP3[:\s]*([\d.]+)", text)

    # ENTRY (اختياري للمستقبل)
    entry = re.search(r"ENTRY[:\s]*([\d.]+)", text)

    if not symbol or not action or not sl:
        return None

    return (
        symbol.group(1),
        action.group(1),
        float(sl.group(1)),
        float(tp.group(1)) if tp else None,
        float(tp1.group(1)) if tp1 else None,
        float(tp2.group(1)) if tp2 else None,
        float(tp3.group(1)) if tp3 else None,
        float(entry.group(1)) if entry else None,  # optional
    )


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
