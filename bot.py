
import os
import logging
from aiogram import Bot, Dispatcher, executor, types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from dotenv import load_dotenv
from cryptopay import CryptoPay

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
CRYPTOBOT_TOKEN = os.getenv("CRYPTOBOT_TOKEN")
SUPPORT_LINK = os.getenv("SUPPORT_LINK", "https://t.me/hamonasa")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

crypto = CryptoPay(token=CRYPTOBOT_TOKEN, network="TON")

# Главное меню
@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("📅 Записаться", callback_data="book"),
        InlineKeyboardButton("👤 Стать мастером", callback_data="become_master"),
        InlineKeyboardButton("🛠 Служба поддержки", url=SUPPORT_LINK),
    )
    await message.answer("Добро пожаловать! Выберите действие:", reply_markup=kb)

# Обработка кнопок
@dp.callback_query_handler(lambda c: c.data == "become_master")
async def become_master(callback: types.CallbackQuery):
    kb = InlineKeyboardMarkup()
    kb.add(
        InlineKeyboardButton("3 дня — 20$", callback_data="subscribe_3d"),
        InlineKeyboardButton("10 дней — 50$", callback_data="subscribe_10d"),
        InlineKeyboardButton("1 месяц — 120$", callback_data="subscribe_1m"),
        InlineKeyboardButton("Навсегда — 300$", callback_data="subscribe_forever"),
    )
    await callback.message.answer("Выберите подписку:", reply_markup=kb)

@dp.callback_query_handler(lambda c: c.data.startswith("subscribe_"))
async def handle_subscription(callback: types.CallbackQuery):
    option = callback.data.split("_")[1]
    amount_usd = {
        "3d": 20,
        "10d": 50,
        "1m": 120,
        "forever": 300
    }[option]

    invoice = await crypto.create_invoice(asset="TON", amount=amount_usd, description="Подписка мастера")
    await callback.message.answer(
        f"💳 Оплата подписки: {amount_usd}$

Нажмите кнопку ниже 👇",
        reply_markup=InlineKeyboardMarkup().add(
            InlineKeyboardButton("💰 Оплатить", url=invoice.pay_url)
        )
    )

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)
    