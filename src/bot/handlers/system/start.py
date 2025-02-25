from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

# Тексты
from src.bot.texts.system_texts import start_command_text

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(start_command_text)
