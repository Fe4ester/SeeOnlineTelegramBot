import io
import locale
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timezone
from matplotlib.patches import Rectangle, PathPatch, Patch
from matplotlib.path import Path
from typing import List, Any

# Устанавливаем локаль для корректного отображения месяца
try:
    locale.setlocale(locale.LC_TIME, 'ru_RU.UTF-8')
except locale.Error:
    locale.setlocale(locale.LC_TIME, 'en_US.UTF-8')

# Определяем цветовые палитры для тёмной и светлой тем
DARK_PALETTE = {
    "BG_COLOR": "#202a2e",         # Фон
    "AXES_COLOR": "#2c3539",       # Область графика
    "TEXT_COLOR": "#f0f0f0",       # Текст
    "AXES_EDGE_COLOR": "#888888",  # Края осей
    "GRID_COLOR": "#444444",       # Сетка
    "OFFLINE_COLOR": "#4f4f4f",    # Офлайн
    "ONLINE_COLOR": "#00b2b8",     # Онлайн
    "TEXT_BBOX_COLOR": "#2a3437",  # Фон под текстом
    "CAPSULE_EDGE_COLOR": "#444444"  # Края капсульной фигуры
}

LIGHT_PALETTE = {
    "BG_COLOR": "#ffffff",         # Фон
    "AXES_COLOR": "#f7f7f7",       # Область графика
    "TEXT_COLOR": "#333333",       # Текст
    "AXES_EDGE_COLOR": "#cccccc",  # Края осей
    "GRID_COLOR": "#e0e0e0",       # Сетка
    "OFFLINE_COLOR": "#d3d3d3",    # Офлайн
    "ONLINE_COLOR": "#4dd0e1",     # Онлайн
    "TEXT_BBOX_COLOR": "#f0f0f0",   # Фон под текстом
    "CAPSULE_EDGE_COLOR": "#cccccc"  # Края капсульной фигуры
}


def time_to_float(time_obj: datetime.time) -> float:
    """Преобразует объект time в десятичное число часов."""
    return time_obj.hour + time_obj.minute / 60 + time_obj.second / 3600


def create_capsule(x: float, y: float, width: float, height: float,
                   edgecolor: str, facecolor: str, linewidth: float) -> PathPatch:
    """
    Создаёт капсульную фигуру с закруглёнными концами для фона офлайна,
    используя NumPy для построения дуг.
    """
    R = height / 2.0
    # Правая дуга
    theta_right = np.linspace(-np.pi / 2, np.pi / 2, 30)
    right_arc = np.column_stack((x + width - R + R * np.cos(theta_right),
                                 y + R + R * np.sin(theta_right)))
    # Левая дуга
    theta_left = np.linspace(np.pi / 2, 3 * np.pi / 2, 30)
    left_arc = np.column_stack((x + R + R * np.cos(theta_left),
                                y + R + R * np.sin(theta_left)))
    # Объединяем вершины
    vertices = [(x + R, y), (x + width - R, y)]
    vertices.extend(right_arc.tolist())
    vertices.append((x + R, y + height))
    vertices.extend(left_arc.tolist())
    # Создаем коды пути
    codes = [Path.MOVETO] + [Path.LINETO] * (len(vertices) - 1)
    codes[-1] = Path.CLOSEPOLY
    return PathPatch(Path(vertices, codes),
                     edgecolor=edgecolor,
                     facecolor=facecolor,
                     lw=linewidth,
                     zorder=1,
                     alpha=1.0)


def _create_day_online_chart(day_statuses: List[Any], chosen_day_str: str, username: str, palette: dict) -> io.BytesIO:
    """
    Внутренняя функция, генерирующая график онлайна за выбранный день с использованием заданной палитры.
    """
    # Обновляем глобальные настройки matplotlib
    plt.rcParams.update({
        'font.family': 'sans-serif',
        'font.sans-serif': ['Helvetica', 'Arial', 'DejaVu Sans'],
        'text.color': palette["TEXT_COLOR"],
        'axes.labelcolor': palette["TEXT_COLOR"],
        'axes.edgecolor': palette["AXES_EDGE_COLOR"],
        'axes.titlecolor': palette["TEXT_COLOR"],
        'figure.facecolor': palette["BG_COLOR"],
        'axes.facecolor': palette["AXES_COLOR"],
        'grid.color': palette["GRID_COLOR"]
    })

    # Сортируем статусы по времени
    day_statuses = sorted(day_statuses, key=lambda s: s.created_at)
    if not day_statuses:
        buf = io.BytesIO()
        fig, ax = plt.subplots(figsize=(10, 2))
        fig.patch.set_facecolor(palette["BG_COLOR"])
        ax.set_facecolor(palette["AXES_COLOR"])
        ax.text(0.5, 0.5, "Нет данных за этот день",
                ha='center', va='center', fontsize=14)
        plt.axis("off")
        plt.savefig(buf, format='png', bbox_inches='tight')
        plt.close(fig)
        buf.seek(0)
        return buf

    # Парсинг выбранной даты (UTC)
    day_dt = datetime.strptime(chosen_day_str, "%Y-%m-%d").replace(tzinfo=timezone.utc)
    day_start = day_dt.replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_dt.replace(hour=23, minute=59, second=59, microsecond=999999)

    # Вычисляем интервалы состояний
    intervals = []
    current_state = day_statuses[0].is_online
    current_time = max(day_start, day_statuses[0].created_at)
    for status in day_statuses[1:]:
        next_time = min(status.created_at, day_end)
        intervals.append((current_time, next_time, current_state))
        current_state = status.is_online
        current_time = status.created_at
        if current_time >= day_end:
            break
    if current_time < day_end and not current_state:
        intervals.append((current_time, day_end, current_state))

    # Фильтруем онлайн-интервалы
    online_periods = [(start_dt.time(), end_dt.time())
                      for start_dt, end_dt, is_online in intervals if is_online and start_dt < end_dt]

    # Создаем график
    fig, ax = plt.subplots(figsize=(16, 4))
    fig.patch.set_facecolor(palette["BG_COLOR"])
    ax.set_facecolor(palette["AXES_COLOR"])

    # Добавляем фон в виде капсульной фигуры
    capsule_patch = create_capsule(
        x=0, y=0.25, width=24, height=0.4,
        edgecolor=palette["CAPSULE_EDGE_COLOR"],
        facecolor=palette["OFFLINE_COLOR"],
        linewidth=1.5
    )
    ax.add_patch(capsule_patch)

    # Рисуем онлайн-интервалы и суммируем общее время
    total_online = 0.0
    for start, end in online_periods:
        start_f, end_f = time_to_float(start), time_to_float(end)
        total_online += (end_f - start_f)
        ax.add_patch(Rectangle(
            (start_f, 0.25),
            end_f - start_f,
            0.4,
            facecolor=palette["ONLINE_COLOR"],
            edgecolor=None,
            zorder=2
        ))

    # Настройка осей
    ax.set_xlim(0, 24)
    ax.set_ylim(0, 1)
    ax.yaxis.set_visible(False)
    ax.set_xticks(np.arange(0, 25, 1))
    ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda val, pos: f'{int(val):02d}'))
    ax.tick_params(axis='x', colors=palette["TEXT_COLOR"], length=6)
    ax.grid(axis='x', linestyle='--', linewidth=0.5, alpha=0.6)

    for spine in ["top", "right", "left"]:
        ax.spines[spine].set_visible(False)
    ax.spines["bottom"].set_color(palette["AXES_EDGE_COLOR"])

    # Форматирование даты (например, "15 Март")
    formatted_date = day_dt.strftime("%d %B")

    # Подписи
    ax.text(0.02, 0.95, username,
            transform=ax.transAxes,
            fontsize=16,
            ha='left', va='top',
            fontweight='bold')
    hours, minutes = divmod(round(total_online * 60), 60)
    ax.text(0.98, 0.95, f"В сети: {hours} ч {minutes} мин",
            transform=ax.transAxes,
            fontsize=12,
            ha='right', va='top',
            fontweight='medium',
            bbox=dict(facecolor=palette["TEXT_BBOX_COLOR"], edgecolor='none', boxstyle='round,pad=0.3'))
    ax.text(0.02, 0.02, formatted_date,
            transform=ax.transAxes,
            fontsize=14,
            ha='left', va='bottom')
    ax.text(0.98, 0.02, "SeeOnline",
            transform=ax.transAxes,
            fontsize=14,
            ha='right', va='bottom',
            alpha=0.7)

    # Легенда
    legend_elements = [
        Patch(facecolor=palette["OFFLINE_COLOR"], edgecolor='none', label='Не в сети'),
        Patch(facecolor=palette["ONLINE_COLOR"], edgecolor='none', label='В сети')
    ]
    ax.legend(handles=legend_elements,
              loc='upper center',
              bbox_to_anchor=(0.5, 0.88),
              ncol=2,
              fontsize=12,
              frameon=False)

    # Сохраняем график в буфер
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight')
    plt.close(fig)
    buf.seek(0)
    return buf


def create_day_online_chart_dark(day_statuses: List[Any], chosen_day_str: str, username: str) -> io.BytesIO:
    """
    Построение графика онлайна за день в тёмной теме.
    """
    return _create_day_online_chart(day_statuses, chosen_day_str, username, DARK_PALETTE)


def create_day_online_chart_light(day_statuses: List[Any], chosen_day_str: str, username: str) -> io.BytesIO:
    """
    Построение графика онлайна за день в светлой теме.
    """
    return _create_day_online_chart(day_statuses, chosen_day_str, username, LIGHT_PALETTE)
