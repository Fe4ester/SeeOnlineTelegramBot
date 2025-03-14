from aiogram import Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from src.bot.states.tracked_users_menu_states import DeleteTrackedUserStates
from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError
from src.config.settings import settings
from src.bot.keyboards.inline import get_tracked_users_menu_keyboard, back_keyboard
from src.bot.states.tracked_users_menu_states import GetDiagramStates
from src.services.build_answer_services import (
    build_tracked_users_menu_text,
    group_statuses_by_day,
    build_day_list_text,
    build_online_intervals_text
)

# Тексты
from src.bot.answers.menu_answers import (
    USER_NUMBER_NOT_DIGIT_ANSWER,
    DELETE_USER_NOT_FOUND_TEMPLATE,
    DELETE_USER_FAILED_TEMPLATE,
    DELETE_USER_SUCCESS_TEMPLATE,
    UNAVAILABLE_ANSWER,
    NO_TRACKING_DATA
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
    """Пользователь присылает номер отслеживаемого аккаунта для 'диаграммы'."""
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

    user_to_show = tracked_users[index - 1]  # 0-based
    tu_id = user_to_show.id

    # Получаем все статусы из API
    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            statuses = await api.get_online_status(tracked_user=tu_id)
        except SeeOnlineAPIError:
            await message.answer(UNAVAILABLE_ANSWER)
            return

    # Группируем по дням
    statuses_by_day = group_statuses_by_day(statuses)
    # Вытащим список дней (ключи словаря)
    days = sorted(statuses_by_day.keys())

    # Сохраним в FSM и имя пользователя тоже, если нужно
    await state.update_data(selected_tracked_user=user_to_show, statuses_by_day=statuses_by_day, days=days)

    # Покажем список дат
    day_list_text = build_day_list_text(days)
    await message.answer(
        text=day_list_text,
        parse_mode="HTML",
        reply_markup=back_keyboard()
    )

    if days:
        # Переходим к состоянию ожидания номера дня
        await state.set_state(GetDiagramStates.waiting_for_day_number)
    else:
        await message.answer(NO_TRACKING_DATA)

        new_text = await build_tracked_users_menu_text(message.from_user.id)
        await message.answer(
            text=new_text,
            parse_mode="HTML",
            reply_markup=get_tracked_users_menu_keyboard()
        )
        await state.clear()


@router.message(GetDiagramStates.waiting_for_day_number)
async def process_get_user_diagram_day(message: Message, state: FSMContext):
    """Пользователь выбирает дату, по которой хочет получить интервалы."""
    user_input = message.text.strip()
    if not user_input.isdigit():
        # Можно использовать ту же константу или завести отдельную
        await message.answer(USER_NUMBER_NOT_DIGIT_ANSWER, parse_mode="HTML")
        return

    index = int(user_input)

    data = await state.get_data()
    days = data.get("days", [])
    statuses_by_day = data.get("statuses_by_day", {})
    user_to_show = data.get("selected_tracked_user")

    if index < 1 or index > len(days):
        await message.answer(
            DELETE_USER_NOT_FOUND_TEMPLATE.format(index=index)
        )
        return

    chosen_day = days[index - 1]
    day_statuses = statuses_by_day[chosen_day]

    intervals_text = build_online_intervals_text(day_statuses)

    username = user_to_show.username if user_to_show else "???"
    header = f"<b>Статистика онлайна @{username} за {chosen_day}</b>\n\n"

    await message.answer(
        header + intervals_text,
        parse_mode="HTML"
    )

    new_text = await build_tracked_users_menu_text(message.from_user.id)
    await message.answer(
        text=new_text,
        parse_mode="HTML",
        reply_markup=get_tracked_users_menu_keyboard()
    )

    await state.clear()
