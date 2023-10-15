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


def update_visitor(date, napr, coach, visitor):
    # Замена 4-го параметра посетилеля на реального человека, когда он записывается
    cursor.execute("SELECT rowid FROM classes WHERE date = ? AND napr = ? AND coach = ? AND visitor = '-'",
                   (date, napr, coach))
    row = cursor.fetchone()
    cursor.execute("UPDATE classes SET visitor = ? WHERE rowid = ?",
                   (visitor, row[0]))

def prob_classes(date, napr, coach, visitor):
    # Добавление информации о записи на пробное занятие в таблицу
    date_today = datetime.now().date()
    cursor.execute("INSERT INTO prob_classes (date_today, date, napr, coach, visitor) VALUES (?, ?, ?, ?, ?)", (date_today, date, napr, coach, visitor))

def rasp_show(date):
   # Вывод расписания
    cursor.execute("SELECT DISTINCT napr, coach FROM classes WHERE date = ?", (date,))
    rows = cursor.fetchall()
    rasp_list = []
    for row in rows:
        napr, coach = row
        rasp_list.append(f"Направление: {napr}, Тренер: {coach}")
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


@bot.message_handler(commands=['start'])
def start(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    botton1 = types.KeyboardButton('Записаться')
    markup.row(botton1)
    bot.send_message(message.chat.id, 'Бот для фитнес-студии', reply_markup=markup)

@bot.message_handler(content_types=['text'])
def menu(message):

    if message.text == 'Записаться':
        markup = types.InlineKeyboardMarkup(row_width=3)
        cursor.execute("SELECT DISTINCT date FROM classes")
        dates_ = cursor.fetchall()
        dates = []
        for date in dates_:
            for d in date:
                dates.append(d)
        for date in dates:
            butt = 'date_button:' + date
            botton = types.InlineKeyboardButton(date, callback_data=butt)
            markup.add(botton)
        bot.send_message(message.chat.id, 'Выберите день:', reply_markup=markup)

@bot.callback_query_handler(func=lambda callback: 'date_button' in callback.data)
def callback_message(callback):
    date = callback.data.split(':')[1]
    rasp_list = rasp_show(date)
    message = "\n".join(rasp_list)
    bot.send_message(callback.message.chat.id, message)


bot.polling(none_stop=True)
