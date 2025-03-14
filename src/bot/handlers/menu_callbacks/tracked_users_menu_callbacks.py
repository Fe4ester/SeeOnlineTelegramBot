from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.states.tracked_users_menu_states import DeleteTrackedUserStates
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError
from src.config.settings import settings
from src.bot.keyboards.inline import back_keyboard
from src.services.build_answer_services import build_delete_user_intro_text, build_tracked_users_for_diagram_text
from src.bot.states.tracked_users_menu_states import GetDiagramStates

# Тексты
from src.bot.answers.menu_answers import (
    UNAVAILABLE_ANSWER,
    NO_TRACKED_USERS_MESSAGE
)

router = Router()


@router.callback_query(F.data == "delete_tracked_user")
async def delete_tracked_user_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка нажатия «Удалить пользователя»."""
    user_id = callback.from_user.id

    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            tracked_users = await api.get_tracked_user(telegram_user_id=user_id)
        except SeeOnlineAPIError:
            await callback.answer(
                text=UNAVAILABLE_ANSWER
            )
            return

    text_for_user = build_delete_user_intro_text(tracked_users)

    await state.update_data(tracked_users=tracked_users)

    await callback.message.edit_text(
        text=text_for_user,
        parse_mode="HTML",
        reply_markup=back_keyboard()
    )

    if tracked_users:
        await state.set_state(DeleteTrackedUserStates.waiting_for_user_number)

    await callback.answer(NO_TRACKED_USERS_MESSAGE)


@router.callback_query(F.data == "get_tracked_user_diagram")
async def get_tracked_user_diagram_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка нажатия «Получить диаграмму (интервалы)»."""
    user_id = callback.from_user.id

    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            tracked_users = await api.get_tracked_user(telegram_user_id=user_id)
        except SeeOnlineAPIError:
            await callback.answer(
                text=UNAVAILABLE_ANSWER,
                show_alert=True
            )
            return

    # Формируем текст со списком отслеживаемых пользователей
    text_for_user = build_tracked_users_for_diagram_text(tracked_users)

    # Сохраняем список в FSM, чтобы потом пользователь выбрал
    await state.update_data(tracked_users=tracked_users)

    # Показываем пользователю
    await callback.message.edit_text(
        text=text_for_user,
        parse_mode="HTML",
        reply_markup=back_keyboard()
    )

    # Если список не пустой — переходим в состояние ожидания номера пользователя
    if tracked_users:
        await state.set_state(GetDiagramStates.waiting_for_user_number)

    await callback.answer()
