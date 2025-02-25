from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable


class WhitelistMiddleware(BaseMiddleware):
    def __init__(self, allowed_users: list[int]):
        super().__init__()
        self.allowed_users = allowed_users

    async def __call__(
            self,
            handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
            event: TelegramObject,
            data: Dict[str, Any]
    ) -> Any:
        user_id = None

        if isinstance(event, Message):
            user_id = event.from_user.id
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id

        if user_id and user_id not in self.allowed_users:
            return

        return await handler(event, data)
