import os
import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import CommandStart

BOT_TOKEN = ("8605977902:AAFcABeU2bbnDJenJ0qLgpvBbOceWC3GzsU")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()


# ===== START COMMAND =====
@dp.message(CommandStart())
async def start_handler(message: Message):

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🚀 ابدأ ب $10 + بونص $30",
                callback_data="roboforex"
            )
        ],
        [
            InlineKeyboardButton(
                text="🏦 حساب احترافي طويل المدى",
                callback_data="exness"
            )
        ]
    ])

    await message.answer(
        "🔥 مرحبا بك في نظام Omar Swing VIP\n\n"
        "اختر المسار المناسب لك:",
        reply_markup=keyboard
    )


# ===== ROBOFOREX =====
@dp.callback_query(F.data == "roboforex")
async def roboforex_handler(callback: CallbackQuery):

    await callback.message.edit_text(
        "🔥 اختيار ممتاز!\n\n"
        "سجل الآن واستفد من بونص $30:\n\n"
        "https://my.roboforex.com/en/?a=omawl"
    )

    await callback.answer()


# ===== EXNESS =====
@dp.callback_query(F.data == "exness")
async def exness_handler(callback: CallbackQuery):

    await callback.message.edit_text(
        "🏦 حساب احترافي طويل المدى\n\n"
        "افتح حسابك عبر الرابط التالي:\n\n"
        "https://one.exnessonelink.com/a/zi8w32eknv"
    )

    await callback.answer()


# ===== MAIN =====
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
