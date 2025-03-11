# src/bot/handlers/admin.py

from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src.bot.answers.admin_answers import ADMIN_COMMAND_TEXT

router = Router()

@router.message(Command('admin'))
async def cmd_admin(message: Message):
    """Команда /admin — пока заглушка."""
    await message.answer(ADMIN_COMMAND_TEXT)
