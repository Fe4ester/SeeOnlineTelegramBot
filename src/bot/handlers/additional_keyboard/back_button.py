from aiogram import Router
from aiogram.types import Message
from aiogram import F

# Тексты
from src.bot.texts.additional_keyboard_texts import back_text

# Клавиатуры
from src.bot.keyboards.reply import get_menu_reply_keyboard

router = Router()


@router.message(F.text == '↩️ Назад')
async def back_button(message: Message):
    await message.answer(
        back_text,
        parse_mode='HTML',
        reply_markup=get_menu_reply_keyboard()
    )
