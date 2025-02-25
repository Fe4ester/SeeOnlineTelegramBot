from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

# Тексты
from src.bot.texts.system_texts import help_text

router = Router()


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(
        help_text,
        parse_mode='HTML'
    )
