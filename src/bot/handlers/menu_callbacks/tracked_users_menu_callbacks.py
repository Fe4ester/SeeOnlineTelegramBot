from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.states.tracked_users_menu_states import DeleteTrackedUserStates
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError
from src.config.settings import settings
from src.bot.keyboards.inline import back_keyboard

# Тексты
from src.bot.answers.menu_answers import (
    UNAVAILABLE_ANSWER,
    NO_TRACKED_USERS_ANSWER,
    DELETE_USER_INTRO_TEMPLATE,
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
                text=UNAVAILABLE_ANSWER,
                show_alert=True
            )
            return

    if not tracked_users:
        # Если список пуст – сообщаем и не переводим в состояние
        await callback.message.edit_text(
            NO_TRACKED_USERS_ANSWER,
            reply_markup=back_keyboard()
        )
        await callback.answer()
        return

    # Формируем пронумерованный список
    tracked_list_str = "\n".join([
        f"{idx}. @{u.username}" for idx, u in enumerate(tracked_users, start=1)
    ])

    text_for_user = DELETE_USER_INTRO_TEMPLATE.format(tracked_list_str=tracked_list_str)

    # Сохраняем список в FSM
    await state.update_data(tracked_users=tracked_users)

    # Переходим в состояние ожидания номера
    await callback.message.edit_text(
        text=text_for_user,
        parse_mode="HTML",
        reply_markup=back_keyboard()
    )
    await state.set_state(DeleteTrackedUserStates.waiting_for_user_number)
    await callback.answer()
