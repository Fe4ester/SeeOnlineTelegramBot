from aiogram import Router
from aiogram.types import Message
from aiogram.filters import Command

# Тексты
from src.bot.texts.system_texts import start_text, main_text

# Клавиатуры
from src.bot.keyboards.reply import get_main_keyboard

# Настройки
from src.config.settings import settings

# Сервисы
from src.services.external_service_client import SeeOnlineAPI

router = Router()


@router.message(Command('start'))
async def cmd_start(message: Message):
    await message.answer(
        start_text,
        parse_mode='HTML'
    )
    async with SeeOnlineAPI(settings.EXTERNAL_SERVICE_API_URL) as api:
        user = await api.get_telegram_user(telegram_id=message.from_user.id)
        tracked_users = await api.get_tracked_user(telegram_user_id=message.from_user.id)

        # Формируем красивый список отслеживаемых пользователей
        tracked_users_list = "\n".join(
            [f"👤 @{tracked_user.username}"
             for tracked_user in tracked_users]
        )

        if not tracked_users_list:  # Если список пуст, добавляем заглушку
            tracked_users_list = "❌ Вы пока никого не отслеживаете"

        role = user[0].role
        available_cells = f'{user[0].max_users - user[0].current_users}/{user[0].max_users}'

        await message.answer(
            main_text.format(tracked_users_list, available_cells, role),
            parse_mode='HTML',
            reply_markup=get_main_keyboard()
        )
