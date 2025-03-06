from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_menu_inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="Добавить пользователя", callback_data="add_tracked_user")
    keyboard.button(text="Кого я отслеживаю?", callback_data="get_tracked_users")
    keyboard.button(text="Дополнительно", callback_data="additional")
    keyboard.button(text="Помощь", callback_data="help")

    keyboard.adjust(1)

    return keyboard.as_markup()


def get_add_tracked_user_inline_keyboard():
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text='Назад', callback_data='cancel')

    keyboard.adjust(1)

    return keyboard.as_markup()
