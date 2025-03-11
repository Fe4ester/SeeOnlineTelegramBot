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


def back_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='🔙 Назад', callback_data='cancel')

    keyboard.adjust(1)

    return keyboard.as_markup()
