from aiogram import Router, F
from aiogram.types import CallbackQuery

# Работа с состояниями
from aiogram.fsm.context import FSMContext
from src.bot.states.tracked_users_menu_states import DeleteTrackedUserStates

# Логика
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError

# Клавиатуры
from src.bot.keyboards.inline import back_keyboard

# Ответы
from src.bot.answers.menu_answers import (
    unavailable_answer,
    no_tracked_users_answer,

)

# Настройки
from src.config.settings import settings

router = Router()


@router.callback_query(F.data == "delete_tracked_user")
async def delete_tracked_user_callback(callback: CallbackQuery, state: FSMContext):

    user_id = callback.from_user.id

    # Получаем список отслеживаемых пользователей
    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            tracked_users = await api.get_tracked_user(telegram_user_id=user_id)
        except SeeOnlineAPIError:
            await callback.answer(
                text=unavailable_answer,
                show_alert=True
            )
            return

    if not tracked_users:
        # Если список пуст, сразу говорим об этом и выходим
        await callback.message.edit_text(
            no_tracked_users_answer,
            reply_markup=back_keyboard()
        )
        await callback.answer()
        return

    # Формируем пронумерованный список
    tracked_list_str = "\n".join([
        f"{idx}. @{u.username}" for idx, u in enumerate(tracked_users, start=1)
    ])

    text_for_user = (
        "🗑️ <b>Удаление пользователя</b>\n\n"
        "Доступные к удалению пользователи:\n\n"
        f"{tracked_list_str}\n\n"
        "<i>Напишите <b>номер</b> пользователя, которого хотите удалить</i>"
    )


    await state.update_data(tracked_users=tracked_users)

    await callback.message.edit_text(
        text=text_for_user,
        parse_mode="HTML",
        reply_markup=back_keyboard()
    )
    await state.set_state(DeleteTrackedUserStates.waiting_for_user_number)
    await callback.answer()
