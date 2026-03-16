import os
import requests
import pandas as pd
from datetime import datetime
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

VIP_CHANNEL = "@OmarSwingVIP"
EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"

signals_today = 0
MAX_SIGNALS = 4
today_date = None


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

    try:
        news = requests.get(
            "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
            timeout=5
        ).json()

        for event in news:

            if event.get("impact") != "High":
                continue

            event_time = datetime.fromisoformat(
                event["date"].replace("Z", "+00:00")
            ).replace(tzinfo=None)

            diff = (event_time - now).total_seconds()

            if 0 < diff < 1800:
                print("High impact news soon")
                return

    except:
        pass

    symbol = "XAU/USD"

    url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=15min&outputsize=200&apikey={TWELVEDATA_API_KEY}"

    response = requests.get(url).json()

    if "values" not in response:
        return

    df = pd.DataFrame(response["values"])
    df = df.iloc[::-1]

    numeric_cols = ["open", "high", "low", "close"]
    df[numeric_cols] = df[numeric_cols].astype(float)

    df["ema200"] = df["close"].ewm(span=200).mean()

    df["high20"] = df["high"].rolling(20).max()
    df["low20"] = df["low"].rolling(20).min()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    signal = None

    if last["close"] > last["ema200"]:

        if prev["close"] < prev["open"] and last["close"] > last["open"]:
            if abs(last["close"] - last["low20"]) < 2:
                signal = "BUY"

    if last["close"] < last["ema200"]:

        if prev["close"] > prev["open"] and last["close"] < last["open"]:
            if abs(last["close"] - last["high20"]) < 2:
                signal = "SELL"

    if not signal:
        return

    entry = last["close"]

    sl_distance = 10
    tp_distance = 20

    if signal == "BUY":

        sl = entry - sl_distance

        tp1 = entry + tp_distance
        tp2 = entry + tp_distance * 2
        tp3 = entry + tp_distance * 3

    else:

        sl = entry + sl_distance

        tp1 = entry - tp_distance
        tp2 = entry - tp_distance * 2
        tp3 = entry - tp_distance * 3

    text = f"""
📊 XAUUSD – {signal}

Entry: {entry:.2f}
SL: {sl:.2f}

TP1: {tp1:.2f}
TP2: {tp2:.2f}
TP3: {tp3:.2f}

⚡ Quick Copy
XAUUSD {signal} {entry:.2f} SL {sl:.2f} TP {tp1:.2f}
"""

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 تنفيذ الصفقة", url=EXNESS_LINK)]
    ])

    await context.bot.send_message(
        chat_id=VIP_CHANNEL,
        text=text,
        reply_markup=keyboard
    )

    signals_today += 1

    print("Signal sent", signal)


async def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.job_queue.run_repeating(
        check_signal,
        interval=900,
        first=10
    )

    print("Gold Pro Bot Started")

    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
