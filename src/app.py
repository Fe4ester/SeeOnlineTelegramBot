# Базовые импорты для бота
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

# Настройки
from src.config.settings import settings

# Хэндлеры
from src.bot.handlers.system import start, help
from src.bot.handlers.admin import admin
from src.bot.handlers.main_keyboard import additional_button, my_tracking_button, add_user_button
from src.bot.handlers.additional_keyboard import settings_button, statistics_button, help_button, back_button

# Мидлвари
from src.bot.middlewares.whitelist_middleware import WhitelistMiddleware


def create_bot_and_dispatcher():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация хэндлеров(через роутеры)
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(admin.router)
    dp.include_router(additional_button.router)
    dp.include_router(my_tracking_button.router)
    dp.include_router(add_user_button.router)
    dp.include_router(settings_button.router)
    dp.include_router(statistics_button.router)
    dp.include_router(help_button.router)
    dp.include_router(back_button.router)

    # Мидлвари
    whitelist_middleware = WhitelistMiddleware(settings.BOT_WHITELIST)

    # Регистрация мидлварей
    dp.update.middleware(whitelist_middleware)
    dp.message.middleware(whitelist_middleware)
    dp.callback_query.middleware(whitelist_middleware)

    return bot, dp


# Установка команд, можно в BotFather
async def set_bot_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/help", description="Дополнительная информация"),
        BotCommand(command="/admin", description="Администрирование"),
    ]
    await bot.set_my_commands(commands)
