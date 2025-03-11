from src.services.tracker_service_client import SeeOnlineAPI
from src.config.settings import settings


async def get_main_menu_text(user_id: int):
    async with SeeOnlineAPI(settings.EXTERNAL_SERVICE_API_URL) as api:
        user = await api.get_telegram_user(telegram_id=user_id)
        role = user[0].role
        counter_tracked_users = f"{user[0].current_users} / {user[0].max_users}"

        menu_text = (
            "📊 <b>Статистика отслеживания</b>\n"
            f"👥 <b>Пользователей:</b>\n   <code>{counter_tracked_users}</code>\n\n"
            f"🎭 <b>Роль:</b> <i>{role}</i>\n\n"
            "➕ <b>Добавить ещё?</b>"
        )

        return menu_text


async def get_tracked_users_menu_text(user_id: int):
    async with SeeOnlineAPI(settings.EXTERNAL_SERVICE_API_URL) as api:
        user = await api.get_telegram_user(telegram_id=user_id)
        counter_tracked_users = f"{user[0].current_users} / {user[0].max_users}"

        tracked_users = await api.get_tracked_user(telegram_user_id=user_id)

        # Формируем список для отображения:
        if tracked_users:
            tracked_users_str = "\n".join(
                [
                    f"{idx}. @{u.username} "
                    f"{'' if u.visible_online else '| Не отслеживаю'}"
                    for idx, u in enumerate(tracked_users, start=1)
                ]
            )
        else:
            tracked_users_str = "Никто не отслеживается, добавь пользователя что бы я начал составлять график его онлайна!"

        # Проверяем, есть ли в списке пользователи со скрытым онлайном
        has_invisible_users = any(not u.visible_online for u in tracked_users)

        # Формируем текст основного меню:
        menu_text = (
            "📊 <b>Отслеживаемые пользователи</b>\n\n"
            f"👥 <b>Пользователей:</b>\n   <code>{counter_tracked_users}</code>\n\n"
            "💼 <b>Отслеживаемые пользователи:</b>\n\n"
            f"{tracked_users_str}\n\n"
        )

        # Добавляем предупреждение только если есть скрытые пользователи
        if has_invisible_users:
            menu_text += (
                "<u>⚠️ Почему не отслеживаю?\n"
                "Я не могу следить за аккаунтами со скрытым онлайном\n"
                "Такие аккаунты удаляются в течение 3 часов</u>"
            )

        return menu_text


def get_successful_added_tracked_account_answer(username: str) -> str:
    return f"Пользователь @{username} успешно добавлен в список отслеживаемых!"


incorrect_username_answer = message = """
❌ <b>Ошибка: Некорректный юзернейм!</b>"""

unavailable_answer = "Недоступно, попробуйте позже"

full_tracked_user_cells_answer = "У вас достигнут лимит отслеживаемых пользователей!"

send_username_answer = "Отправьте юзернейм (без @)"
