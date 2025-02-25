from aiogram import Router
from aiogram.types import Message
from aiogram import F

# Тексты
from src.bot.texts.main_keyboard_texts import my_tracking_text

router = Router()


@router.message(F.text == '👁 Мои отслеживания')
async def my_tracking_button(message: Message):
    await message.answer(
        my_tracking_text,
        parse_mode='HTML'
    )
