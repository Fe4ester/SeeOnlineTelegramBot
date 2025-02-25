from aiogram import Router
from aiogram.types import Message
from aiogram import F

# Тексты
from src.bot.texts.main_keyboard_texts import add_user_text

router = Router()


@router.message(F.text == '➕ Добавить пользователя')
async def add_user_button(message: Message):
    await message.answer(
        add_user_text,
        parse_mode='HTML'
    )
