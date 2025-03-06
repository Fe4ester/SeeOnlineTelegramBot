from aiogram.utils.keyboard import InlineKeyboardBuilder


from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup


def get_main_menu_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardBuilder()

    # Основные действия
    keyboard.button(text="➕ Добавить пользователя", callback_data="add_tracked_user")
    keyboard.button(text="📋 Кого я отслеживаю?", callback_data="get_tracked_users")

    # Дополнительные опции
    keyboard.button(text="⚙️ Дополнительно", callback_data="additional")
    keyboard.button(text="❓ Помощь", callback_data="help")

    # Группируем кнопки: первые две в один ряд, остальные — отдельно
    keyboard.adjust(1)

    return keyboard.as_markup()



def get_add_tracked_user_inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Назад', callback_data='cancel')

    keyboard.adjust(1)

    return keyboard.as_markup()
