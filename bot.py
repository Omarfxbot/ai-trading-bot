import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = ("8605977902:AAFcABeU2bbnDJenJ0qLgpvBbOceWC3GzsU")

ROBO_LINK = "https://my.roboforex.com/en/?a=omawl"
EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔵 RoboForex + بونص 30$", callback_data="robo")],
        [InlineKeyboardButton("🟢 Exness منصة احترافية", callback_data="exness")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔥 اختر المنصة التي تريد البدء بها:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "robo":
        await query.edit_message_text(
            f"""🔵 RoboForex

✅ إيداع فقط 10$
🎁 بونص 30$ إضافي للتداول

⚠️ البونص مخصص للتداول وليس للسحب المباشر.

🚀 سجل من هنا:
{ROBO_LINK}
"""
        )

    elif query.data == "exness":
        await query.edit_message_text(
            f"""🟢 Exness

🌍 منصة عالمية احترافية
⚡ تنفيذ سريع + سبريد منخفض

🚀 سجل من هنا:
{EXNESS_LINK}
"""
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
