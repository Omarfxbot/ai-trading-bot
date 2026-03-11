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
        "هنا نعمل بخطة واضحة وإدارة رأس مال صارمة.\n\n"
        "اختر المسار المناسب لك:",
        reply_markup=reply_markup
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "robo":
        keyboard = [[InlineKeyboardButton("✅ سجلت", callback_data="confirmed")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"""🔵 مسار 10$ + بونص 30$

✔️ إيداع 10$
✔️ تستافد من 30$ دعم للتداول
✔️ نوجهك خطوة بخطوة

⚠️ البونص مخصص للتداول فقط.

سجل من هنا:
{ROBO_LINK}
""",
            reply_markup=reply_markup
        )

    elif query.data == "exness":
        keyboard = [[InlineKeyboardButton("✅ سجلت", callback_data="confirmed")]]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await query.edit_message_text(
            f"""🟢 مسار احترافي

✔️ منصة عالمية قوية
✔️ تنفيذ سريع
✔️ سبريد منخفض
✔️ مناسبة لبناء حساب طويل المدى

سجل من هنا:
{EXNESS_LINK}
""",
            reply_markup=reply_markup
        )

    elif query.data == "confirmed":
        await query.edit_message_text(
            f"""🔥 ممتاز!

باش نفعل لك الوصول لقناة VIP الخاصة:

1️⃣ دير الإيداع
2️⃣ صيفط سكرين للإيداع هنا

من بعد المراجعة غادي نضيفك لقناة VIP 🔒

رابط القناة:
{VIP_CHANNEL_LINK}
"""
        )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    app.run_polling()

if __name__ == "__main__":
    main()
