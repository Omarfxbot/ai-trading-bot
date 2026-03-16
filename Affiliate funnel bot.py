import os
import psycopg2

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"
ROBO_LINK = "https://my.roboforex.com/en/?a=omawl"

SIGNAL_CHANNEL = "https://t.me/OmarFXSignal"


# -------- DATABASE --------

conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS signals (
id SERIAL PRIMARY KEY,
symbol TEXT,
direction TEXT,
result TEXT,
profit FLOAT,
created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()


# -------- START COMMAND --------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [KeyboardButton("🔥 منصة احترافية Exness")],
        [KeyboardButton("🎁 ابدأ ب 10$ + Bonus 30$ RoboForex")],
        [KeyboardButton("✅ سجلت بالفعل")]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    text = """
مرحبا 👋

باش تستافد من إشارات الذهب خاصك تسجل فواحدة من المنصات 👇
"""

    await update.message.reply_text(text, reply_markup=reply_markup)


# -------- MESSAGE HANDLER --------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if "Exness" in text:

        await update.message.reply_text(
            f"""
🔥 اختيار احترافي.

سجل من هنا 👇
{EXNESS_LINK}

من بعد التسجيل رجع واضغط:
✅ سجلت بالفعل
"""
        )

    elif "RoboForex" in text:

        await update.message.reply_text(
            f"""
🎁 تبدأ ب 10$ فقط

ومع التوثيق تحصل على Bonus 30$

سجل من هنا 👇
{ROBO_LINK}

من بعد التسجيل رجع واضغط:
✅ سجلت بالفعل
"""
        )

    elif "سجلت بالفعل" in text:

        await update.message.reply_text(
            f"""
ممتاز 🔥

ادخل لقناة الإشارات من هنا 👇

{SIGNAL_CHANNEL}

⚠️ دير Stop Loss دائما
"""
        )


# -------- DASHBOARD --------

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cur.execute("SELECT COUNT(*) FROM signals")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM signals WHERE result='WIN'")
    wins = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM signals WHERE result='LOSS'")
    loss = cur.fetchone()[0]

    winrate = 0
    if total > 0:
        winrate = round((wins / total) * 100, 2)

    cur.execute("SELECT COALESCE(SUM(profit),0) FROM signals")
    profit = cur.fetchone()[0]

    text = f"""
📊 AI GOLD BOT DASHBOARD

Signals: {total}
Wins: {wins}
Loss: {loss}

Winrate: {winrate} %

Profit: {profit} $

Status: Running
"""

    await update.message.reply_text(text)


# -------- BOT START --------

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("dashboard", dashboard))
app.add_handler(MessageHandler(filters.TEXT, handle_message))

print("Affiliate Funnel Bot Running")
app.run_polling(drop_pending_updates=True)

