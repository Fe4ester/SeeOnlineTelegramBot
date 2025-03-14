import io
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timezone
from matplotlib.patches import FancyBboxPatch


def time_to_float(time_obj):
    """Преобразуем объект time (часы, минуты, секунды) в число float (часы.десятичная_часть)."""
    return time_obj.hour + time_obj.minute / 60 + time_obj.second / 3600


def create_day_online_chart(day_statuses, chosen_day_str: str, username: str) -> io.BytesIO:
    """
    Рисует «расписание» онлайна за конкретный день (chosen_day_str)
    для пользователя (username) на основе списка day_statuses (список объектов).
    Возвращает BytesIO (PNG-картинка).
    """

    # Сортируем статусы по дате/времени
    day_statuses = sorted(day_statuses, key=lambda s: s.created_at)

    # Если статусов нет, возвращаем картинку с текстом «Нет данных»
    if not day_statuses:
        buf = io.BytesIO()
        plt.figure(figsize=(8, 2))
        plt.text(0.5, 0.5, "Нет данных за этот день", ha='center', va='center', fontsize=12)
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        return buf

    # Парсим дату дня (UTC, чтобы не было конфликтов со временем)
    day_dt = datetime.strptime(chosen_day_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    day_start = day_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Собираем интервалы (start, end, is_online).
    # Логика почти та же, что и раньше, но нам нужны лишь интервалы онлайн
    intervals = []
    current_state = day_statuses[0].is_online
    current_time = max(day_start, day_statuses[0].created_at)

    for i in range(1, len(day_statuses)):
        next_time = day_statuses[i].created_at
        if next_time > day_end:
            next_time = day_end
        intervals.append((current_time, next_time, current_state))
        current_state = day_statuses[i].is_online
        current_time = day_statuses[i].created_at
        if current_time > day_end:
            break

    # Закрываем «хвост» дня, если осталось время
    if current_time < day_end:
        intervals.append((current_time, day_end, current_state))

    # Теперь преобразуем интервалы, оставив только «онлайн» (is_online = True),
    # потому что для «онлайна» мы будем рисовать зелёные полосы
    online_periods = []
    for (start_dt, end_dt, is_online) in intervals:
        if is_online:
            # Переведём в локальные time-объекты (чтобы time_to_float сработал)
            # или просто берём время из UTC — не столь важно, так как на графике 0-24
            start_local_time = start_dt.replace(tzinfo=None).time()
            end_local_time = end_dt.replace(tzinfo=None).time()
            online_periods.append((start_local_time, end_local_time))

    # Формируем структуру «periods_by_day», где ключ – это день
    # (хотя здесь у нас только один день)
    periods_by_day = {chosen_day_str: online_periods}

    # *** Далее идёт отрисовка в стиле «новой» функции ***

    fig, ax = plt.subplots(figsize=(16, 4))

    # Общий интервал времени
    start_time = 0
    end_time = 24

    # Настройка фона
    fig.patch.set_facecolor('#f0f0f0')  # Светло-серый фон «всей» области
    ax.set_facecolor('#ffffff')  # Белый фон «основного» полотна

    # Красный полупрозрачный фон для "офлайна"
    ax.add_patch(
        FancyBboxPatch(
            (start_time, 0.3),
            end_time - start_time,
            0.3,
            boxstyle="round,pad=0.03",
            edgecolor='none',
            facecolor='#ff4c4c',
            alpha=0.7,
            zorder=1
        )
    )

    # Подсчитываем общее время «в сети»
    total_online_hours = 0.0
    for day_key, periods in periods_by_day.items():
        for (start_t, end_t) in periods:
            start_float = time_to_float(start_t)
            end_float = time_to_float(end_t)
            total_online_hours += (end_float - start_float)

            # Зелёные зоны «онлайн»
            ax.add_patch(
                FancyBboxPatch(
                    (start_float, 0.3),
                    end_float - start_float,
                    0.3,
                    boxstyle="round,pad=0.03",
                    edgecolor='none',
                    facecolor='#77DD77',
                    alpha=0.9,
                    zorder=2
                )
            )

    # Настройки осей
    ax.set_xlim(start_time, end_time)
    ax.set_ylim(0, 1)

    ax.yaxis.set_visible(False)

    ax.set_xticks(np.arange(0, 25, 1))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f'{int(val):02d}'))
    ax.set_xlabel("Время суток", color='#333333', fontsize=12, fontweight='bold')
    ax.tick_params(axis='x', colors='#333333', length=6)

    # Рисуем вертикальные линии
    ax.grid(False)
    for i in range(25):
        ax.axvline(x=i, color='#cccccc', linestyle='-', zorder=0, linewidth=0.7)

    # Скрываем рамки вокруг графика
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_color('#666666')

    # Вывод имени пользователя
    plt.text(-2, 1.2, username, color='#333333', fontsize=16, ha='left', va='center', fontweight='bold')

    # Вывод общего времени в сети
    total_hours_formatted = f"{int(total_online_hours)} ч {int((total_online_hours % 1) * 60)} мин"
    plt.text(
        12, 1.2,
        f"Общее время в сети: {total_hours_formatted}",
        color='#333333',
        fontsize=12,
        ha='center',
        va='center',
        fontweight='bold',
        bbox=dict(facecolor='#eeeeee', edgecolor='none', boxstyle='round,pad=0.5')
    )

    # Водяной знак
    plt.text(25.5, 1.2, 'SeeOnlineBot', color='#999999', fontsize=14, ha='right', va='center', alpha=0.6)

    # Дата
    formatted_date = day_dt.strftime("%d %b")
    plt.text(-2, -0.05, formatted_date, color='#555555', fontsize=10, ha='left', va='center')

    # Легенда
    ax.legend(
        ['Не в сети', 'В сети'],
        loc='upper center',
        bbox_to_anchor=(0.5, 1.2),
        ncol=2,
        fontsize=12,
        frameon=False,
        markerscale=1.2,
        labelspacing=1.5
    )

    # Сохраняем график в буфер байтов и возвращаем
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=fig.get_facecolor(), bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)

    return buf
