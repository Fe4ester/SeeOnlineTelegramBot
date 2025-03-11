from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.bot.states.tracked_users_menu_states import DeleteTrackedUserStates
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError
from src.config.settings import settings

from src.bot.keyboards.inline import get_tracked_users_menu_keyboard
from src.bot.answers.menu_answers import (
    get_tracked_users_menu_text
)

router = Router()


@router.message(DeleteTrackedUserStates.waiting_for_user_number)
async def process_delete_user_number(message: Message, state: FSMContext):
    user_input = message.text.strip()

    # Пытаемся преобразовать введённое значение в int
    if not user_input.isdigit():
        await message.answer(
            "Пожалуйста, введите <b>числовой</b> номер пользователя (или нажмите Назад).",
            parse_mode="HTML"
        )
        return

    index = int(user_input)

    # Достаём из FSM сохранённый список
    data = await state.get_data()
    tracked_users = data.get("tracked_users", [])

    # Проверяем, что номер в валидном диапазоне
    if index < 1 or index > len(tracked_users):
        await message.answer(
            f"Нет пользователя с номером {index}. Попробуйте снова или нажмите Назад."
        )
        return

    # Получаем пользователя, соответствующего этому номеру
    user_to_delete = tracked_users[index - 1]  # т.к. нумерация с 1
    username = user_to_delete.username
    pk = user_to_delete.id  # предположим, что поле id - это PK (или используйте нужное поле)

    # Пытаемся удалить
    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            await api.delete_tracked_user(pk=pk)
        except SeeOnlineAPIError:
            # Если произошла ошибка на сервере
            await message.answer(
                f"Не удалось удалить @{username}. Попробуйте позже."
            )
            return

    # Говорим пользователю, что удаление успешно
    await message.answer(
        f"Пользователь @{username} успешно удалён из списка!"
    )
    await message.answer(
        text=await get_tracked_users_menu_text(message.from_user.id),
        parse_mode="HTML",
        reply_markup=get_tracked_users_menu_keyboard()
    )

    # Сбросим состояние – вернёмся в «обычное» состояние без ожидания данных
    await state.clear()
