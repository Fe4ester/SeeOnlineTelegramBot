from aiogram.types import CallbackQuery, Message
from aiogram import Router
from aiogram import F

# Работа с состояниями
from aiogram.fsm.context import FSMContext
from src.bot.states.main_menu_states import AddTrackedUserStates

# Клавиатуры
from src.bot.keyboards.inline import back_keyboard, get_tracked_users_menu_keyboard

# Сервисы
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError

# Ответы
from src.bot.answers.menu_answers import (
    unavailable_answer,
    full_tracked_user_cells_answer,
    send_username_answer,
    get_tracked_users_menu_text
)

# Настройки
from src.config.settings import settings

router = Router()


@router.callback_query(F.data == "add_tracked_user")
async def add_tracked_user_callback(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id

    # Получаем данные о пользователе из внешнего API
    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            # get_telegram_user может вернуть список или None, если pk=None
            users = await api.get_telegram_user(telegram_id=tg_id)

            # По вашей структуре может вернуться список, берём первый:
            telegram_user = users[0]

            if telegram_user.current_users >= telegram_user.max_users:
                await callback.answer(
                    text=full_tracked_user_cells_answer,
                    show_alert=True
                )
                return

            # Если места хватает, говорим пользователю, что нужно ввести username
            await callback.message.edit_text(
                text=send_username_answer,
                reply_markup=back_keyboard()
            )
            # Устанавливаем состояние:
            await state.set_state(AddTrackedUserStates.waiting_for_username)
            await callback.answer()

        except SeeOnlineAPIError as e:
            await callback.answer(
                text=unavailable_answer,
                show_alert=True
            )
            return


@router.callback_query(F.data == "tracked_users_menu")
async def tracked_users_menu_callback(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        text=await get_tracked_users_menu_text(callback.from_user.id),
        parse_mode='html',
        reply_markup=get_tracked_users_menu_keyboard()
    )
