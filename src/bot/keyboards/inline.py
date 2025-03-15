from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()


    keyboard.button(text="➕ Добавить пользователя", callback_data="add_tracked_user")
    keyboard.button(text="📋 Кого я отслеживаю?", callback_data="tracked_users_menu")

    keyboard.button(text="⚙️ Дополнительно", callback_data="additional")
    keyboard.button(text="❓ Помощь", callback_data="help")

    keyboard.adjust(1)

    return keyboard.as_markup()


def get_tracked_users_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()


    keyboard.button(text="📊 Получить график", callback_data="get_tracked_user_diagram")
    keyboard.button(text="🗑️ Удалить пользователя", callback_data="delete_tracked_user")
    keyboard.button(text="🔙 Назад", callback_data="cancel")

    keyboard.adjust(1)

    return keyboard.as_markup()


def back_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()


    keyboard.button(text="🔙 Назад", callback_data="cancel")

    keyboard.adjust(1)

    return keyboard.as_markup()


def build_delete_user_keyboard(tracked_users) -> InlineKeyboardMarkup:
    """
    Делаем инлайн-кнопки для каждого отслеживаемого пользователя.
    callback_data = "delete_user:{id}"
    """
    keyboard = InlineKeyboardBuilder()


    for user in tracked_users:
        cb_data = f"delete_user:{user.id}"
        keyboard.button(text=f"🗑️  @{user.username}", callback_data=cb_data)
    keyboard.button(text="🔙 Назад", callback_data="cancel")

    keyboard.adjust(1)
    return keyboard.as_markup()


def build_diagram_users_keyboard(tracked_users) -> InlineKeyboardMarkup:
    """
    Инлайн-кнопки для выбора пользователя, по которому хотим график.
    callback_data = "diagram_user:{id}"
    """
    keyboard = InlineKeyboardBuilder()


    for user in tracked_users:
        cb_data = f"diagram_user:{user.id}"
        keyboard.button(text=f"📊 @{user.username}", callback_data=cb_data)
    keyboard.button(text="🔙 Назад", callback_data="cancel")

    keyboard.adjust(1)
    return keyboard.as_markup()


def build_diagram_days_keyboard(tu_id: int, days: list[str]) -> InlineKeyboardMarkup:
    """
    Инлайн-кнопки для выбора конкретного дня: "diagram_day:{tu_id}:{YYYY-MM-DD}"
    """
    keyboard = InlineKeyboardBuilder()


    for day_str in days:
        cb_data = f"diagram_day:{tu_id}:{day_str}"
        keyboard.button(text=f"📅 {day_str}", callback_data=cb_data)

    keyboard.button(text="🔙 Назад", callback_data="cancel")
    keyboard.adjust(1)
    return keyboard.as_markup()


def build_delete_confirmation_keyboard(tracked_user_id: int) -> InlineKeyboardMarkup:
    """
    Клавиатура с кнопками «Да» / «Нет» для подтверждения удаления.
    callback_data:
      - confirm_delete_user:{tracked_user_id}
      - cancel_delete_user:{tracked_user_id}
    """
    keyboard = InlineKeyboardBuilder()


    keyboard.button(
        text="✅",
        callback_data=f"confirm_delete_user:{tracked_user_id}"
    )
    keyboard.button(
        text="❌",
        callback_data=f"cancel_delete_user:{tracked_user_id}"
    )

    keyboard.adjust(2)  # 2 кнопки в ряд
    return keyboard.as_markup()
