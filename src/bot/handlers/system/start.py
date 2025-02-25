from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

# Тексты
from src.bot.texts.system_texts import start_text

# Клавиатуры
from src.bot.keyboards.reply import get_main_keyboard

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        start_text,
        parse_mode='HTML',
        reply_markup=get_main_keyboard()
    )
