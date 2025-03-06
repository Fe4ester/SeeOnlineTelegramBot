from aiogram import Router
from aiogram.types import Message
from aiogram import F

# Тексты
from src.bot.texts.system_texts import get_menu_text

# Клавиатуры
from src.bot.keyboards.inline import get_menu_inline_keyboard

router = Router()


@router.message(F.text == 'Меню')
async def menu_button(message: Message):
    await message.answer(
        await get_menu_text(message),
        parse_mode='HTML',
        reply_markup=get_menu_inline_keyboard()
    )
