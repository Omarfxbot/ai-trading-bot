import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

BOT_TOKEN = ("8605977902:AAFcABeU2bbnDJenJ0qLgpvBbOceWC3GzsU")

ROBO_LINK = "https://my.roboforex.com/en/?a=omawl"
EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🔵 RoboForex + بونص 30$", url=ROBO_LINK)],
        [InlineKeyboardButton("🟢 Exness منصة احترافية", url=EXNESS_LINK)]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🔥 اختر المنصة التي تريد البدء بها:",
        reply_markup=reply_markup
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
