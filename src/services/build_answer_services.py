from typing import List, Dict, Optional
from collections import defaultdict
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
    DIAGRAM_USER_INTRO_TEMPLATE,
    PICK_DAY_INTRO_TEMPLATE
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


def group_statuses_by_day(statuses: List[OnlineStatus]) -> Dict[str, List[OnlineStatus]]:
    """
    Группируем список OnlineStatus по дате (ключи словаря — строка 'YYYY-MM-DD'),
    значения — список OnlineStatus за этот день.
    """
    grouped = defaultdict(list)
    for st in statuses:
        # st.created_at — datetime, берем только дату
        day_str = st.created_at.strftime("%Y-%m-%d")
        grouped[day_str].append(st)
    return dict(grouped)


def build_day_list_text(days: List[str]) -> str:
    """
    Строим пронумерованный список доступных дат.
    Если days пуст, возвращаем сообщение, что нет данных.
    """
    if not days:
        return "Нет доступных дат для отображения статистики."

    lines = [f"{idx}. {day}" for idx, day in enumerate(days, start=1)]
    day_list_str = "\n".join(lines)

    return PICK_DAY_INTRO_TEMPLATE.format(day_list_str=day_list_str)


def build_online_intervals_text(statuses: List[OnlineStatus]) -> str:
    """
    Преобразует список OnlineStatus в человекочитаемые интервалы: «с HH:MM до HH:MM».
    """
    if not statuses:
        return "Данные о времени онлайна отсутствуют."

    sorted_statuses = sorted(statuses, key=lambda x: x.created_at)
    intervals = []
    current_start: Optional[datetime] = None

    for st in sorted_statuses:
        if st.is_online and current_start is None:
            # Начало онлайн-интервала
            current_start = st.created_at
        elif not st.is_online and current_start is not None:
            # Конец онлайн-интервала
            intervals.append((current_start, st.created_at))
            current_start = None

    # Если остался незакрытый интервал
    if current_start is not None:
        last_created_at = sorted_statuses[-1].created_at
        intervals.append((current_start, last_created_at))

    # Формируем строки «с HH:MM до HH:MM»
    result_lines = []
    for start_dt, end_dt in intervals:
        start_str = start_dt.strftime("%H:%M")
        end_str = end_dt.strftime("%H:%M")
        result_lines.append(f"с {start_str} до {end_str}")

    if not result_lines:
        return "За выбранный день не было периодов онлайн."

    return "\n".join(result_lines)
