from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.bot.states.main_menu_states import AddTrackedUserStates
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError
from src.config.settings import settings
from src.services.validators import is_valid_telegram_username

# Тексты
from src.bot.answers.menu_answers import (
    INCORRECT_USERNAME_ANSWER,
    UNAVAILABLE_ANSWER,
    SUCCESSFUL_ADDED_TRACKED_ACCOUNT_MESSAGE,
)

router = Router()


@router.message(AddTrackedUserStates.waiting_for_username)
async def process_tracked_user_username(msg: Message, state: FSMContext):
    """Добавление пользователя в отслеживание."""
    tg_id = msg.from_user.id
    username_to_track = msg.text.strip()

    if not is_valid_telegram_username(username_to_track):
        await msg.answer(INCORRECT_USERNAME_ANSWER, parse_mode="html")
        return

    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            # Получаем текущего TelegramUser
            users = await api.get_telegram_user(telegram_id=tg_id)
            if not users:
                await msg.answer(UNAVAILABLE_ANSWER)
                await state.clear()
                return

            telegram_user = users[0]

            # Создаём нового TrackedUser
            data_for_tracked_user = {
                "telegram_user_id": telegram_user.id,
                "username": username_to_track
            }

            await api.create_tracked_user(data_for_tracked_user)

            # Сообщаем об успехе
            success_text = SUCCESSFUL_ADDED_TRACKED_ACCOUNT_MESSAGE.format(username=username_to_track)
            await msg.answer(success_text)

        except SeeOnlineAPIError:
            await msg.answer(UNAVAILABLE_ANSWER)
        except Exception:
            await msg.answer(UNAVAILABLE_ANSWER)
        finally:
            await state.clear()
