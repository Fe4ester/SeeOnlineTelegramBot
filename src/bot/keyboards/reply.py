from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


def _create_keyboard(buttons: list[list[str]], resize: bool = True) -> ReplyKeyboardMarkup:
    """Генератор клавиатуры, подходит для всех reply"""
    kb_builder = ReplyKeyboardBuilder()
    for row in buttons:
        kb_builder.row(*[KeyboardButton(text=btn) for btn in row])
    return kb_builder.as_markup(resize_keyboard=resize)

# Пусто потому что не нужно, но на всякий случай, может в будущем будут создаваться клавиатуры
