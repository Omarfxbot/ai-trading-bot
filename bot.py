import asyncio
import csv
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from aiogram.contrib.fsm_storage.memory import MemoryStorage


BOT_TOKEN = "8605977902:AAFcABeU2bbnDJenJ0qLgpvBbOceWC3GzsU"

EXNESS_LINK = "https://one.exnessonelink.com/a/zi8w32eknv?platform=mobile"
ROBOFOREX_LINK = "https://my.roboforex.com/en/?a=omawl"

ACTIVATION_CHANNEL = "https://t.me/OmarFXStart"
SIGNAL_CHANNEL = "https://t.me/OmarFXSignal"

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

CSV_FILE = "system_data.csv"


# ================= Tracking =================

def save_event(user_id, username, event, extra=""):
    file_exists = os.path.isfile(CSV_FILE)

    with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)

        if not file_exists:
            writer.writerow(["timestamp", "user_id", "username", "event", "extra"])

        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            user_id,
            username,
            event,
            extra
        ])


# ================= Keyboards =================

platform_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🎁 أبدأ بـ 10$ + Bonus 30$")],
        [KeyboardButton(text="🔥 منصة احترافية (Exness)")],
    ],
    resize_keyboard=True
)

confirm_keyboard = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="✅ سجلت و بغيت نبدأ صح")]],
    resize_keyboard=True
)


# ================= START =================

@dp.message_handler(commands=['start'])
async def start(message: types.Message):

    save_event(message.from_user.id, message.from_user.username, "start")

    await message.answer(
        "مرحبا 👋\n\nاختار الطريقة اللي بغيتي تبدا بها 👇",
        reply_markup=platform_keyboard
    )


# ================= MAIN HANDLER =================

@dp.message()
async def main_handler(message: types.Message):

    text = message.text

    # ===== RoboForex =====
    if text == "🎁 أبدأ بـ 10$ + Bonus 30$":

        save_event(message.from_user.id, message.from_user.username, "choose", "roboforex")

        await message.answer(
            "🔥 تبدأ بـ 10$ فقط\n"
            "ومع التوثيق تستافد من 30$ Bonus.\n\n"
            "⚠️ البونوس مخصص للتداول وما كيتسحبش مباشرة."
        )

        await message.answer(f"👇 سجل من هنا\n{ROBOFOREX_LINK}")

        await message.answer(
            "📺 دابا دخل لقناة الشرح وشوف الفيديو كامل 👇\n"
            f"{ACTIVATION_CHANNEL}\n\n"
            "منين تكمل التوثيق + الإيداع رجع للبوت واضغط 👇",
            reply_markup=confirm_keyboard
        )

    # ===== Exness =====
    elif text == "🔥 منصة احترافية (Exness)":

        save_event(message.from_user.id, message.from_user.username, "choose", "exness")

        await message.answer(
            "🔥 اختيار احترافي.\n"
            "منصة قوية للناس اللي ناويين يخدمو بجدية."
        )

        await message.answer(f"👇 سجل من هنا\n{EXNESS_LINK}")

        await message.answer(
            "منين تكمل التسجيل رجع واضغط 👇",
            reply_markup=confirm_keyboard
        )

    # ===== Activation Button =====
    elif text == "✅ سجلت و بغيت نبدأ صح":

        save_event(message.from_user.id, message.from_user.username, "confirmed")

        try:
            await message.delete()
        except:
            pass

        await message.answer(
            "ممتاز 🔥\n\nشحال رأس المال ديالك بالدولار؟",
            reply_markup=ReplyKeyboardRemove()
        )

    # ===== Capital Handling =====
    elif text.isdigit():

        capital = int(text)
        save_event(message.from_user.id, message.from_user.username, "capital", capital)

        if capital <= 100:
            lot = "0.01"
        elif capital <= 300:
            lot = "0.02"
        elif capital <= 500:
            lot = "0.03"
        else:
            lot = "0.05"

        await message.answer(
            f"👌 برأس مال {capital}$\n"
            f"اللوت المناسب ليك: {lot}\n\n"
            "⚠️ ما تخاطرش بأكثر من 2% فكل صفقة."
        )

        await message.answer(
            f"🔥 دابا مرحبا بك فالقناة الرسمية للإشارات 👇\n{SIGNAL_CHANNEL}"
        )

        await asyncio.sleep(120)

        await message.answer(
            "🔎 تذكير:\n"
            "دير Stop Loss قبل أي دخول.\n"
            "الانضباط أهم من الربح."
        )


async def main():
    print("🔥 SYSTEM WITH ACTIVATION CHANNEL RUNNING...")
    await dp.start_polling(bot)



asyncio.run(main())


