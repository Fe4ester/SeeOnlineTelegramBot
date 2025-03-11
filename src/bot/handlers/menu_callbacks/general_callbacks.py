from aiogram.types import CallbackQuery
from aiogram import Router
from aiogram import F

# Работа с состояниями
from aiogram.fsm.context import FSMContext

# Клавиатуры
from src.bot.keyboards.inline import get_main_menu_keyboard

# Ответы
from src.bot.answers.menu_answers import (
    get_main_menu_text,
)

router = Router()


@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        text=await get_main_menu_text(callback.from_user.id),
        parse_mode='html',
        reply_markup=get_main_menu_keyboard()
    )
    await state.clear()
