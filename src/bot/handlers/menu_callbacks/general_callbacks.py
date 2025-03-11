from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.keyboards.inline import get_main_menu_keyboard

# Тексты
from src.services.build_answer_services import build_main_menu_text

router = Router()


@router.callback_query(F.data == "cancel")
async def cancel_callback(callback: CallbackQuery, state: FSMContext):
    """Кнопка «Назад/Отмена» – возвращаем пользователя в главное меню."""
    await callback.message.delete()

    main_menu_text = await build_main_menu_text(callback.from_user.id)
    await callback.message.answer(
        text=main_menu_text,
        parse_mode='html',
        reply_markup=get_main_menu_keyboard()
    )

    await state.clear()
