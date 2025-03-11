import asyncio
from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

from src.bot.answers.system_answers import START_TEXT
from src.bot.keyboards.inline import get_main_menu_keyboard

# Импортируем функцию сборки главного меню
from src.services.build_answer_services import build_main_menu_text

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    """Обработка команды /start."""
    await message.answer(
        START_TEXT,
        parse_mode='HTML'
    )

    await asyncio.sleep(0.6)

    # Отправляем главное меню
    main_menu_text = await build_main_menu_text(message.from_user.id)
    await message.answer(
        main_menu_text,
        parse_mode='HTML',
        reply_markup=get_main_menu_keyboard(),
    )
