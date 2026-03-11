import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# خليه ياخذ التوكن من Environment Variables
BOT_TOKEN = ("8605977902:AAFcABeU2bbnDJenJ0qLgpvBbOceWC3GzsU")

# روابط الإحالة
ROBO_LINK = "https://my.roboforex.com/en/?a=omawl"
EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"


# رسالة /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🚀 ابدأ ب $10 + بونص $30"],
        ["🏦 حساب احترافي طويل المدى"],
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    await update.message.reply_text(
        "🔥 مرحبا بك في نظام Omar Swing VIP\n\n"
        "نظام تداول منظم بخطة واضحة وإدارة رأس مال صارمة.\n\n"
        "اختر المسار المناسب لك:",
        reply_markup=reply_markup,
    )


# معالجة ضغط الأزرار
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if "بونص" in text:
        await update.message.reply_text(
            "🔥 اختيار ممتاز!\n\n"
            "سجل الآن واستفد من بونص 30$:\n\n"
            f"{ROBO_LINK}"
        )

    elif "احترافي" in text:
        await update.message.reply_text(
            "🏦 حساب احترافي طويل المدى\n\n"
            "افتح حسابك عبر الرابط التالي:\n\n"
            f"{EXNESS_LINK}"
        )


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
