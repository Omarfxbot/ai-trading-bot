import os
import httpx
import pandas as pd
from datetime import datetime
import MetaTrader5 as mt5

# ---------- API ----------
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY")

# ---------- MT5 LOGIN ----------
mt5.initialize()
mt5.login(262411967, password="Audio@2204", server="Exness-MT5Trial16")

# ---------- SETTINGS ----------
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

# ---------- EXECUTION ----------
def execute_trade(symbol, direction, lot, sl, tp):

    symbol_mt5 = symbol.replace("/", "") + "m"
    mt5.symbol_select(symbol_mt5, True)

    tick = mt5.symbol_info_tick(symbol_mt5)
    price = tick.ask if direction == "BUY" else tick.bid

    request = {
        "action": mt5.TRADE_ACTION_DEAL,
        "symbol": symbol_mt5,
        "volume": lot,
        "type": mt5.ORDER_TYPE_BUY if direction=="BUY" else mt5.ORDER_TYPE_SELL,
        "price": price,
        "sl": sl,
        "tp": tp,
        "deviation": 10,
        "magic": 123456,
        "comment": "AI AUTO BOT",
    }

    mt5.order_send(request)

# ---------- ENGINE ----------
import asyncio

async def run_bot():

    print("🚀 AI BOT MT5 STARTED")

    while True:

        for symbol in ["XAU/USD","EUR/USD"]:

            try:
                df = await get_data(symbol, "5min")
                price = df["close"].iloc[-1]

                f_price = await get_finnhub_price(symbol)
                if not f_price:
                    continue

                if abs(price - f_price) > price * 0.002:
                    continue

                t = trend(df)

                # ---------- SL / TP ----------
                if t == "BUY":
                    sl = price - 5
                    tp = price + 10
                else:
                    sl = price + 5
                    tp = price - 10

                # ---------- EXECUTE ----------
                execute_trade(symbol, t, LOT, sl, tp)

                print(f"✅ Trade executed: {symbol} {t}")

            except Exception as e:
                print("ERROR:", e)

        await asyncio.sleep(60)

# ---------- RUN ----------
asyncio.run(run_bot())
