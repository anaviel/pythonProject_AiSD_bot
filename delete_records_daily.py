import asyncio
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from threading import Thread
from database_editing import Classes

engine = create_engine('sqlite:///rasp.db', echo=False)
Session = sessionmaker(bind=engine)


# Функция для удаления записей, которые были три недели назад
async def delete_records_daily():
    session = Session()

    three_weeks_ago = datetime.now() - timedelta(weeks=4)
    target_date = three_weeks_ago.date()

    # Удаление записей с заданной датой
    session.query(Classes).filter(Classes.date == target_date).delete()
    session.commit()

    session.close()


# Функция для запуска задачи удаления записей каждый день в 23:00
async def schedule_daily_task():
    while True:
        now = datetime.now()
        target_time = now.replace(hour=23, minute=0, second=0, microsecond=0)

        # Если текущее время больше или равно заданному времени, запускается удаление записей
        if now >= target_time:
            await delete_records_daily()

            # Ожидание до следующего дня
            await asyncio.sleep(86395)  # 86400 секунд в одном дне


# Функция для запуска цикла событий asyncio в отдельном потоке
def run_asyncio_loop():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(schedule_daily_task())


# Запуск цикла событий asyncio в отдельном потоке
thread = Thread(target=run_asyncio_loop)
thread.start()