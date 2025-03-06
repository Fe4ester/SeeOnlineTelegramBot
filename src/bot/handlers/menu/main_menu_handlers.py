from aiogram.types import Message
from aiogram import Router

# Состояния
from aiogram.fsm.context import FSMContext
from src.bot.states.main_menu_states import AddTrackedUserStates

# Сервисы
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError

# Конфиг
from src.config.settings import settings

router = Router()


@router.message(AddTrackedUserStates.waiting_for_username)
async def process_tracked_user_username(msg: Message, state: FSMContext):
    tg_id = msg.from_user.id
    username_to_track = msg.text.strip()

    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            # Получим текущего TelegramUser
            users = await api.get_telegram_user(telegram_id=tg_id)
            if not users:
                await msg.answer("Недоступно, попробуйте позже")
                await state.clear()
                return

            telegram_user = users[0]
            telegram_user_id = telegram_user.id  # В модели это поле

            # Готовим данные для создания нового TrackedUser
            # По ТЗ tracker_account_id НЕ передаём, значит просто не указываем его
            data_for_tracked_user = {
                "telegram_user_id": telegram_user_id,
                "username": username_to_track,
                "visible_online": True
            }

            # Пытаемся создать запись
            await api.create_tracked_user(data_for_tracked_user)

            # Сообщаем об успехе
            await msg.answer(
                f"Пользователь @{username_to_track} успешно добавлен в список отслеживаемых!"
            )

        except SeeOnlineAPIError as e:
            # Если ошибка на бэке
            await msg.answer(
                "Недоступно, попробуйте позже"
            )
        except Exception as ex:
            # Любая другая ошибка
            await msg.answer(
                f"Недоступно, попробуйте позже"
            )
        finally:
            # В конце — очищаем состояние
            await state.clear()
