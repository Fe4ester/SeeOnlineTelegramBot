from aiogram.types import CallbackQuery, Message
from aiogram import Router
from aiogram import F

from aiogram.fsm.context import FSMContext
from src.bot.states.main_menu_states import AddTrackedUserStates

from src.bot.keyboards.inline import get_add_tracked_user_inline_keyboard

from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError

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
            if not users:
                # Если пользователя нет в БД — возможно, нужно его создать
                # Но здесь, по условию, предположим, что user точно есть
                await callback.answer("Кажется, вы не зарегистрированы в системе")
                return

            # По вашей структуре может вернуться список, берём первый:
            telegram_user = users[0]

            if telegram_user.current_users >= telegram_user.max_users:
                await callback.answer(
                    text="У вас достигнут лимит отслеживаемых пользователей!",
                    show_alert=True
                )
                return

            # Если места хватает, говорим пользователю, что нужно ввести username
            await callback.message.edit_text(
                text="Отправьте юзернейм (без @) того, кого хотите отслеживать:",
                reply_markup=get_add_tracked_user_inline_keyboard()
            )
            # Устанавливаем состояние:
            await state.set_state(AddTrackedUserStates.waiting_for_username)
            await callback.answer()

        except SeeOnlineAPIError as e:
            await callback.answer(
                text=f"Недоступно, попробуйте позже",
                show_alert=True
            )
            return
