import os
import psycopg2
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# ================= CONFIG =================

BOT_TOKEN = "8605977902:AAHFHDzeqPuQJW-WDEC3S7qSjosj1TpP8Mc"
DATABASE_URL = ("postgresql://postgres:IcdudqSekkFoJgLltsAHtekmWKPZFQdM@turntable.proxy.rlwy.net:26146/railway")

ROBO_LINK = "https://my.roboforex.com/en/?a=omawl"
EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"

ROBO_GUIDE = "https://t.me/+68YvPcWphtE3ZGM0"
EXNESS_GUIDE = "https://t.me/+z5iRMblllboxYWNk"

VIP_CHANNEL = "@OmarSwingVIP"
VIP_LINK = "https://t.me/OmarSwingVIP"

# ================= DATABASE =================

conn = psycopg2.connect(DATABASE_URL)
cur = conn.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS stats (
    platform TEXT PRIMARY KEY,
    count INTEGER DEFAULT 0
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

    # ===== اختيار المنصة =====
    if data in ["robo", "exness"]:

        context.user_data["platform"] = data

        link = ROBO_LINK if data == "robo" else EXNESS_LINK

        keyboard = [
            [InlineKeyboardButton("🎥 مساعدة في التسجيل", callback_data="help")],
            [InlineKeyboardButton("✅ تأكيد التسجيل", callback_data="confirm")]
        ]

        await query.edit_message_text(
            f"سجل عبر الرابط التالي:\n\n{link}\n\n"
            "إذا لم تعرف طريقة التسجيل اضغط على مساعدة.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ===== زر المساعدة =====
    elif data == "help":

        platform = context.user_data.get("platform")

        if platform == "robo":
            guide_link = ROBO_GUIDE
            platform_name = "RoboForex"
        else:
            guide_link = EXNESS_GUIDE
            platform_name = "Exness"

        keyboard = [
            [InlineKeyboardButton("🎥 مشاهدة فيديو الشرح", url=guide_link)],
            [InlineKeyboardButton("⬅️ رجوع", callback_data=platform)]
        ]

        await query.edit_message_text(
            f"📌 شرح التسجيل في {platform_name}:\n\n"
            "شاهد الفيديو ثم عد وأكمل التسجيل.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ===== تأكيد التسجيل =====
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
                    "🎉 تم التحقق بنجاح!\n\n"
                    "مرحبا بك في VIP 🚀",
                    reply_markup=InlineKeyboardMarkup(keyboard)
                )

            else:
                raise Exception("Not member")

        except:

            keyboard = [
                [InlineKeyboardButton("🔓 انضم لقناة VIP", url=VIP_LINK)],
                [InlineKeyboardButton("✅ تحققت", callback_data="confirm")]
            ]

            await query.edit_message_text(
                "❌ يجب الانضمام لقناة VIP أولاً ثم اضغط تحققت.",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )

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
