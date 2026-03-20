import os
import httpx
import pandas as pd
from datetime import datetime
from telegram.ext import ApplicationBuilder, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

VIP_CHANNEL = "@OmarSwingVIP"

signals_today = 0
today_date = datetime.utcnow().date()

# ---------- DATA ----------
async def get_data(symbol, interval):
    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=200&apikey={TWELVEDATA_API_KEY}"
    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()

    df = pd.DataFrame(data["values"])
    df = df[["open","high","low","close"]].astype(float)
    return df.iloc[::-1]

# ---------- FINNHUB ----------
async def get_finnhub_price(symbol):
    mapping = {
        "XAU/USD": "OANDA:XAU_USD",
        "EUR/USD": "OANDA:EUR_USD"
    }

    url = f"https://finnhub.io/api/v1/quote?symbol={mapping[symbol]}&token={FINNHUB_API_KEY}"

    async with httpx.AsyncClient() as client:
        r = await client.get(url)
        data = r.json()

    return float(data["c"]) if "c" in data else None

# ---------- TREND ----------
def trend(df):
    ema50 = df["close"].ewm(50).mean().iloc[-1]
    ema200 = df["close"].ewm(200).mean().iloc[-1]
    return "BUY" if ema50 > ema200 else "SELL"

# ---------- ENGINE ----------
async def check_signal(context: ContextTypes.DEFAULT_TYPE):

    print("RUNNING...")

    for symbol in ["XAU/USD", "EUR/USD"]:

        try:
            df = await get_data(symbol, "5min")
            price = df["close"].iloc[-1]

            # Finnhub confirm
            f_price = await get_finnhub_price(symbol)
            if not f_price:
                continue

            if abs(price - f_price) > price * 0.002:
                continue

            main_trend = trend(df)
            f_trend = "BUY" if f_price > df["close"].ewm(50).mean().iloc[-1] else "SELL"

            if main_trend != f_trend:
                continue

            sl = price - 5 if main_trend == "BUY" else price + 5
            tp = price + 10 if main_trend == "BUY" else price - 10

            text = f"{symbol} {main_trend}\nEntry: {price}\nSL: {sl}\nTP: {tp}"

            await context.bot.send_message(chat_id=VIP_CHANNEL, text=text)

            print("Signal sent:", symbol)

        except Exception as e:
            print("ERROR:", e)

# ---------- BOT ----------
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.job_queue.run_repeating(check_signal, interval=60, first=10)

print("BOT STARTED")

app.run_polling()
