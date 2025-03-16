# menu_answers.py

MAIN_MENU_TEMPLATE = """\
📊 <b>Статистика отслеживания</b>
👥 <b>Пользователей:</b>
   <code>{counter_tracked_users}</code>

🎭 <b>Роль:</b> <i>{role}</i>

➕ <b>Добавить ещё?</b>
"""

TRACKED_USERS_MENU_TEMPLATE = """\
📊 <b>Отслеживаемые пользователи</b>

👥 <b>Пользователей:</b>
   <code>{counter_tracked_users}</code>

💼 <b>Отслеживаемые пользователи:</b>

{tracked_users_str}

{invisible_warning}
"""

INVISIBLE_USERS_WARNING = """\
<u>⚠️ Почему не отслеживаю?
Я не могу следить за аккаунтами со скрытым онлайном
Такие аккаунты удаляются в течение 3 часов</u>
"""

NO_TRACKED_USERS_MESSAGE = (
    "⚠️ Никто не отслеживается, добавь пользователя что бы я начал составлять график его онлайна!"
)

SUCCESSFUL_ADDED_TRACKED_ACCOUNT_MESSAGE = (
    "✅ Пользователь @{username} успешно добавлен в список отслеживаемых!"
)

FULL_TRACKED_USER_CELLS_ANSWER = "⚠️ У вас достигнут лимит отслеживаемых пользователей!"
SEND_USERNAME_ANSWER = "🔍 Отправьте юзернейм (без @)"
UNAVAILABLE_ANSWER = "⚠️ Недоступно, попробуйте позже"
INCORRECT_USERNAME_ANSWER = "❌ <b>Ошибка: Некорректный юзернейм!</b>"

DELETE_USER_FAILED_TEMPLATE = (
    "⚠️ Не удалось удалить @{username}. Попробуйте позже."
)
DELETE_USER_SUCCESS_TEMPLATE = (
    "✅ Пользователь @{username} успешно удалён из списка!"
)

NO_TRACKING_DATA = (
    "⚠️ Нет информации для получения графика, подождите немного и она появится"
)

DELETE_SELECT_USER_PROMPT = "🔍 Выберите пользователя для удаления:"
INVALID_DATA_FORMAT = "⚠️ Некорректный формат данных!"
USER_NOT_FOUND = "⚠️ Пользователь не найден"
CONFIRM_DELETE_USER_TEMPLATE = (
    "⁉️ Точно удалить @{username}?\n\n <u>⚠️ Внимание, после удаления пользователя\n удалятся все данные о посещении</u>"
)

SELECT_USER_FOR_CHART = "🔍 Выберите пользователя:"
SELECT_DAY = "🔍 Выберите день:"
CHART_CAPTION_TEMPLATE = "✅ Статистика онлайна @{username} за {day_str}"

# Новые тексты для разделов "Дополнительно" и "Помощь"
ADDITIONAL_MENU_ANSWER = (
    "⚙️ <b>Дополнительные настройки</b>\n\n"
    "• <b>Тема:</b> {theme}\n"
    "• <b>Часовой пояс:</b> {timezone}"
)

HELP_MENU_ANSWER = (
    "❓ <b>Помощь</b>\n\n"
    "• <b>Поддержка:</b> @seeonline_support"
)

SET_THEME_ANSWER = "Функция настройки темы в разработке."
SET_TIMEZONE_ANSWER = "Функция настройки часового пояса в разработке."
EXTRA_INFO_ANSWER = "Дополнительная информация о боте в разработке."
