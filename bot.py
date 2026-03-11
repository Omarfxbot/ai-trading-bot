import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("8605977902:AAHFHDzeqPuQJW-WDEC3S7qSjosj1TpP8Mc")

ROBO_LINK = "https://my.roboforex.com/en/?a=omawl"
EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"
VIP_LINK = "https://t.me/+_woSe4hCzCMzZGE8"


# ========================
# START
# ========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        ["🚀 ابدأ ب 10$ + بونص 30$"],
        ["🏦 حساب احترافي طويل المدى"]
    ]

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    context.user_data.clear()

    await update.message.reply_text(
        "🔥 مرحبا بك في Omar Swing VIP\n\n"
        "اختر المسار المناسب لك:",
        reply_markup=reply_markup
    )

    context.user_data["step"] = "choose_platform"


# ========================
# HANDLER
# ========================
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text
    step = context.user_data.get("step")

    # ---- ROBOFOREX ----
    if text == "🚀 ابدأ ب 10$ + بونص 30$" and step == "choose_platform":

        keyboard = [["✅ سجلت"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "🔥 اختيار ممتاز!\n\n"
            "سجل الآن واستفد من بونص 30$:\n"
            f"{ROBO_LINK}\n\n"
            "بعد التسجيل اضغط على (سجلت)",
            reply_markup=reply_markup
        )

        context.user_data["step"] = "waiting_confirmation"
        return

    # ---- EXNESS ----
    if text == "🏦 حساب احترافي طويل المدى" and step == "choose_platform":

        keyboard = [["✅ فتحت الحساب"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "🏦 حساب احترافي طويل المدى\n\n"
            "افتح حسابك عبر الرابط التالي:\n"
            f"{EXNESS_LINK}\n\n"
            "بعد فتح الحساب اضغط (فتحت الحساب)",
            reply_markup=reply_markup
        )

        context.user_data["step"] = "waiting_confirmation_exness"
        return

    # ---- CONFIRM ROBO ----
    if text == "✅ سجلت" and step == "waiting_confirmation":

        await update.message.reply_text(
            "🎉 ممتاز!\n\n"
            "هذا رابط قناة VIP الخاصة:\n"
            f"{VIP_LINK}",
            reply_markup=ReplyKeyboardRemove()
        )

        context.user_data["step"] = "done"
        return

    # ---- CONFIRM EXNESS ----
    if text == "✅ فتحت الحساب" and step == "waiting_confirmation_exness":

        await update.message.reply_text(
            "🎉 رائع!\n\n"
            "هذا رابط قناة VIP الخاصة:\n"
            f"{VIP_LINK}",
            reply_markup=ReplyKeyboardRemove()
        )

        context.user_data["step"] = "done"
        return


# ========================
# MAIN
# ========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_buttons))

    app.run_polling()


if __name__ == "__main__":
    main()
