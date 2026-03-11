import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

BOT_TOKEN = ("8605977902:AAFcABeU2bbnDJenJ0qLgpvBbOceWC3GzsU")

# ====== START COMMAND ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🚀 ابدأ ب 10$ + بونص 30$"],
        ["🏦 حساب احترافي طويل المدى"]
    ]

    from telegram import ReplyKeyboardMarkup
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🔥 مرحبا بك في Omar Swing VIP\n\n"
        "اختر المسار المناسب لك:",
        reply_markup=reply_markup
    )

# ====== BUTTON HANDLER ======
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "10$" in text:
        await update.message.reply_text(
            "🔥 اختيار ممتاز!\n\n"
            "سجل الآن واستفد من بونص 30$:\n"
            "https://my.roboforex.com/en/?a=omawl"
        )

    elif "احترافي" in text:
        await update.message.reply_text(
            "🏦 حساب احترافي طويل المدى\n\n"
            "افتح حسابك عبر الرابط التالي:\n"
            "https://one.exnessonelink.com/a/zi8w32eknv"
        )

# ====== MAIN ======
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    app.run_polling()

if __name__ == "__main__":
    main()
