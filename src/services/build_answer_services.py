from src.services.tracker_service_client import SeeOnlineAPI
from src.config.settings import settings

# Тексты
from src.bot.answers.menu_answers import MAIN_MENU_TEMPLATE
from src.bot.answers.menu_answers import (
    TRACKED_USERS_MENU_TEMPLATE,
    INVISIBLE_USERS_WARNING,
    NO_TRACKED_USERS_MESSAGE,
    NO_TRACKED_USERS_ANSWER,
    DELETE_USER_INTRO_TEMPLATE
)


async def build_main_menu_text(user_id: int) -> str:
    """Формирует текст главного меню."""
    async with SeeOnlineAPI(settings.EXTERNAL_SERVICE_API_URL) as api:
        user = await api.get_telegram_user(telegram_id=user_id)
        role = user[0].role
        counter_tracked_users = f"{user[0].current_users} / {user[0].max_users}"

    return MAIN_MENU_TEMPLATE.format(
        counter_tracked_users=counter_tracked_users,
        role=role
    )


async def build_tracked_users_menu_text(user_id: int) -> str:
    """Формирует текст для меню 'Отслеживаемые пользователи'."""
    async with SeeOnlineAPI(settings.EXTERNAL_SERVICE_API_URL) as api:
        user = await api.get_telegram_user(telegram_id=user_id)
        counter_tracked_users = f"{user[0].current_users} / {user[0].max_users}"
        tracked_users = await api.get_tracked_user(telegram_user_id=user_id)

    if tracked_users:
        tracked_users_str = "\n".join([
            f"{idx}. @{u.username} {'' if u.visible_online else '| Не отслеживаю'}"
            for idx, u in enumerate(tracked_users, start=1)
        ])
    else:
        tracked_users_str = NO_TRACKED_USERS_MESSAGE

    has_invisible_users = any(not u.visible_online for u in tracked_users)
    invisible_warning = INVISIBLE_USERS_WARNING if has_invisible_users else ""

    return TRACKED_USERS_MENU_TEMPLATE.format(
        counter_tracked_users=counter_tracked_users,
        tracked_users_str=tracked_users_str,
        invisible_warning=invisible_warning
    )


def build_delete_user_intro_text(tracked_users) -> str:
    """
    Формирует текст для сообщения, где выводится список
    пользователей (пронумерованных).
    """
    if not tracked_users:
        return NO_TRACKED_USERS_ANSWER

    tracked_list_str = "\n".join(
        f"{idx}. @{u.username}" for idx, u in enumerate(tracked_users, start=1)
    )

    return DELETE_USER_INTRO_TEMPLATE.format(tracked_list_str=tracked_list_str)
