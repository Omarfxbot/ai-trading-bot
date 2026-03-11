import os
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = ("8605977902:AAHFHDzeqPuQJW-WDEC3S7qSjosj1TpP8Mc")


# ========================
# /start
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

    await update.message.reply_text(
        "🔥 مرحبا بك في Omar Swing VIP\n\n"
        "نظام تداول منظم بخطة واضحة وإدارة رأس مال صارمة.\n\n"
        "اختر المسار المناسب لك:",
        reply_markup=reply_markup
    )

    context.user_data["step"] = "choose_platform"


# ========================
# معالجة الأزرار
# ========================

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    step = context.user_data.get("step")

    # ---------------------------------
    # اختيار RoboForex
    # ---------------------------------
    if text == "🚀 ابدأ ب 10$ + بونص 30$" and step == "choose_platform":

        keyboard = [["✅ سجلت"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "🔥 اختيار ممتاز!\n\n"
            "سجل الآن واستفد من بونص 30$:\n"
            "https://my.roboforex.com/en/?a=omawl\n\n"
            "بعد التسجيل اضغط على (سجلت)",
            reply_markup=reply_markup
        )

        context.user_data["step"] = "waiting_registration"
        return

    # ---------------------------------
    # تأكيد التسجيل
    # ---------------------------------
    if text == "✅ سجلت" and step == "waiting_registration":

        await update.message.reply_text(
            "🎉 ممتاز!\n\n"
            "هذا رابط قناة VIP الخاصة:\n"
            "https://t.me/+_woSe4hCzCMzZGE8",
            reply_markup=ReplyKeyboardRemove()
        )

        context.user_data["step"] = "done"
        return

    # ---------------------------------
    # اختيار Exness
    # ---------------------------------
    if text == "🏦 حساب احترافي طويل المدى" and step == "choose_platform":

        await update.message.reply_text(
            "🏦 حساب احترافي طويل المدى\n\n"
            "افتح حسابك عبر الرابط التالي:\n"
            "https://one.exnessonelink.com/a/zi8w32eknv",
            reply_markup=ReplyKeyboardRemove()
        )

        context.user_data["step"] = "done"
        return


# ========================
# تشغيل البوت
# ========================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))

    # فلتر محدد باش ميوقعش double reply
    app.add_handler(
        MessageHandler(
            filters.Regex(
                "^(🚀 ابدأ ب 10\\$ \\+ بونص 30\\$|🏦 حساب احترافي طويل المدى|✅ سجلت)$"
            ),
            handle_buttons
        )
    )

    app.run_polling()


if __name__ == "__main__":
    main()
