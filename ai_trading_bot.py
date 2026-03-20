import os
import httpx
import pandas as pd
import requests
import asyncio

# ---------- API ----------
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")
ALPHA_API_KEY = os.getenv("ALPHA_API_KEY")  # 🔥 جديد

LOT = 0.01

# ---------- DATA (MAIN + BACKUP) ----------
async def get_data(symbol, interval):

    # ---------- MAIN: TwelveData ----------
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval={interval}&outputsize=200&apikey={TWELVEDATA_API_KEY}"

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            data = r.json()

        if "values" in data:
            df = pd.DataFrame(data["values"])

            if all(col in df.columns for col in ["open","high","low","close"]):
                df = df[["open","high","low","close"]].astype(float)
                return df.iloc[::-1]

        print(f"⚠️ TwelveData failed for {symbol}")

    except Exception as e:
        print(f"❌ TwelveData ERROR {symbol}:", e)

    # ---------- BACKUP: Alpha Vantage ----------
    try:
        print(f"🔁 Using AlphaVantage backup for {symbol}")

        symbol_av = symbol.replace("/", "")
        url = f"https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol={symbol_av[:3]}&to_symbol={symbol_av[3:]}&interval=5min&apikey={ALPHA_API_KEY}"

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            data = r.json()

        key = "Time Series FX (5min)"
        if key in data:
            df = pd.DataFrame(data[key]).T
            df.columns = ["open","high","low","close"]
            df = df.astype(float)
            return df

        print(f"❌ AlphaVantage failed for {symbol}")
        return None

    except Exception as e:
        print(f"❌ Backup ERROR {symbol}:", e)
        return None


# ---------- FINNHUB ----------
async def get_finnhub_price(symbol):

    mapping = {
        "XAU/USD": "OANDA:XAU_USD",
        "EUR/USD": "OANDA:EUR_USD"
    }

    try:
        url = f"https://finnhub.io/api/v1/quote?symbol={mapping[symbol]}&token={FINNHUB_API_KEY}"

        async with httpx.AsyncClient(timeout=10) as client:
            r = await client.get(url)
            data = r.json()

        if "c" not in data or data["c"] is None:
            print(f"❌ No Finnhub price for {symbol}")
            return None

        return float(data["c"])

    except Exception as e:
        print(f"❌ Finnhub ERROR {symbol}:", e)
        return None


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
        requests.post(url, json=data, headers=headers, timeout=10)
        print(f"📤 Sent: {symbol} {direction}")
    except Exception as e:
        print("❌ SEND ERROR:", e)


# ---------- ENGINE ----------
async def run_bot():

    print("🚀 AI PRO BOT STARTED")

    while True:

        for symbol in ["XAU/USD","EUR/USD"]:
            print(f"🔍 Checking: {symbol}")

            try:
                df = await get_data(symbol, "5min")

                if df is None:
                    continue

                price = df["close"].iloc[-1]

                f_price = await get_finnhub_price(symbol)
                if not f_price:
                    continue

                if abs(price - f_price) > price * 0.002:
                    continue

                trend_main = trend(df)
                structure = structure_break(df)

                if trend_main != structure:
                    continue

                high, low = get_smart_zone(df)

                if trend_main == "BUY" and price > (low + 5):
                    continue

                if trend_main == "SELL" and price < (high - 5):
                    continue

                send_to_mt5(symbol, trend_main, LOT)

                print(f"✅ SIGNAL: {symbol} {trend_main}")

            except Exception as e:
                print("❌ LOOP ERROR:", e)

        await asyncio.sleep(60)


# ---------- RUN ----------
asyncio.run(run_bot())
