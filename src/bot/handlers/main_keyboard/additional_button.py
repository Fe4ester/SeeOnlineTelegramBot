from aiogram import Router
from aiogram.types import Message
from aiogram import F

# Тексты
from src.bot.texts.main_keyboard_texts import additional_text

# Клавиатуры
from src.bot.keyboards.reply import get_additional_keyboard

router = Router()


@router.message(F.text == '🛠 Дополнительно')
async def additional_button(message: Message):
    await message.answer(
        additional_text,
        parse_mode='HTML',
        reply_markup=get_additional_keyboard()
    )
