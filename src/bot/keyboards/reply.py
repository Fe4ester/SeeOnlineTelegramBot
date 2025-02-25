from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def _create_keyboard(buttons: list[list[str]], resize: bool = True) -> ReplyKeyboardMarkup:
    """Генератор клавиатуры, подходит для всех reply"""
    kb_builder = ReplyKeyboardBuilder()
    for row in buttons:
        kb_builder.row(*[KeyboardButton(text=btn) for btn in row])
    return kb_builder.as_markup(resize_keyboard=resize)


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Главное меню (95% времени у пользователя)"""
    return _create_keyboard([
        ["👁 Мои отслеживания", "➕ Добавить пользователя"],
        ["⚙️ Настройки", "📊 Статистика"],
        ["ℹ️ Помощь", "🛠 Дополнительно"]
    ])


def get_cancel_keyboard() -> ReplyKeyboardMarkup:
    """Отмена действия (выход из состояния)"""
    return _create_keyboard([["❌ Отменить"]])
