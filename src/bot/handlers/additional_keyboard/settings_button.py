from aiogram import Router
from aiogram.types import Message
from aiogram import F

# Тексты
from src.bot.texts.additional_keyboard_texts import settings_text

router = Router()


@router.message(F.text == '⚙️ Настройки')
async def settings_button(message: Message):
    await message.answer(
        settings_text,
        parse_mode='HTML'
    )
