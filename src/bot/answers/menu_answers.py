from src.services.tracker_service_client import SeeOnlineAPI
from src.config.settings import settings


async def get_main_menu_text(user_id: int):
    async with SeeOnlineAPI(settings.EXTERNAL_SERVICE_API_URL) as api:
        user = await api.get_telegram_user(telegram_id=user_id)
        role = user[0].role
        tracked_users = f"{user[0].current_users} / {user[0].max_users}"

        menu_text = (
            "📊 <b>Статистика отслеживания</b>\n"
            f"👥 <b>Пользователей:</b>\n   <code>{tracked_users}</code>\n\n"
            f"🎭 <b>Роль:</b> <i>{role}</i>\n\n"
            "➕ <b>Добавить ещё?</b>"
        )

        return menu_text


def get_successful_added_tracked_account_answer(username: str) -> str:
    return f"Пользователь @{username} успешно добавлен в список отслеживаемых!"


incorrect_username_answer = message = """
❌ <b>Ошибка: Некорректный юзернейм!</b>"""

unavailable_answer = "Недоступно, попробуйте позже"

full_tracked_user_cells_answer = "У вас достигнут лимит отслеживаемых пользователей!"

send_username_answer = "Отправьте юзернейм (без @)"
