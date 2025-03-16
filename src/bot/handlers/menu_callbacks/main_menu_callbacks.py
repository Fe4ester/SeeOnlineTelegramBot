from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext

from src.bot.keyboards.inline import (
    back_keyboard,
    get_tracked_users_menu_keyboard,
    get_additional_keyboard,
    get_help_keyboard
)
from src.bot.states.main_menu_states import AddTrackedUserStates
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError
from src.config.settings import settings
from src.services.build_answer_services import build_tracked_users_menu_text

# Импортируем все тексты из menu_answers
from src.bot.answers.menu_answers import (
    UNAVAILABLE_ANSWER,
    FULL_TRACKED_USER_CELLS_ANSWER,
    SEND_USERNAME_ANSWER,
    ADDITIONAL_MENU_ANSWER,
    HELP_MENU_ANSWER,
    EXTRA_INFO_ANSWER
)

router = Router()


@router.callback_query(F.data == "add_tracked_user")
async def add_tracked_user_callback(callback: CallbackQuery, state: FSMContext):
    tg_id = callback.from_user.id
    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            users = await api.get_telegram_user(telegram_id=tg_id)
            telegram_user = users[0]
            if telegram_user.current_users >= telegram_user.max_users:
                await callback.answer(text=FULL_TRACKED_USER_CELLS_ANSWER)
                return

            await callback.message.edit_text(
                text=SEND_USERNAME_ANSWER,
                reply_markup=back_keyboard()
            )
            await state.set_state(AddTrackedUserStates.waiting_for_username)
            await callback.answer()

        except SeeOnlineAPIError:
            await callback.answer(text=UNAVAILABLE_ANSWER)
            return


@router.callback_query(F.data == "tracked_users_menu")
async def tracked_users_menu_callback(callback: CallbackQuery):
    text = await build_tracked_users_menu_text(callback.from_user.id)
    await callback.message.edit_text(
        text=text,
        parse_mode='html',
        reply_markup=get_tracked_users_menu_keyboard()
    )


@router.callback_query(F.data == "additional")
async def additional_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text=ADDITIONAL_MENU_ANSWER,
        parse_mode="html",
        reply_markup=get_additional_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "help")
async def help_callback(callback: CallbackQuery):
    await callback.message.edit_text(
        text=HELP_MENU_ANSWER,
        parse_mode="html",
        reply_markup=get_help_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "extra_info")
async def extra_info_callback(callback: CallbackQuery):
    await callback.answer(EXTRA_INFO_ANSWER)
