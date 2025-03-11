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
    "Никто не отслеживается, добавь пользователя что бы я начал составлять график его онлайна!"
)

SUCCESSFUL_ADDED_TRACKED_ACCOUNT_MESSAGE = (
    "Пользователь @{username} успешно добавлен в список отслеживаемых!"
)

NO_TRACKED_USERS_ANSWER = "У вас пока нет отслеживаемых пользователей"
FULL_TRACKED_USER_CELLS_ANSWER = "У вас достигнут лимит отслеживаемых пользователей!"
SEND_USERNAME_ANSWER = "Отправьте юзернейм (без @)"
UNAVAILABLE_ANSWER = "Недоступно, попробуйте позже"
INCORRECT_USERNAME_ANSWER = "❌ <b>Ошибка: Некорректный юзернейм!</b>"

DELETE_USER_INTRO_TEMPLATE = """\
🗑️ <b>Удаление пользователя</b>

Доступные к удалению пользователи:

{tracked_list_str}

<i>Напишите <b>номер</b> пользователя, которого хотите удалить</i>
"""
DELETE_USER_NUMBER_NOT_DIGIT_ANSWER = (
    "Пожалуйста, введите <b>числовой</b> номер пользователя (или нажмите Назад)."
)
DELETE_USER_NOT_FOUND_TEMPLATE = (
    "Нет пользователя с номером {index}. Попробуйте снова или нажмите Назад."
)
DELETE_USER_FAILED_TEMPLATE = (
    "Не удалось удалить @{username}. Попробуйте позже."
)
DELETE_USER_SUCCESS_TEMPLATE = (
    "Пользователь @{username} успешно удалён из списка!"
)
