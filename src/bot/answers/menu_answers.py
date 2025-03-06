from aiogram.types import Message
from src.services.tracker_service_client import SeeOnlineAPI

from src.config.settings import settings


async def get_main_menu_text(message: Message):
    async with SeeOnlineAPI(settings.EXTERNAL_SERVICE_API_URL) as api:
        user = await api.get_telegram_user(telegram_id=message.from_user.id)

        role = user[0].role
        tracked_users = f'{user[0].current_users}/{user[0].max_users}'

        menu_text = (
            "<b>🔍 Я отслеживаю:</b>"
            f"<code>{tracked_users}</code>\n\n"
            ""
            f"<i>🔧 [DEBUG] Ваша роль: {role}</i>\n\n"
            ""
            "➕ Добавить ещё?"
        )

        return menu_text
