
import os
import psycopg2
import requests
import pandas as pd
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================= CONFIG =================

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.environ.get("DATABASE_URL")

ROBO_LINK = "https://my.roboforex.com/en/?a=omawl"
EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"

ROBO_GUIDE = "https://t.me/+68YvPcWphtE3ZGM0"
EXNESS_GUIDE = "https://t.me/+z5iRMblllboxYWNk"

VIP_CHANNEL = "@OmarSwingVIP"
VIP_LINK = "https://t.me/OmarSwingVIP"

TWELVEDATA_API_KEY = os.getenv("TWELVEDATA_API_KEY")

# ================= DATABASE =================

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS stats (
    platform TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS daily_signals (
    id SERIAL PRIMARY KEY,
    symbol TEXT,
    direction TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
""")

cur.execute("""
CREATE INDEX IF NOT EXISTS idx_signal_symbol_direction
ON daily_signals(symbol, direction);
""")

conn.commit()

cur.execute("INSERT INTO stats (platform) VALUES ('robo') ON CONFLICT DO NOTHING;")
cur.execute("INSERT INTO stats (platform) VALUES ('exness') ON CONFLICT DO NOTHING;")
conn.commit()

# ================= START =================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🚀 RoboForex 10$ + 30$ Bonus", callback_data="robo")],
        [InlineKeyboardButton("🏦 Exness حساب احترافي", callback_data="exness")]
    ]

    await update.message.reply_text(
        "اختر المنصة المناسبة:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ================= BUTTON HANDLER =================

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):

    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id
    data = query.data

    if data in ["robo", "exness"]:

        context.user_data["platform"] = data
        link = ROBO_LINK if data == "robo" else EXNESS_LINK

        keyboard = [
            [InlineKeyboardButton("🎥 مساعدة في التسجيل", callback_data="help")],
            [InlineKeyboardButton("✅ تأكيد التسجيل", callback_data="confirm")]
        ]

        await query.edit_message_text(
            f"سجل عبر الرابط التالي:\n\n{link}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "help":

        platform = context.user_data.get("platform")
        guide_link = ROBO_GUIDE if platform == "robo" else EXNESS_GUIDE

        keyboard = [
            [InlineKeyboardButton("🎥 مشاهدة فيديو الشرح", url=guide_link)],
            [InlineKeyboardButton("⬅️ رجوع", callback_data=f"back_{platform}")]
        ]

        await query.edit_message_text(
            "شاهد الفيديو ثم أكمل التسجيل.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data.startswith("back_"):

        platform = data.split("_")[1]
        context.user_data["platform"] = platform
        link = ROBO_LINK if platform == "robo" else EXNESS_LINK

        keyboard = [
            [InlineKeyboardButton("🎥 مساعدة في التسجيل", callback_data="help")],
            [InlineKeyboardButton("✅ تأكيد التسجيل", callback_data="confirm")]
        ]

        await query.edit_message_text(
            f"سجل عبر الرابط التالي:\n\n{link}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "confirm":

        try:
            member = await context.bot.get_chat_member(VIP_CHANNEL, user_id)

            if member.status in ["member", "administrator", "creator"]:

                platform = context.user_data.get("platform")
                if platform:
                    cur.execute(
                        "UPDATE stats SET count = count + 1 WHERE platform = %s;",
                        (platform,)
                    )
                    conn.commit()

                keyboard = [
                    [InlineKeyboardButton("🚀 دخول قناة VIP", url=VIP_LINK)]
                ]

                await query.edit_message_text(
                    "🎉 تم التحقق! مرحبا بك في VIP 🚀",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

            else:
                raise Exception()

        except:

            keyboard = [
                [InlineKeyboardButton("🔓 انضم لقناة VIP", url=VIP_LINK)],
                [InlineKeyboardButton("✅ تحققت", callback_data="confirm")]
            ]

            await query.edit_message_text(
                "يجب الانضمام لقناة VIP أولاً.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

# ================= AUTO SIGNAL =================

async def check_signal(context: ContextTypes.DEFAULT_TYPE):

    symbols = ["XAU/USD", "EUR/USD", "BTC/USD"]

    now = datetime.utcnow()
    hour = now.hour

    if False:
        print("Outside trading sessions")
        return
# ===== News Filter =====
try:
    news_response = requests.get(
        "https://nfs.faireconomy.media/ff_calendar_thisweek.json",
        timeout=5
    )

    if news_response.status_code == 200:
        news = news_response.json()

        for event in news:
            if event.get("impact") != "High":
                continue

            event_time = datetime.fromisoformat(
                event["date"].replace("Z", "+00:00")
            ).replace(tzinfo=None)

            diff = (event_time - now).total_seconds()

            # إذا كان الخبر خلال 30 دقيقة
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
                print("API error:", symbol)
                continue

            df = pd.DataFrame(response["values"])
            df = df.iloc[::-1]

            numeric_cols = ["open","high","low","close"]
            df[numeric_cols] = df[numeric_cols].astype(float)

            df["ema50"] = df["close"].ewm(span=50).mean()
            df["ema200"] = df["close"].ewm(span=200).mean()

            last = df.iloc[-1]
            prev = df.iloc[-2]

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
    f"📊 {pair} – {signal}\n\n"
    f"Entry: {entry:.5f}\n"
    f"SL: {sl:.5f}\n"
    f"TP: {tp:.5f}\n\n"
    f"⚡ Quick Copy:\n"
    f"`{pair} {signal} {entry:.5f} SL {sl:.5f} TP {tp:.5f}`"
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
                (symbol,signal)
            )

            conn.commit()

            print("Signal sent:",symbol,signal)

        except Exception as e:

            print("Error processing",symbol,e)
            conn.rollback()
            continue

# ================= MAIN =================

def main():
    import time

    while True:

        try:

            print("Bot starting...")

            app = ApplicationBuilder().token(BOT_TOKEN).build()

            app.add_handler(CommandHandler("start",start))
            app.add_handler(CallbackQueryHandler(button_handler))

            if app.job_queue:
                app.job_queue.run_repeating(check_signal,interval=900,first=10)

            app.run_polling(drop_pending_updates=True)

        except Exception as e:

            print("Bot crashed:",e)
            time.sleep(5)

if __name__ == "__main__":
    main()

