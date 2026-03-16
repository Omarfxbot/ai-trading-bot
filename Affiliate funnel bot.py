import os
import psycopg2
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

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

async def dashboard(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cur.execute("SELECT COUNT(*) FROM signals")
    total = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM signals WHERE result='WIN'")
    wins = cur.fetchone()[0]

    cur.execute("SELECT COUNT(*) FROM signals WHERE result='LOSS'")
    loss = cur.fetchone()[0]

    winrate = 0
    if total > 0:
        winrate = round((wins / total) * 100,2)

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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("AI GOLD BOT Dashboard Ready")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("dashboard", dashboard))

print("Dashboard Bot Running")

app.run_polling()
