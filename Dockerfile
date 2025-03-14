# Используем минимальный образ Python
FROM python:3.12

# Устанавливаем рабочую директорию внутри контейнера
WORKDIR /app

# Копируем файлы с кодом и зависимостями
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Определяем переменные окружения (если нужно)
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Запускаем бота
CMD ["python3", "src/main.py"]
