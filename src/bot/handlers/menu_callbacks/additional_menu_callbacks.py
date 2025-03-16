from aiogram import Router, F
from aiogram.types import CallbackQuery

# Импортируем нужные ответы
from src.bot.answers.menu_answers import (
    SET_THEME_ANSWER,
    SET_TIMEZONE_ANSWER
)

router = Router()


@router.callback_query(F.data == "set_theme")
async def set_theme_callback(callback: CallbackQuery):
    await callback.answer(SET_THEME_ANSWER)


@router.callback_query(F.data == "set_timezone")
async def set_timezone_callback(callback: CallbackQuery):
    await callback.answer(SET_TIMEZONE_ANSWER)
