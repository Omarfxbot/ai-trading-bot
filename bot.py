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
print("DATABASE_URL =", DATABASE_URL)
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
    date DATE PRIMARY KEY,
    sent BOOLEAN DEFAULT FALSE
);
""")

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
    print("=== CHECK SIGNAL START ===")

    today = datetime.utcnow().date()
    print("Today:", today)

    cur.execute("SELECT sent FROM daily_signals WHERE date = %s;", (today,))
    row = cur.fetchone()

    if row:
        print("Signal already sent today")
        return

    url = f"https://api.twelvedata.com/time_series?symbol=XAU/USD&interval=15min&outputsize=200&apikey={TWELVEDATA_API_KEY}"
    response = requests.get(url).json()

    if "values" not in response:
        print("API response invalid:", response)
        return

    print("API response received")

    df = pd.DataFrame(response["values"])
    df = df.iloc[::-1]

    numeric_cols = ["open", "high", "low", "close", "volume"]
    df[numeric_cols] = df[numeric_cols].astype(float)

    df["ema50"] = df["close"].ewm(span=50).mean()
    df["ema200"] = df["close"].ewm(span=200).mean()

    last = df.iloc[-1]

    print("Last Close:", last["close"])
    print("EMA50:", last["ema50"])
    print("EMA200:", last["ema200"])

    signal = None

    if last["ema50"] > last["ema200"] and last["close"] > last["ema200"]:
        signal = "BUY"
    elif last["ema50"] < last["ema200"] and last["close"] < last["ema200"]:
        signal = "SELL"

    if not signal:
        print("No valid setup found")
        return

    print("Signal detected:", signal)

    entry = last["close"]
    sl = entry - 5 if signal == "BUY" else entry + 5
    tp = entry + 10 if signal == "BUY" else entry - 10

    text = (
        f"📊 XAUUSD – {signal}\n"
        f"Entry: {entry:.2f}\n"
        f"SL: {sl:.2f}\n"
        f"TP: {tp:.2f}\n\n"
        "⚠️ التداول ينطوي على مخاطر"
    )

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔥 تنفيذ الصفقة", url=EXNESS_LINK)]
    ])

    await context.bot.send_message(
        chat_id=VIP_CHANNEL,
        text=text,
        reply_markup=keyboard
    )

    cur.execute("INSERT INTO daily_signals (date, sent) VALUES (%s, TRUE);", (today,))
    conn.commit()

    print("Signal sent successfully")
# ================= MAIN =================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers ديما خاصهم يتسجلو
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # JobQueue غير إلا كانت متوفرة
    if app.job_queue:
        app.job_queue.run_repeating(check_signal, interval=900, first=10)
    else:
        print("JobQueue not available")

    app.run_polling()

if __name__ == "__main__":
    main()











