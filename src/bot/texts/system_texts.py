from aiogram.types import Message
from src.services.tracker_service_client import SeeOnlineAPI

from src.config.settings import settings

start_text = """
<b>👋 Привет! Я - Бот для слежки</b>

ℹ️ <b>Как пользоваться?</b>
• Добавь пользователей для мониторинга
• Смотри графики онлайна

<u>⚠️ Я нахожусь в раннем доступе, возможны ошибки</u>

✅ Если обнаружишь баг пиши в поддержку - @seeonline_support

❔ <i>Подробнее:</i> /help
"""

help_text = """
<b>🔧 Как это работает?</b>

Я слежу за онлайном пользователей и составляю графики

<i>ℹ️ График составляется со временем, 
нужно подождать пока я соберу статистику</i>

<b>🚀 Что я умею?</b>
    ✅ Отправлять графики с онлайном

<b>📝 Что находится в активной разработке?</b>
    ✏️ Оповещения смены статуса в реальном времени
    ✏️ Пересечения онлайнов разных пользователей

<i>Добавляй пользователей и я начну составлять статистику!</i>
"""


async def get_menu_text(message: Message):
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
