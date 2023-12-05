import sqlite3
from telebot import types
from bot_start import bot

database = sqlite3.connect('rasp.db', check_same_thread=False)
cursor = database.cursor()


# функция, которая вызывается при нажатии админом на кнопку "Редактировать расписание"
def edit_rasp(message):
    cursor.execute("SELECT * FROM classes")
    markup_edit_rasp = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Удалить занятие', callback_data='delete_a_training')
    button2 = types.InlineKeyboardButton('Заменить занятие', callback_data='replace_a_training')
    markup_edit_rasp.add(button1, button2)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup_edit_rasp)


# Словарь для хранения текущей страницы
pages_delete = {}


@bot.callback_query_handler(func=lambda callback: 'delete_a_training' in callback.data)
def callback_delete_a_training(callback):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    # Получение всех дат и направлений занятий
    cursor.execute("SELECT date, napr FROM classes")
    data = cursor.fetchall()

    # Создание списка дат
    dates = []
    for row in data:
        if row[0] not in dates:
            dates.append(row[0])

    # Получение текущей страницы пользователя
    current_page = pages_delete.get(callback.from_user.id, 0)

    # Количество элементов на одной странице
    items_per_page = 5
    start_index = current_page * items_per_page
    end_index = start_index + items_per_page

    # Формирование клавиатуры с датами на текущей странице
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for date in dates[start_index:end_index]:
        button = types.InlineKeyboardButton(text=date, callback_data='delete_date_' + date)
        keyboard.add(button)

    # Добавление кнопок "Вперёд" и "Назад"
    if current_page > 0:
        prev_button = types.InlineKeyboardButton(text='Назад', callback_data='prev_page_1')
        keyboard.row(prev_button)
    if end_index < len(dates):
        next_button = types.InlineKeyboardButton(text='Вперёд', callback_data='next_page_1')
        keyboard.row(next_button)

    # Отправка сообщения с выбором даты
    bot.send_message(callback.message.chat.id, "Выберете дату, на которую хотели бы отменить занятие:",
                     reply_markup=keyboard)


# Обработка нажатий кнопок "Вперёд" и "Назад"
@bot.callback_query_handler(func=lambda callback: callback.data in ['prev_page_1', 'next_page_1'])
def callback_pagination(callback):
    user_id = callback.from_user.id
    current_page = pages_delete.get(user_id, 0)

    if callback.data == 'prev_page':
        current_page = max(0, current_page - 1)
    elif callback.data == 'next_page':
        current_page += 1

    pages_delete[user_id] = current_page

    # Вызов функции, которая формирует и отправляет клавиатуру
    callback_delete_a_training(callback)


@bot.callback_query_handler(func=lambda callback: 'delete_date_' in callback.data)
def callback_delete_class_date(callback):
    date = callback.data.split('_')[2]
    # получение направления
    cursor.execute("SELECT napr FROM classes WHERE date=?", (date,))
    data = cursor.fetchall()

    # создание клавиатуры с направлениями
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for row in data:
        if row[0] not in buttons:
            buttons.append(row[0])
            button = types.InlineKeyboardButton(text=row[0], callback_data='delete_napr_' + date + '_' + row[0])
            keyboard.add(button)

    # отправка сообщения с выбором направления
    bot.send_message(callback.message.chat.id, "Какое направление вы хотите удалить?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: 'delete_napr_' in callback.data)
def callback_delete_class_napr(callback):
    data = callback.data.split('_')
    date = data[2]
    napr = data[3]
    cursor.execute("SELECT id FROM classes WHERE date=? AND napr=?", (date, napr))
    results = cursor.fetchall()
    users = [result[0] for result in results]
    # удаление занятий
    cursor.execute("DELETE FROM classes WHERE date=? AND napr=?", (date, napr))
    database.commit()
    # отправка сообщения об успешном удалении
    bot.send_message(callback.message.chat.id, f'Занятие на {date} по направлению {napr} успешно удалено.')
    notice_of_class_cancellation(users, date, napr)


# Словарь для хранения текущей страницы
pages_replace = {}


@bot.callback_query_handler(func=lambda callback: 'replace_a_training' in callback.data)
def callback_replace_a_training(callback):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    # Получение всех дат и направлений занятий
    cursor.execute("SELECT date, napr FROM classes")
    data = cursor.fetchall()

    # Создание списка дат
    dates = []
    for row in data:
        if row[0] not in dates:
            dates.append(row[0])

    # Получение текущей страницы пользователя
    current_page = pages_replace.get(callback.from_user.id, 0)

    # Количество элементов на одной странице
    items_per_page = 5
    start_index = current_page * items_per_page
    end_index = start_index + items_per_page

    # Формирование клавиатуры с датами на текущей странице
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    for date in dates[start_index:end_index]:
        button = types.InlineKeyboardButton(text=date, callback_data='replace_date_' + date)
        keyboard.add(button)

    # Добавление кнопок "Вперёд" и "Назад"
    if current_page > 0:
        prev_button = types.InlineKeyboardButton(text='Назад', callback_data='prev_page_2')
        keyboard.row(prev_button)
    if end_index < len(dates):
        next_button = types.InlineKeyboardButton(text='Вперёд', callback_data='next_page_2')
        keyboard.row(next_button)

    # Отправка сообщения с выбором даты
    bot.send_message(callback.message.chat.id, "Выберете дату, на которую хотели бы заменить занятие:",
                     reply_markup=keyboard)


# Обработка нажатий кнопок "Вперёд" и "Назад"
@bot.callback_query_handler(func=lambda callback: callback.data in ['prev_page_2', 'next_page_2'])
def callback_pagination(callback):
    user_id = callback.from_user.id
    current_page = pages_replace.get(user_id, 0)

    if callback.data == 'prev_page':
        current_page = max(0, current_page - 1)
    elif callback.data == 'next_page':
        current_page += 1

    pages_delete[user_id] = current_page

    # Вызов функции, которая формирует и отправляет клавиатуру
    callback_delete_a_training(callback)


@bot.callback_query_handler(func=lambda callback: 'replace_date_' in callback.data)
def callback_replace_class_date(callback):
    date = callback.data.split('_')[2]
    # получение направления
    cursor.execute("SELECT napr FROM classes WHERE date=?", (date,))
    data = cursor.fetchall()

    # создание клавиатуры с направлениями
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for row in data:
        if row[0] not in buttons:
            buttons.append(row[0])
            button = types.InlineKeyboardButton(text=row[0], callback_data='replace_napr_' + date + '_' + row[0])
            keyboard.add(button)

    # отправка сообщения с выбором направления
    bot.send_message(callback.message.chat.id, "Какое направление вы хотите заменить?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: 'replace_napr_' in callback.data)
def callback_replace_class_napr(callback):
    data, napr = callback.data.split('_')[2:]
    cursor.execute("SELECT * FROM classes WHERE date=? AND napr=?", (data, napr))
    rows = cursor.fetchall()
    if len(rows) == 0:
        bot.send_message(callback.message.chat.id, "Не найдено занятий на эту дату и направление")
        return
    bot.send_message(callback.message.chat.id,
                     "Введите новые данные в формате 'дд-мм-гггг_новое направление_новый тренер'")
    bot.register_next_step_handler(callback.message, replace_classes, rows, data, napr)


# функция, которая вызывается при замене занятия админом
def replace_classes(message, rows, data, napr):
    new_data, new_napr, new_coach = message.text.split('_')
    cursor.execute("SELECT id FROM classes WHERE date=? AND napr=?", (data, napr))
    results = cursor.fetchall()
    users = [result[0] for result in results]
    for row in rows:
        cursor.execute("UPDATE classes SET date=?, napr=?, coach=? WHERE date=? AND napr=?",
                       (new_data, new_napr, new_coach, data, napr))
    database.commit()
    bot.send_message(message.chat.id, "Данные обновлены!")
    notice_of_class_change(users, new_data, new_napr, new_coach, data, napr)


# функция, которая уведомляет пользователя об отмене занятия
def notice_of_class_cancellation(users, date, napr):
    cursor = database.cursor()
    users = [user for user in users if user != "-"]
    for user in users:
        bot.send_message(user, f"Внимание! Занятие {date} - {napr}, к сожалению, отменено.")
    cursor.close()


# функция, которая уведомляет пользователя о замене занятия
def notice_of_class_change(users, new_data, new_napr, new_coach, data, napr):
    cursor = database.cursor()
    users = [user for user in users if user != "-"]
    for user in users:
        bot.send_message(user, f"Внимание! Занятие {data} - {napr}, к сожалению, заменено.\n"
                               f"Новое занятие состоится {new_data} - {new_napr}, тренер {new_coach}")
    cursor.close()
