import asyncio

# Функции настроек бота
from src.app import create_bot_and_dispatcher, set_bot_commands


async def main():
    bot, dp = create_bot_and_dispatcher()

    await set_bot_commands(bot)

    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
