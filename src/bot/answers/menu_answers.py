from aiogram.types import Message
from src.services.tracker_service_client import SeeOnlineAPI
from src.config.settings import settings


async def get_main_menu_text(message: Message):
    async with SeeOnlineAPI(settings.EXTERNAL_SERVICE_API_URL) as api:
        user = await api.get_telegram_user(telegram_id=message.from_user.id)

        role = user[0].role
        tracked_users = f"{user[0].current_users} / {user[0].max_users}"

        menu_text = (
            "📊 <b>Статистика отслеживания</b>\n"
            f"👥 <b>Пользователей:</b>\n   <code>{tracked_users}</code>\n\n"
            f"🎭 <b>Роль:</b> <i>{role}</i>\n\n"
            "➕ <b>Добавить ещё?</b>"
        )

        return menu_text
