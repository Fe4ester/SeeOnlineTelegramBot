from aiogram import Router, F
from aiogram.types import CallbackQuery, BufferedInputFile

from src.services.tracker_service_client import SeeOnlineAPI, SeeOnlineAPIError
from src.config.settings import settings

from src.bot.keyboards.inline import (
    get_tracked_users_menu_keyboard,
    build_delete_user_keyboard,
    build_delete_confirmation_keyboard,
    build_diagram_users_keyboard,
    build_diagram_days_keyboard,
)

from src.services.build_answer_services import (
    build_tracked_users_menu_text,
    group_statuses_by_day
)
from src.services.build_chart_service import create_day_online_chart

# Тексты
from src.bot.answers.menu_answers import (
    UNAVAILABLE_ANSWER,
    NO_TRACKED_USERS_MESSAGE,
    DELETE_USER_FAILED_TEMPLATE,
    DELETE_USER_SUCCESS_TEMPLATE,
    NO_TRACKING_DATA,
    DELETE_SELECT_USER_PROMPT,
    INVALID_DATA_FORMAT,
    USER_NOT_FOUND,
    CONFIRM_DELETE_USER_TEMPLATE,
    SELECT_USER_FOR_CHART,
    SELECT_DAY,
    CHART_CAPTION_TEMPLATE
)

router = Router()


@router.callback_query(F.data == "delete_tracked_user")
async def delete_tracked_user_callback(callback: CallbackQuery):
    """Показать список пользователей для удаления (кнопки «Удалить @username»)."""
    user_id = callback.from_user.id

    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            tracked_users = await api.get_tracked_user(telegram_user_id=user_id)
        except SeeOnlineAPIError:
            await callback.answer(text=UNAVAILABLE_ANSWER, show_alert=True)
            return

    if not tracked_users:
        await callback.answer(text=NO_TRACKED_USERS_MESSAGE, show_alert=True)
        return

    kb = build_delete_user_keyboard(tracked_users)
    await callback.message.edit_text(
        text=DELETE_SELECT_USER_PROMPT,
        reply_markup=kb,
        parse_mode='html'
    )
    await callback.answer()


@router.callback_query(F.data.startswith("delete_user:"))
async def ask_delete_user_callback(callback: CallbackQuery):
    """
    Пользователь выбрал «Удалить @username», но мы делаем ДОП. подтверждение.
    Формат callback_data: "delete_user:{tracked_user_id}"
    """
    data = callback.data.split(":")
    if len(data) != 2:
        await callback.answer(INVALID_DATA_FORMAT, show_alert=True)
        return

    tracked_user_id = data[1]

    # Пытаемся получить юзернейм, чтобы в сообщении отобразить "Точно удалить @username?"
    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            tu = await api.get_tracked_user(pk=int(tracked_user_id))
            if not tu:
                await callback.answer(USER_NOT_FOUND, show_alert=True)
                return
        except SeeOnlineAPIError:
            await callback.answer(UNAVAILABLE_ANSWER, show_alert=True)
            return

    username = tu.username
    kb = build_delete_confirmation_keyboard(int(tracked_user_id))
    await callback.message.edit_text(
        text=CONFIRM_DELETE_USER_TEMPLATE.format(username=username),
        reply_markup=kb,
        parse_mode='html'
    )
    await callback.answer()


@router.callback_query(F.data.startswith("confirm_delete_user:"))
async def confirm_delete_user_callback(callback: CallbackQuery):
    """
    «Да, удалить» – делаем запрос на удаление.
    Формат: "confirm_delete_user:{tracked_user_id}"
    """
    data = callback.data.split(":")
    if len(data) != 2:
        await callback.answer(INVALID_DATA_FORMAT, show_alert=True)
        return

    tracked_user_id = data[1]
    user_id = callback.from_user.id

    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        # Снова достаём юзернейм, чтоб написать кто удалён
        try:
            tu = await api.get_tracked_user(pk=int(tracked_user_id))
            if not tu:
                await callback.answer(USER_NOT_FOUND, show_alert=True)
                return

            username = tu.username
            try:
                await api.delete_tracked_user(pk=int(tracked_user_id))
            except SeeOnlineAPIError:
                await callback.answer(DELETE_USER_FAILED_TEMPLATE.format(username=username), show_alert=True)
                return
        except SeeOnlineAPIError:
            await callback.answer(UNAVAILABLE_ANSWER, show_alert=True)
            return

    # Успешно удалили
    await callback.message.edit_text(
        text=DELETE_USER_SUCCESS_TEMPLATE.format(username=username)
    )
    # Обновим меню
    new_text = await build_tracked_users_menu_text(user_id)
    await callback.message.answer(
        text=new_text,
        reply_markup=get_tracked_users_menu_keyboard(),
        parse_mode='html'
    )
    await callback.answer()


@router.callback_query(F.data.startswith("cancel_delete_user:"))
async def cancel_delete_user_callback(callback: CallbackQuery):
    """
    «Нет, не удаляем» – просто возвращаемся в меню.
    Формат: "cancel_delete_user:{tracked_user_id}"
    """
    user_id = callback.from_user.id

    # Можно сразу показать меню без лишних проверок
    new_text = await build_tracked_users_menu_text(user_id)
    await callback.message.edit_text(
        text=new_text,
        reply_markup=get_tracked_users_menu_keyboard(),
        parse_mode='html'
    )
    await callback.answer()


@router.callback_query(F.data == "get_tracked_user_diagram")
async def get_tracked_user_diagram_callback(callback: CallbackQuery):
    """Показать список пользователей, по которым можно получить график."""
    user_id = callback.from_user.id

    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            tracked_users = await api.get_tracked_user(telegram_user_id=user_id)
        except SeeOnlineAPIError:
            await callback.answer(text=UNAVAILABLE_ANSWER, show_alert=True)
            return

    if not tracked_users:
        await callback.answer(text=NO_TRACKED_USERS_MESSAGE, show_alert=True)
        return

    # Делаем кнопки "График @username"
    kb = build_diagram_users_keyboard(tracked_users)

    await callback.message.edit_text(
        text=SELECT_USER_FOR_CHART,
        reply_markup=kb,
        parse_mode='html'
    )
    await callback.answer()


@router.callback_query(F.data.startswith("diagram_user:"))
async def choose_day_for_diagram(callback: CallbackQuery):
    """
    Получаем список дней для выбранного пользователя,
    показываем их в виде inline-кнопок.
    """
    data = callback.data.split(":")
    if len(data) != 2:
        await callback.answer(INVALID_DATA_FORMAT, show_alert=True)
        return

    tracked_user_id = data[1]
    user_id = callback.from_user.id

    # Обращаемся к API за всеми статусами этого пользователя
    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            statuses = await api.get_online_status(tracked_user=int(tracked_user_id))
        except SeeOnlineAPIError:
            await callback.answer(UNAVAILABLE_ANSWER, show_alert=True)
            return

        # Группируем
        statuses_by_day = group_statuses_by_day(statuses)
        days = sorted(statuses_by_day.keys())

        if not days:
            await callback.message.edit_text(NO_TRACKING_DATA)
            # Показать меню ещё раз
            new_text = await build_tracked_users_menu_text(user_id)
            await callback.message.answer(
                text=new_text,
                reply_markup=get_tracked_users_menu_keyboard(),
                parse_mode='html'
            )
            await callback.answer()
            return

        # Строим инлайн-кнопки по дням
        kb = build_diagram_days_keyboard(int(tracked_user_id), days)
        await callback.message.edit_text(
            text=SELECT_DAY,
            reply_markup=kb,
            parse_mode='html'
        )
    await callback.answer()


@router.callback_query(F.data.startswith("diagram_day:"))
async def get_diagram_for_day(callback: CallbackQuery):
    """
    Пользователь выбрал конкретный день. Генерируем график и отправляем.
    Формат callback_data: "diagram_day:{tracked_user_id}:{YYYY-MM-DD}"
    """
    data = callback.data.split(":")
    if len(data) != 3:
        await callback.answer(INVALID_DATA_FORMAT, show_alert=True)
        return

    _, user_id_str, day_str = data
    tg_user_id = callback.from_user.id

    # Идём в API за этим tracked_user, чтобы узнать его username
    # и достать статусы только за нужный день (при желании).
    async with SeeOnlineAPI(base_url=settings.EXTERNAL_SERVICE_API_URL) as api:
        try:
            tu = await api.get_tracked_user(pk=int(user_id_str))
            if not tu:
                await callback.answer(USER_NOT_FOUND, show_alert=True)
                return
            statuses = await api.get_online_status(
                tracked_user=int(user_id_str),
                created_at_after=f"{day_str} 00:00:00",
                created_at_before=f"{day_str} 23:59:59"
            )
        except SeeOnlineAPIError:
            await callback.answer(UNAVAILABLE_ANSWER, show_alert=True)
            return

    if not statuses:
        # Нет данных
        await callback.message.edit_text(NO_TRACKING_DATA)
        # Покажем меню
        new_text = await build_tracked_users_menu_text(tg_user_id)
        await callback.message.answer(
            text=new_text,
            reply_markup=get_tracked_users_menu_keyboard(),
            parse_mode='html'
        )
        await callback.answer()
        return

    # Генерируем картинку
    chart_buf = create_day_online_chart(
        day_statuses=statuses,
        chosen_day_str=day_str,
        username=tu.username
    )
    photo_file = BufferedInputFile(chart_buf.getvalue(), filename="chart.png")

    # Отправляем фото
    await callback.message.answer_photo(
        photo=photo_file,
        caption=CHART_CAPTION_TEMPLATE.format(username=tu.username, day_str=day_str)
    )

    # Показываем меню отслеживаемых
    new_text = await build_tracked_users_menu_text(tg_user_id)
    await callback.message.answer(
        text=new_text,
        reply_markup=get_tracked_users_menu_keyboard(),
        parse_mode='html'
    )

    await callback.answer()
