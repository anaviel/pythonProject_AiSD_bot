import telebot
import sqlite3
from datetime import datetime
from telebot import types

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

"""
insert_rasp('01.10.23', 'Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01.10.23', 'Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01.10.23', 'Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01.10.23', 'Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01.10.23', 'Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01.10.23', 'Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01.10.23', 'Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01.10.23', 'Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02.10.23', 'Здоровая спина', 'Кузнецова Екатерина Александровна')
insert_rasp('02.10.23', 'Здоровая спина', 'Кузнецова Екатерина Александровна')
insert_rasp('02.10.23', 'Здоровая спина', 'Кузнецова Екатерина Александровна')
insert_rasp('02.10.23', 'Здоровая спина', 'Кузнецова Екатерина Александровна')
insert_rasp('04.10.23', 'Растяжка', 'Иванова Александра Михайловна')
insert_rasp('04.10.23', 'Растяжка', 'Иванова Александра Михайловна')
insert_rasp('04.10.23', 'Растяжка', 'Иванова Александра Михайловна')
insert_rasp('04.10.23', 'Растяжка', 'Иванова Александра Михайловна')
"""

#update_visitor('01.10.23', 'Йога', 'Тренер', 'Инна')

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
    botton1 = types.KeyboardButton('Записаться')
    markup.row(botton1)
    bot.send_message(message.chat.id, 'Бот для фитнес-студии', reply_markup=markup)
    if name == '':
        bot.send_message(message.chat.id, 'Перед тем, как начать пользоваться ботом, пожалуйста, укажите свои полные фамилию, имя и отчество')
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
        napr = i.split(':')[0][1:].split(',')[0]
        reg = 'reg:' + date + ':' + napr
        button = types.InlineKeyboardButton(napr, callback_data=reg)
        markup.add(button)
    bot.send_message(callback.message.chat.id, rasp_str, reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: 'reg:' in callback.data)
def callback_reg(callback):
    data_parts = callback.data.split(':')
    date = data_parts[1]
    napr = data_parts[2]
    cursor.execute("SELECT coach FROM classes WHERE date = ? AND napr = ?", (date, napr))
    coach = ''.join(cursor.fetchone())
    global name
    update_visitor(date, napr, coach, name)
    bot.send_message(callback.message.chat.id, f'Вы успешно записаны на {date} {napr}')

def new_name(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Ваше имя успешно сохранено.')

bot.polling(none_stop=True)
