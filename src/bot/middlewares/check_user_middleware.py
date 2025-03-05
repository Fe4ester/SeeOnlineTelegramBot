from aiogram import BaseMiddleware
from aiogram.types import Message
from typing import Any, Awaitable, Callable, Dict

from src.services.external_service_client import SeeOnlineAPI


class CheckOrCreateUserMiddleware(BaseMiddleware):
    def __init__(self, base_external_api_url: str):
        super().__init__()
        self.base_external_api_url = base_external_api_url

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        """
        Проверяем/создаём пользователя и добавляем ему role в data
        """

        tg_id = event.from_user.id

        # Получаем пользователя из API
        async with SeeOnlineAPI(self.base_external_api_url) as api:
            user = await api.get_telegram_user(telegram_id=tg_id)

            # Проверяем, если вернулся список — берём первый элемент
            if isinstance(user, list):
                user = user[0] if user else None

            # Если пользователь не найден — создаём
            if not user:
                await api.create_telegram_user(
                    {"telegram_id": tg_id, "role": "user"}  # Здесь можно задать логику определения роли
                )

        # Передаём управление дальше
        return await handler(event, data)
