import os
import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

DATABASE_URL = ("postgresql://postgres:IcdudqSekkFoJgLltsAHtekmWKPZFQdM@turntable.proxy.rlwy.net:26146/railway")

ROBO_LINK = "https://my.roboforex.com/en/?a=omawl"
EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"
VIP_CHANNEL = "@YOUR_VIP_CHANNEL_USERNAME"

# ===== DATABASE CONNECTION =====
conn = psycopg2.connect(DATABASE_URL, sslmode="require")
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    referrer BIGINT
);
""")

cur.execute("""
CREATE TABLE IF NOT EXISTS stats (
    platform TEXT PRIMARY KEY,
    count INTEGER
);
""")

cur.execute("INSERT INTO stats (platform, count) VALUES ('robo', 0) ON CONFLICT DO NOTHING;")
cur.execute("INSERT INTO stats (platform, count) VALUES ('exness', 0) ON CONFLICT DO NOTHING;")

conn.commit()


# ================= START =================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id
    args = context.args

    referrer = None
    if args:
        try:
            referrer = int(args[0])
            if referrer == user_id:
                referrer = None
        except:
            pass

    cur.execute("INSERT INTO users (user_id, referrer) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (user_id, referrer))
    conn.commit()

    keyboard = [
        [InlineKeyboardButton("🚀 RoboForex", callback_data="robo")],
        [InlineKeyboardButton("🏦 Exness", callback_data="exness")]
    ]

    await update.message.reply_text(
        "اختر المنصة:",
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
            [InlineKeyboardButton("✅ تأكيد التسجيل", callback_data="confirm")]
        ]

        await query.edit_message_text(
            f"سجل عبر الرابط:\n{link}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif data == "confirm":

        member = await context.bot.get_chat_member(VIP_CHANNEL, user_id)

        if member.status not in ["member", "administrator", "creator"]:
            await query.edit_message_text("يجب الانضمام لقناة VIP أولاً.")
            return

        platform = context.user_data.get("platform")

        cur.execute("UPDATE stats SET count = count + 1 WHERE platform = %s;", (platform,))
        conn.commit()

        await query.edit_message_text("تم التحقق بنجاح 🎉 مرحباً بك في VIP")


# ================= STATS =================
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):

    cur.execute("SELECT platform, count FROM stats;")
    rows = cur.fetchall()

    text = "📊 الإحصائيات:\n\n"
    for row in rows:
        text += f"{row[0]}: {row[1]}\n"

    await update.message.reply_text(text)


# ================= MAIN =================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stats", show_stats))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()


if __name__ == "__main__":
    main()


