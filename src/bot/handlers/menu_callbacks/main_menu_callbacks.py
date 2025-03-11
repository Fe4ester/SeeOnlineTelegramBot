from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.states.main_menu_states import AddTrackedUserStates
from src.bot.keyboards.inline import back_keyboard, get_tracked_users_menu_keyboard
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError
from src.config.settings import settings

# Тексты
from src.bot.answers.menu_answers import (
    UNAVAILABLE_ANSWER,
    FULL_TRACKED_USER_CELLS_ANSWER,
    SEND_USERNAME_ANSWER
)

# Функция для формирования текста меню отслеживаемых пользователей
from src.services.build_answer_services import build_tracked_users_menu_text

router = Router()


@router.callback_query(F.data == "add_tracked_user")
async def add_tracked_user_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка нажатия «Добавить пользователя»."""
    tg_id = callback.from_user.id

    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            users = await api.get_telegram_user(telegram_id=tg_id)
            telegram_user = users[0]
            if telegram_user.current_users >= telegram_user.max_users:
                await callback.answer(
                    text=FULL_TRACKED_USER_CELLS_ANSWER,
                    show_alert=True
                )
                return

            # Переходим к состоянию ожидания ввода юзернейма
            await callback.message.edit_text(
                text=SEND_USERNAME_ANSWER,
                reply_markup=back_keyboard()
            )
            await state.set_state(AddTrackedUserStates.waiting_for_username)
            await callback.answer()

        except SeeOnlineAPIError:
            await callback.answer(
                text=UNAVAILABLE_ANSWER,
                show_alert=True
            )
            return


@router.callback_query(F.data == "tracked_users_menu")
async def tracked_users_menu_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка нажатия «Отслеживаемые пользователи»."""
    text = await build_tracked_users_menu_text(callback.from_user.id)
    await callback.message.edit_text(
        text=text,
        parse_mode='html',
        reply_markup=get_tracked_users_menu_keyboard()
    )
