from typing import List, Optional
from datetime import datetime

from src.services.tracker_service_client import SeeOnlineAPI
from src.config.settings import settings
from src.services.tracker_service_models import OnlineStatus, TrackedUser

# Тексты
from src.bot.answers.menu_answers import MAIN_MENU_TEMPLATE
from src.bot.answers.menu_answers import (
    TRACKED_USERS_MENU_TEMPLATE,
    INVISIBLE_USERS_WARNING,
    NO_TRACKED_USERS_MESSAGE,
    NO_TRACKED_USERS_ANSWER,
    DELETE_USER_INTRO_TEMPLATE,
    DIAGRAM_USER_INTRO_TEMPLATE
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


def build_tracked_users_for_diagram_text(tracked_users: List[TrackedUser]) -> str:
    """
    Возвращает текст со списком отслеживаемых пользователей (пронумерованных),
    если список пуст — возвращает NO_TRACKED_USERS_ANSWER.
    """
    if not tracked_users:
        return NO_TRACKED_USERS_ANSWER

    tracked_list_str = "\n".join([
        f"{idx}. @{u.username}"
        for idx, u in enumerate(tracked_users, start=1)
    ])

    return DIAGRAM_USER_INTRO_TEMPLATE.format(tracked_list_str=tracked_list_str)


def build_online_intervals_text(statuses: List[OnlineStatus]) -> str:
    """
    Преобразует список OnlineStatus в человекочитаемые интервалы:
    «с HH:MM до HH:MM»
    """
    if not statuses:
        return "Данные о времени онлайна отсутствуют."

    # Сортируем статусы по created_at (на всякий случай)
    sorted_statuses = sorted(statuses, key=lambda x: x.created_at)

    intervals = []
    current_start: Optional[datetime] = None

    for st in sorted_statuses:
        if st.is_online and current_start is None:
            # Начинается новый онлайн-интервал
            current_start = st.created_at
        elif not st.is_online and current_start is not None:
            # Закрываем интервал
            intervals.append((current_start, st.created_at))
            current_start = None

    # Если закончились статусы, а current_start не закрыт
    if current_start is not None:
        # Пользователь, возможно, всё ещё онлайн,
        # тогда фиксируем последний момент как "последний зафиксированный статус"
        # Либо можно написать "до сейчас".
        last_created_at = sorted_statuses[-1].created_at
        intervals.append((current_start, last_created_at))

    # Формируем строки вида "с HH:MM до HH:MM"
    result_lines = []
    for start_dt, end_dt in intervals:
        start_str = start_dt.strftime("%H:%M")
        end_str = end_dt.strftime("%H:%M")
        result_lines.append(f"с {start_str} до {end_str}")

    # Если у нас нет ни одного «закрытого» интервала, значит, пользователь никогда не был онлайн
    if not result_lines:
        return "За данный период не было периодов онлайн."

    return "\n".join(result_lines)
