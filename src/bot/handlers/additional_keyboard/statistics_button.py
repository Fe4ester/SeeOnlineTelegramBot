from aiogram import Router
from aiogram.types import Message
from aiogram import F

# Тексты
from src.bot.texts.additional_keyboard_texts import statistics_text

router = Router()


@router.message(F.text == '📊 Статистика')
async def statistics_button(message: Message):
    await message.answer(
        statistics_text,
        parse_mode='HTML'
    )
