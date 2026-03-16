
import os
import psycopg2
import requests
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"

VIP_CHANNEL = "@OmarSwingVIP"

TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS daily_signals (
    id SERIAL PRIMARY KEY,
    symbol TEXT,
    direction TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

conn.commit()

def trading_session():
    now = datetime.utcnow()
    hour = now.hour

    if 7 <= hour <= 22:
        return True
    else:
        return False

async def check_signal(context: ContextTypes.DEFAULT_TYPE):

    if not trading_session():
        print("Outside London/NY session")
        return

    symbols = ["XAU/USD", "EUR/USD", "BTC/USD"]

    now = datetime.utcnow()

    # -------- NEWS FILTER --------
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

    except Exception as e:
        print("News filter error:", e)

    for symbol in symbols:

        try:

            print("Checking:", symbol)

            url = f"https://api.twelvedata.com/time_series?symbol={symbol}&interval=15min&outputsize=200&apikey={TWELVEDATA_API_KEY}"

            response = requests.get(url).json()

            if "values" not in response:
                print("API error")
                continue

            df = pd.DataFrame(response["values"])
            df = df.iloc[::-1]

            numeric_cols = ["open","high","low","close"]
            df[numeric_cols] = df[numeric_cols].astype(float)

            # EMA
            df["ema50"] = df["close"].ewm(span=50).mean()
            df["ema200"] = df["close"].ewm(span=200).mean()

            # ATR
            df["prev_close"] = df["close"].shift(1)
            df["tr1"] = df["high"] - df["low"]
            df["tr2"] = (df["high"] - df["prev_close"]).abs()
            df["tr3"] = (df["low"] - df["prev_close"]).abs()

            df["tr"] = df[["tr1","tr2","tr3"]].max(axis=1)
            df["atr"] = df["tr"].rolling(14).mean()

            last = df.iloc[-1]
            prev = df.iloc[-2]

            # Candle strength filter
            candle_size = abs(last["close"] - last["open"])
            if candle_size < last["atr"] * 0.3:
                print("Weak candle:", symbol)
                continue

            signal = None

            if last["ema50"] > last["ema200"] and last["close"] > prev["high"]:
                signal = "BUY"

            elif last["ema50"] < last["ema200"] and last["close"] < prev["low"]:
                signal = "SELL"

            if not signal:
                continue

            cur.execute(
                "SELECT created_at FROM daily_signals WHERE direction=%s AND symbol=%s ORDER BY created_at DESC LIMIT 1",
                (signal, symbol)
            )

            last_signal = cur.fetchone()

            if last_signal:
                diff = (datetime.utcnow() - last_signal[0]).total_seconds()
                if diff < 3600:
                    print("Duplicate signal skipped:", symbol)
                    continue

            entry = last["close"]

            atr_val = last["atr"]

            sl_distance = atr_val * 1.2
            tp_distance = sl_distance * 2

            if signal == "BUY":
                sl = entry - sl_distance
                tp = entry + tp_distance
            else:
                sl = entry + sl_distance
                tp = entry - tp_distance

            pair = symbol.replace("/","")

            text = (
    f"📊 {pair} – {signal} (MARKET)\n\n"
    f"Current Price: {entry:.5f}\n"
    f"SL: {sl:.5f}\n"
    f"TP: {tp:.5f}\n\n"
    f"⚡ Quick Copy:\n"
    f"`{pair} {signal} SL {sl:.5f} TP {tp:.5f}`"
)

            keyboard = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔥 تنفيذ الصفقة", url=EXNESS_LINK)]
            ])

            await context.bot.send_message(
                chat_id=VIP_CHANNEL,
                text=text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )

            cur.execute(
                "INSERT INTO daily_signals(symbol, direction) VALUES(%s,%s)",
                (symbol, signal)
            )

            conn.commit()

            print("Signal sent:", symbol, signal)

        except Exception as e:
            print("Error processing", symbol, e)
            conn.rollback()
            continue


def main():

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.job_queue.run_repeating(check_signal, interval=900, first=10)

    print("Bot starting...")

    app.run_polling()


if __name__ == "__main__":
    main()

