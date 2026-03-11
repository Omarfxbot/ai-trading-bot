import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

BOT_TOKEN = ("8605977902:AAFcABeU2bbnDJenJ0qLgpvBbOceWC3GzsU")

# زر البداية
keyboard = [["🚀 ابدأ الآن"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 مرحبا بك\n\nاضغط على الزر باش نبدأو:",
        reply_markup=reply_markup
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🚀 ابدأ الآن":
        await update.message.reply_text(
            "🔥 ممتاز!\n\nرابط الدخول للبوت:\nhttps://t.me/OmarFX_helper_bot"
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == "__main__":
    main()

