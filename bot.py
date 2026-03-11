import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

BOT_TOKEN = ("8605977902:AAHFHDzeqPuQJW-WDEC3S7qSjosj1TpP8Mc")


# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        ["🚀 ابدأ ب 10$ + بونص 30$"],
        ["🏦 حساب احترافي طويل المدى"]
    ]

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        "🔥 مرحبا بك في Omar Swing VIP\n\n"
        "اختر المسار المناسب لك:",
        reply_markup=reply_markup
    )

# ========= HANDLER =========
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # ===== RoboForex =====
    if "10$" in text:
        keyboard = [["✅ سجلت"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "🔥 اختيار ممتاز!\n\n"
            "سجل الآن واستفد من بونص 30$:\n"
            "https://my.roboforex.com/en/?a=omawl\n\n"
            "بعد التسجيل اضغط على (سجلت)",
            reply_markup=reply_markup
        )

    # ===== Exness =====
    elif "احترافي" in text:
        keyboard = [["✅ فتحت الحساب"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "🏦 حساب احترافي طويل المدى\n\n"
            "افتح حسابك عبر الرابط التالي:\n"
            "https://one.exnessonelink.com/a/zi8w32eknv\n\n"
            "بعد فتح الحساب اضغط (فتحت الحساب)",
            reply_markup=reply_markup
        )

    # ===== CONFIRM ROBO =====
    elif "سجلت" in text:
        await update.message.reply_text(
            "🎉 ممتاز!\n\n"
            "هذا رابط قناة VIP الخاصة:\n"
            "https://t.me/+_woSe4hCzCMzZGE8",
            reply_markup=ReplyKeyboardRemove()
        )

    # ===== CONFIRM EXNESS =====
    elif "فتحت الحساب" in text:
        await update.message.reply_text(
            "🎉 رائع!\n\n"
            "هذا رابط قناة VIP الخاصة:\n"
            "https://t.me/+_woSe4hCzCMzZGE8",
            reply_markup=ReplyKeyboardRemove()
        )

# ========= MAIN =========
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    app.run_polling()

if __name__ == "__main__":
    main()

