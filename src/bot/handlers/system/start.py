import asyncio

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

# Тексты
from src.bot.texts.system_texts import start_text
from src.bot.texts.menu_text import get_main_menu_text

# Клавиатуры
from src.bot.keyboards.inline import get_menu_inline_keyboard

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        start_text,
        parse_mode='HTML'
    )
    await asyncio.sleep(0.6)
    await message.answer(
        await get_main_menu_text(message),
        parse_mode='HTML',
        reply_markup=get_menu_inline_keyboard(),

    )
