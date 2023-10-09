import telebot
import sqlite3
from datetime import datetime

bot = telebot.TeleBot('6432420440:AAGQcNnopghQU9RWCRL_FwODBDUPIl9dTT8')

# Создание БД с расписанием
database = sqlite3.connect('rasp.db')
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
    print(cursor.fetchall())

# Удаление данных
#cursor.execute("DELETE FROM classes")

# Удаление таблицы
#cursor.execute("DROP TABLE prob_classes")

"""insert_rasp('01.10.23', 'Растяжка', 'Тренер')
insert_rasp('01.10.23', 'Растяжка', 'Тренер')
insert_rasp('01.10.23', 'Растяжка', 'Тренер')
insert_rasp('01.10.23', 'Растяжка', 'Тренер')
insert_rasp('01.10.23', 'Йога', 'Тренер')
insert_rasp('01.10.23', 'Йога', 'Тренер')
insert_rasp('01.10.23', 'Йога', 'Тренер')
insert_rasp('01.10.23', 'Йога', 'Тренер')"""

#update_visitor('01.10.23', 'Йога', 'Тренер', 'Инна')

# Вывод таблицы с расписанием
cursor.execute("SELECT * FROM classes")
print(cursor.fetchall())

# Вывод таблицы с пробными занятиями
cursor.execute("SELECT * FROM prob_classes")
print(cursor.fetchall())

database.commit()
database.close()

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Тест')

# bot.polling(none_stop=True)
