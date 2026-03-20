import os
import httpx
import pandas as pd
import requests
import asyncio

# ---------- API ----------
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

LOT = 0.01

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

# ---------- STRUCTURE ----------
def structure_break(df):

    last = df.iloc[-1]

    high_prev = df["high"].iloc[-10:-1].max()
    low_prev = df["low"].iloc[-10:-1].min()

    if last["close"] > high_prev:
        return "BUY"

    if last["close"] < low_prev:
        return "SELL"

    return None

# ---------- SMART ZONE ----------
def get_smart_zone(df):

    swing_high = df["high"].iloc[-20:-1].max()
    swing_low = df["low"].iloc[-20:-1].min()

    return swing_high, swing_low

# ---------- SEND TO MT5 ----------
def send_to_mt5(symbol, direction, lot):

    url = "https://drawn-unhectically-joetta.ngrok-free.dev/trade"

    data = {
        "symbol": symbol,
        "direction": direction,
        "lot": lot
    }

    headers = {
        "ngrok-skip-browser-warning": "true"
    }

    try:
        requests.post(url, json=data, headers=headers)
        print(f"📤 Sent: {symbol} {direction}")
    except Exception as e:
        print("ERROR:", e)

# ---------- ENGINE ----------
async def run_bot():

    print("🚀 AI PRO BOT STARTED")

    while True:

        for symbol in ["XAU/USD","EUR/USD"]:
            print(f"🔍 Checking: {symbol}")
            try:
                df = await get_data(symbol, "5min")
                price = df["close"].iloc[-1]

                f_price = await get_finnhub_price(symbol)
                if not f_price:
                    continue

                if abs(price - f_price) > price * 0.002:
                    continue

                trend_main = trend(df)
                structure = structure_break(df)

                # ❌ لازم يتوافقو
                if trend_main != structure:
                    continue

                high, low = get_smart_zone(df)

                # ---------- ZONE FILTER ----------
                if trend_main == "BUY" and price > (low + 5):
                    continue

                if trend_main == "SELL" and price < (high - 5):
                    continue

                # ---------- SEND ----------
                send_to_mt5(symbol, trend_main, LOT)

                print(f"✅ SIGNAL: {symbol} {trend_main}")

            except Exception as e:
                print("ERROR:", e)

        await asyncio.sleep(60)

# ---------- RUN ----------
asyncio.run(run_bot())
