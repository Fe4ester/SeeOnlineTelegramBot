from aiogram.types import Message
from aiogram import Router

# Состояния
from aiogram.fsm.context import FSMContext
from src.bot.states.main_menu_states import AddTrackedUserStates

# Сервисы
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError

# Конфиг
from src.config.settings import settings

# Валидатор
from src.services.validators import is_valid_telegram_username

# Ответы
from src.bot.answers.menu_answers import incorrect_username_answer, unavailable_answer, get_successful_added_tracked_account_answer

router = Router()


@router.message(AddTrackedUserStates.waiting_for_username)
async def process_tracked_user_username(msg: Message, state: FSMContext):
    tg_id = msg.from_user.id
    username_to_track = msg.text.strip()
    is_valid = is_valid_telegram_username(username_to_track)

    if not is_valid:
        await msg.answer(incorrect_username_answer, parse_mode="html")
        return

    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            # Получим текущего TelegramUser
            users = await api.get_telegram_user(telegram_id=tg_id)
            if not users:
                await msg.answer(unavailable_answer)
                await state.clear()
                return

            telegram_user = users[0]
            telegram_user_id = telegram_user.id  # В модели это поле

            # Готовим данные для создания нового TrackedUser
            data_for_tracked_user = {
                "telegram_user_id": telegram_user_id,
                "username": username_to_track
            }

            # Пытаемся создать запись

            await api.create_tracked_user(data_for_tracked_user)

            # Сообщаем об успехе
            await msg.answer(get_successful_added_tracked_account_answer(username_to_track))

        except SeeOnlineAPIError as e:
            # Если ошибка на бэке
            await msg.answer(unavailable_answer)
        except Exception as e:
            # Любая другая ошибка
            await msg.answer(unavailable_answer)
        finally:
            # В конце — очищаем состояние
            await state.clear()
