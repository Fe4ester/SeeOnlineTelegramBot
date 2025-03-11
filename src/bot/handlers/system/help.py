from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command
from src.bot.answers.system_answers import HELP_TEXT

router = Router()


@router.message(Command('help'))
async def cmd_help(message: Message):
    await message.answer(
        HELP_TEXT,
        parse_mode='HTML'
    )
