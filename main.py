import telebot
import sqlite3
from datetime import datetime
from telebot import types
import os

bot = telebot.TeleBot('6432420440:AAGQcNnopghQU9RWCRL_FwODBDUPIl9dTT8')

#Создание БД с расписанием
database = sqlite3.connect('rasp.db', check_same_thread=False)
# Создание курсора
cursor = database.cursor()

def rasp_create():
    # Создание таблицы с расписанием
    cursor.execute("""CREATE TABLE IF NOT EXISTS classes (
        date text,
        napr text,
        coach text,
        visitor text
    )""")

def prob_create():
    # Создание таблицы с оплаченными пробными занятиями
    cursor.execute("""CREATE TABLE IF NOT EXISTS prob_classes (
        date_today text,
        date text,
        napr text,
        coach text,
        visitor text
    )""")

def subscription():
    # Создание таблицы с информацией об абонементах
    cursor.execute("""CREATE TABLE IF NOT EXISTS subscription_inf (
            visitor text,
            subscription int
        )""")

def insert_rasp(date, napr, coach, visitor='-'):
    # Добавление расписания
    cursor.execute("INSERT INTO classes (date, napr, coach, visitor) VALUES (?, ?, ?, ?)", (date, napr, coach, visitor))
    database.commit()

def update_visitor(date, napr, coach, visitor):
    # Замена 4-го параметра посетилеля на реального человека, когда он записывается
    cursor.execute("SELECT rowid FROM classes WHERE date = ? AND napr = ? AND coach = ? AND visitor = '-'",
                   (date, napr, coach))
    row = cursor.fetchone()
    cursor.execute("UPDATE classes SET visitor = ? WHERE rowid = ?",
                   (visitor, row[0]))
    cursor.execute("SELECT * FROM classes")
    print(cursor.fetchall())
    database.commit()

def prob_classes(date, napr, coach, visitor):
    # Добавление информации о записи на пробное занятие в таблицу
    date_today = datetime.now().date()
    cursor.execute("INSERT INTO prob_classes (date_today, date, napr, coach, visitor) VALUES (?, ?, ?, ?, ?)", (date_today, date, napr, coach, visitor))
    database.commit()

def rasp_show(date):
   # Вывод расписания
    cursor.execute("SELECT DISTINCT napr, coach FROM classes WHERE date = ?", (date,))
    rows = cursor.fetchall()
    rasp_list = []
    for row in rows:
        napr, coach = row
        rasp_list.append(f"🤍{napr}, тренер: {coach}")
    return rasp_list

# Удаление данных
#cursor.execute("DELETE FROM classes")

# Удаление таблицы
#cursor.execute("DROP TABLE clsses")

#Заполнение таблицы

"""
insert_rasp('01.11.23', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01.11.23', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01.11.23', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01.11.23', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01.11.23', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01.11.23', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01.11.23', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01.11.23', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01.11.23', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01.11.23', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01.11.23', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('01.11.23', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('01.11.23', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('01.11.23', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('02.11.23', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('02.11.23', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('02.11.23', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('02.11.23', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('02.11.23', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('02.11.23', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02.11.23', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02.11.23', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02.11.23', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02.11.23', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02.11.23', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('02.11.23', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('02.11.23', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('02.11.23', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
"""

# Вывод таблицы с расписанием
cursor.execute("SELECT * FROM classes")
print(cursor.fetchall())

# Вывод таблицы с пробными занятиями
#cursor.execute("SELECT * FROM prob_classes")
#print(cursor.fetchall())

database.commit()

name = ''

@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    button1 = types.KeyboardButton('Записаться')
    button2 = types.KeyboardButton('Добавить расписание')
    button3 = types.KeyboardButton('Отменить занятие')
    button4 = types.KeyboardButton('Абонементы')
    button5 = types.KeyboardButton('Личный кабинет')
    button6 = types.KeyboardButton('Обновить прайс-лист')
    markup.row(button1, button3, button5)
    markup.row(button2, button4, button6)
    bot.send_message(message.chat.id, 'Бот для фитнес-студии', reply_markup=markup)
    if name == '':
        bot.send_message(message.chat.id, 'Перед тем, как начать пользоваться ботом, пожалуйста, укажите свои полные фамилию, имя и отчество.')
        bot.register_next_step_handler(message, new_name)

@bot.message_handler(content_types=['text'])
def menu(message):

    if message.text == 'Записаться':
        markup = types.InlineKeyboardMarkup()
        cursor.execute("SELECT DISTINCT date FROM classes")
        dates_ = cursor.fetchall()
        dates = []
        for date in dates_:
            for d in date:
                dates.append(d)
        for date in dates:
            butt = 'date:' + date
            button = types.InlineKeyboardButton(date, callback_data=butt)
            markup.add(button)
        bot.send_message(message.chat.id, 'Выберите день:', reply_markup=markup)
    elif message.text == 'Добавить расписание':
        bot.send_message(message.chat.id, 'Введите сообщение в формате:\nгггг-мм-дд_Направление_Тренер')
        bot.register_next_step_handler(message, add_rasp)
    elif message.text == 'Отменить занятие':
        visitor = name
        cursor.execute("SELECT date, napr FROM classes WHERE visitor = ?", (visitor,))
        markup = types.InlineKeyboardMarkup()
        dates_napr_ = cursor.fetchall()
        dates_napr = []
        for d_n in dates_napr_:
            dates_napr.append(d_n)
        for d_n in dates_napr:
            date = d_n[0]
            napr = d_n[1]
            butt = 'date-napr_' + date + '_' + napr
            name_butt = date + ' ' + napr
            button = types.InlineKeyboardButton(name_butt, callback_data=butt)
            markup.add(button)
        bot.send_message(message.chat.id, 'Какое направление хотите отменить?', reply_markup=markup)
    elif message.text == 'Абонементы':
        cursor.execute("SELECT * FROM subscription_inf")
        print(cursor.fetchall())
        markup_subscription = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton('Добавить абонемент', callback_data='add_subscription')
        button2 = types.InlineKeyboardButton('Пополнить абонемент', callback_data='replenish_subscription')
        markup_subscription.add(button1, button2)
        cursor.execute("SELECT visitor FROM subscription_inf WHERE subscription > 0")
        kol = len(cursor.fetchall())
        bot.send_message(message.chat.id, f'Количество активных абонентов: {kol}', reply_markup=markup_subscription)
    elif message.text == 'Личный кабинет':
        cursor.execute("SELECT subscription FROM subscription_inf WHERE visitor = ?",
                       (name,))
        result = cursor.fetchone()[0]
        cursor.execute("SELECT date, napr FROM classes WHERE visitor = ?", (name,))
        dates_napr_ = cursor.fetchall()
        dates_napr = []
        for d_n in dates_napr_:
            dates_napr.append(d_n)
        classes = ''
        for d_n in dates_napr:
            date = d_n[0]
            napr = d_n[1]
            classes = classes + '\n' + '    ' + date + '  ' + napr + '\n'
        image_file = os.listdir("images")
        if image_file:
            image_path = os.path.join("images", image_file[0])
            with open(image_path, 'rb') as photo:
                bot.send_photo(message.chat.id, photo, caption=f'🤍Уважаемая, {name}!\n\n    Количество занятий на балансе Вашего абонемента: {result}\n\n🎀Занятия, на которые Вы записаны:\n{classes}')
    elif message.text == 'Обновить прайс-лист':
        bot.send_message(message.chat.id, 'Пожалуйста, отправьте изображение обновлённого прайс-листа.')
        bot.register_next_step_handler(message, update_price_list)
@bot.callback_query_handler(func=lambda callback: 'add_subscription' in callback.data)
def callback_add_subscription(callback):
    bot.send_message(callback.message.chat.id, f'Введите ФИО нового посетителя и количество пополняемых занятий через запятую.\n\nПример: <b><i>Иванова Екатерина Александровна, 30</i></b>', parse_mode='HTML')
    bot.register_next_step_handler(callback.message, add_subscription, callback)

@bot.callback_query_handler(func=lambda callback: 'replenish_subscription' in callback.data)
def callback_replenish_subscription(callback):
    bot.send_message(callback.message.chat.id, 'Введите ФИО посетителя, пополнившего абонемент, и количество приобретённых занятий через запятую.\n\nПример: <b><i>Иванова Екатерина Александровна, 30</i></b>', parse_mode='HTML')
    bot.register_next_step_handler(callback.message, replenish_subscription, callback)

@bot.callback_query_handler(func=lambda callback: 'date-napr_' in callback.data)
def callback_cancel(callback):
    global name
    date_napr = callback.data.split('_')
    date = date_napr[1]
    napr = date_napr[2]
    cursor.execute("SELECT coach FROM classes WHERE date = ? AND napr = ?", (date, napr))
    coach = ''.join(cursor.fetchone())
    cursor.execute("UPDATE classes SET visitor = '-' WHERE date = ? AND napr = ? AND coach = ?",
                   (date, napr, coach))
    cursor.execute("SELECT subscription FROM subscription_inf WHERE visitor = ?",
                   (name,))
    result = cursor.fetchone()
    new_subscription = result[0] + 1
    cursor.execute("UPDATE subscription_inf SET subscription = ? WHERE visitor = ?",
                   (new_subscription, name))
    database.commit()
    bot.send_message(callback.message.chat.id, f'Запись на {date}, "{napr}" успешно отменена.\nНа баланс Вашего абонемента было возвращено одно занятие.')
    cursor.execute("SELECT * FROM classes")
    print(cursor.fetchall())

@bot.callback_query_handler(func=lambda callback: 'date:' in callback.data)
def callback_dates_show(callback):

    markup = types.InlineKeyboardMarkup()
    date = callback.data.split(':')[1]
    rasp_list = rasp_show(date)
    rasp_str = f'Информация о направлениях на {date}:\n\n'
    for string in rasp_list:
        rasp_str += string
        rasp_str += '\n'
    rasp_str += '\nВыберите направление, на которое хотели бы записаться:'
    for i in rasp_list:
        napr = i.split(',')[0][1:]
        reg = 'reg_' + date + '_' + napr
        button = types.InlineKeyboardButton(napr, callback_data=reg)
        markup.add(button)
    bot.send_message(callback.message.chat.id, rasp_str, reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: 'reg_' in callback.data)
def callback_reg(callback):
    data_parts = callback.data.split('_')
    date = data_parts[1]
    napr = data_parts[2]
    cursor.execute("SELECT coach FROM classes WHERE date = ? AND napr = ?", (date, napr))
    coach = ''.join(cursor.fetchone())
    global name
    update_visitor(date, napr, coach, name)
    cursor.execute("SELECT subscription FROM subscription_inf WHERE visitor = ?",
                   (name,))
    result = cursor.fetchone()
    new_subscription = result[0] - 1
    cursor.execute("UPDATE subscription_inf SET subscription = ? WHERE visitor = ?",
                   (new_subscription, name))
    database.commit()
    bot.send_message(callback.message.chat.id, f'Вы успешно записаны {date} на {napr}.\nС баланса Вашего абонемента было списано одно занятие.')

def new_name(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Ваше имя успешно сохранено.')

def add_rasp(message):
    date = message.text.split('_')[0]
    napr = message.text.split('_')[1]
    coach = message.text.split('_')[2]
    insert_rasp(date, napr, coach)
    bot.send_message(message.chat.id, f"В расписание добавилась запись со следующими параметрами:\nДата: {date}\nНаправление: {napr}\nТренер: {coach}")

def add_subscription(message, callback):
    try:
        visitor, kol = message.text.split(', ')
        cursor.execute("INSERT INTO subscription_inf (visitor, subscription) VALUES (?, ?)", (visitor, kol))
        database.commit()
        cursor.execute("SELECT * FROM subscription_inf")
        print(cursor.fetchall())
    except:
        bot.send_message(message.chat.id, "Данные введены некорректно. Попробуйте снова.")
        callback_add_subscription(callback)
def replenish_subscription(message, callback):
    try:
        visitor, kol = message.text.split(', ')
        cursor.execute("SELECT subscription FROM subscription_inf WHERE visitor = ?",
                       (visitor,))
        result = cursor.fetchone()
        if result is None:
            bot.send_message(message.chat.id, "Посетитель с таким именем не найден")
        else:
            new_subscription = result[0] + int(kol)
            cursor.execute("UPDATE subscription_inf SET subscription = ? WHERE visitor = ?",
                           (new_subscription, visitor))
        database.commit()
        cursor.execute("SELECT * FROM subscription_inf")
        print(cursor.fetchall())
    except:
        bot.send_message(message.chat.id, "Данные введены некорректно. Попробуйте снова.")
        callback_add_subscription(callback)

def update_price_list(message):

    file_info = bot.get_file(message.photo[-1].file_id)
    file_name = f"images/{file_info.file_id}.jpg"
    if os.listdir("images"):
        os.remove(os.path.join("images", os.listdir("images")[0]))
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, "Прайс-лист успешно обновлён.")



bot.polling(none_stop=True)
