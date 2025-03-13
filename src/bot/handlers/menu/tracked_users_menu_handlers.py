from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.bot.states.tracked_users_menu_states import DeleteTrackedUserStates
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError
from src.config.settings import settings
from src.bot.keyboards.inline import get_tracked_users_menu_keyboard
from src.bot.states.tracked_users_menu_states import GetDiagramStates
from src.services.build_answer_services import build_tracked_users_menu_text, build_online_intervals_text

# Тексты
from src.bot.answers.menu_answers import (
    USER_NUMBER_NOT_DIGIT_ANSWER,
    DELETE_USER_NOT_FOUND_TEMPLATE,
    DELETE_USER_FAILED_TEMPLATE,
    DELETE_USER_SUCCESS_TEMPLATE,
    UNAVAILABLE_ANSWER
)

router = Router()


@router.message(DeleteTrackedUserStates.waiting_for_user_number)
async def process_delete_user_number(message: Message, state: FSMContext):
    """Обработка удаления пользователя по выбранному номеру."""
    user_input = message.text.strip()
    if not user_input.isdigit():
        await message.answer(USER_NUMBER_NOT_DIGIT_ANSWER, parse_mode="HTML")
        return

    index = int(user_input)

    data = await state.get_data()
    tracked_users = data.get("tracked_users", [])

    if index < 1 or index > len(tracked_users):
        await message.answer(
            DELETE_USER_NOT_FOUND_TEMPLATE.format(index=index)
        )
        return

    user_to_delete = tracked_users[index - 1]
    username = user_to_delete.username
    pk = user_to_delete.id

    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            await api.delete_tracked_user(pk=pk)
        except SeeOnlineAPIError:
            await message.answer(DELETE_USER_FAILED_TEMPLATE.format(username=username))
            return

    # Сообщаем, что пользователь успешно удалён
    await message.answer(DELETE_USER_SUCCESS_TEMPLATE.format(username=username))

    # Показываем обновлённое меню
    new_text = await build_tracked_users_menu_text(message.from_user.id)
    await message.answer(
        text=new_text,
        parse_mode="HTML",
        reply_markup=get_tracked_users_menu_keyboard()
    )

    await state.clear()


@router.message(GetDiagramStates.waiting_for_user_number)
async def process_get_user_diagram_number(message: Message, state: FSMContext):
    """Обрабатываем ввод номера пользователя для показа «диаграммы» (интервалов)."""
    user_input = message.text.strip()
    if not user_input.isdigit():
        await message.answer(USER_NUMBER_NOT_DIGIT_ANSWER, parse_mode="HTML")
        return

    index = int(user_input)

    data = await state.get_data()
    tracked_users = data.get("tracked_users", [])

    if index < 1 or index > len(tracked_users):
        await message.answer(
            DELETE_USER_NOT_FOUND_TEMPLATE.format(index=index)
        )
        return

    # Находим нужного TrackedUser
    user_to_show = tracked_users[index - 1]  # 0-based
    tu_id = user_to_show.id
    username = user_to_show.username

    # Идём в API, получаем OnlineStatus для этого tracked_user
    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            # Допустим, наше API умеет искать статусы по tracked_user=<id>
            statuses = await api.get_online_status(tracked_user=tu_id)
        except SeeOnlineAPIError:
            await message.answer(UNAVAILABLE_ANSWER)
            return

    # Преобразуем список статусов в интервалы
    intervals_text = build_online_intervals_text(statuses)

    # Отправляем пользователю результат
    header = f"<b>Статистика онлайна @{username}</b>\n\n"
    await message.answer(
        header + intervals_text,
        parse_mode="HTML"
    )

    # После этого возвращаем в меню отслеживаемых пользователей
    new_text = await build_tracked_users_menu_text(message.from_user.id)
    await message.answer(
        text=new_text,
        parse_mode="HTML",
        reply_markup=get_tracked_users_menu_keyboard()
    )

    await state.clear()
