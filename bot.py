import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = ("8605977902:AAFcABeU2bbnDJenJ0qLgpvBbOceWC3GzsU")

ROBO_LINK = "https://my.roboforex.com/en/?a=omawl"
EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"
VIP_CHANNEL_LINK = "https://t.me/+_woSe4hCzCMzZGE8"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🚀 أبدأ بـ 10$ + بونص 30$", callback_data="robo")],
        [InlineKeyboardButton("🏦 حساب احترافي طويل المدى", callback_data="exness")]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔥 مرحبا بك في نظام Omar Swing VIP\n\n"
        "اختر المسار المناسب لك:",
        reply_markup=reply_markup
    )

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "robo":
        await query.message.reply_text(
            f"""🔵 مسار 10$ + بونص 30$

سجل من هنا:
{ROBO_LINK}

من بعد دير الإيداع وصيفط ليا سكرين 👇
"""
        )

    elif query.data == "exness":
        await query.message.reply_text(
            f"""🟢 حساب احترافي طويل المدى

سجل من هنا:
{EXNESS_LINK}

من بعد دير الإيداع وصيفط ليا سكرين 👇
"""
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
