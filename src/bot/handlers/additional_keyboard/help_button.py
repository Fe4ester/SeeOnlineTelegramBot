from aiogram import Router
from aiogram.types import Message
from aiogram import F

# Тексты
from src.bot.texts.system_texts import help_text

router = Router()


@router.message(F.text == 'ℹ️ Помощь')
async def help_button(message: Message):
    await message.answer(
        help_text,
        parse_mode='HTML'
    )
