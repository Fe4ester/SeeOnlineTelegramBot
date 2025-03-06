# Базовые импорты для бота
from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand

# Настройки
from src.config.settings import settings

# Хэндлеры
from src.bot.handlers.system import start, help, main_menu
from src.bot.handlers.admin import admin

# Каллбеки
from src.bot.handlers.main_menu_callbacks import add_tracked_user

# Мидлвари
from src.bot.middlewares.whitelist_middleware import WhitelistMiddleware
from src.bot.middlewares.check_user_middleware import CheckOrCreateUserMiddleware


def create_bot_and_dispatcher():
    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher()

    # Регистрация хэндлеров

    ## system
    dp.include_router(start.router)
    dp.include_router(help.router)
    dp.include_router(admin.router)
    dp.include_router(main_menu.router)

    # Регистрация каллбеков
    dp.include_router(add_tracked_user.router)

    # Мидлвари
    whitelist_middleware = WhitelistMiddleware(settings.BOT_WHITELIST)
    check_user_middleware = CheckOrCreateUserMiddleware(settings.EXTERNAL_SERVICE_API_URL)

    # Регистрация мидлварей
    # Проверка или создание пользователя
    dp.message.middleware(check_user_middleware)
    dp.callback_query.middleware(check_user_middleware)

    # Вайтлист
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
