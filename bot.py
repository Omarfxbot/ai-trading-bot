import os
from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = ("8605977902:AAFcABeU2bbnDJenJ0qLgpvBbOceWC3GzsU")

ROBO_LINK = "https://my.roboforex.com/en/?a=omawl"
EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv"
VIP_CHANNEL = "https://t.me/+_woSe4hCzCMzZGE8"


# ===== START =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    keyboard = [
        [InlineKeyboardButton("🚀 ابدأ ب $10 + بونص $30", callback_data="robo")],
        [InlineKeyboardButton("🏦 حساب احترافي طويل المدى", callback_data="exness")],
    ]

    await update.message.reply_text(
        "🔥 مرحبا بك في Omar Swing VIP\n\n"
        "نظام تداول منظم بخطة واضحة وإدارة رأس مال صارمة.\n\n"
        "اختر المسار المناسب لك:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ===== HANDLE BUTTONS =====
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "robo":
        keyboard = [
            [InlineKeyboardButton("📌 سجل الآن عبر RoboForex", url=ROBO_LINK)],
            [InlineKeyboardButton("✅ تم التسجيل", callback_data="done")],
        ]

        await query.edit_message_text(
            "🔥 اختيار ممتاز!\n\n"
            "سجل الآن واستفد من بونص 30$.\n\n"
            "بعد التسجيل اضغط على 'تم التسجيل'.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data == "exness":
        keyboard = [
            [InlineKeyboardButton("📌 افتح حساب Exness", url=EXNESS_LINK)],
            [InlineKeyboardButton("✅ تم التسجيل", callback_data="done")],
        ]

        await query.edit_message_text(
            "🏦 حساب احترافي طويل المدى\n\n"
            "افتح حسابك عبر الرابط التالي.\n\n"
            "بعد التسجيل اضغط على 'تم التسجيل'.",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    elif query.data == "done":
        keyboard = [
            [InlineKeyboardButton("🔐 دخول القناة VIP", url=VIP_CHANNEL)]
        ]

        await query.edit_message_text(
            "🎯 ممتاز!\n\n"
            "الآن يمكنك الدخول إلى القناة الخاصة:\n\n"
            "اضغط الزر أسفل 👇",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )


# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))

    print("Bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()
