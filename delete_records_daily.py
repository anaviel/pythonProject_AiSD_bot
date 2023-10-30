import asyncio
from threading import Thread
from datetime import datetime
import sqlite3

database = sqlite3.connect('rasp.db', check_same_thread=False)
cursor = database.cursor()

# Функция для удаления записей с текущей датой
async def delete_records_daily():
    current_date = datetime.now().date().strftime("%d-%m-%Y")
    # Удаление записей с текущей датой
    cursor.execute(f"DELETE FROM classes WHERE date = '{current_date}'")
    database.commit()

# Функция для запуска задачи удаления записей каждый день в 23:00
async def schedule_daily_task():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=23, minute=0, second=0, microsecond=0)

        # Если текущее время больше или равно заданному времени, запускается удаление записей
        if now >= target_time:
            await delete_records_daily()

            # Ожидание до следующего дня
            await asyncio.sleep(86400)  # 86400 секунд в одном дне

# Функция для запуска цикла событий asyncio в отдельном потоке
def run_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(schedule_daily_task())

# Запуск цикла событий asyncio в отдельном потоке
thread = Thread(target=run_asyncio_loop)
thread.start()