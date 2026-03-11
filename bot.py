import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = ("8605977902:AAFcABeU2bbnDJenJ0qLgpvBbOceWC3GzsU")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "مرحبا 👋\n\n"
        "إذا بغيت تبدأ التداول بطريقة منظمة،\n"
        "اكتب START في الخاص."
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()

