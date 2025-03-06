from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

# Тексты
from src.bot.answers.admin_answers import admin_command_text

router = Router()


@router.message(Command('admin'))
async def cmd_help(message: Message):
    await message.answer(admin_command_text)
