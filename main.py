import telebot
import sqlite3

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
        napr text,
        coach text,
        visitor text
    )""")


def insert_rasp(date, napr, coach, visitor='-'):
    # Добавление расписания
    cursor.execute("INSERT INTO classes (date, napr, coach, visitor) VALUES (?, ?, ?, ?)", (date, napr, coach, visitor))

def update_visitor(date, napr, coach, visitor):
    # Замена 4-го параметра посетилеля на реального человека, когда он записывается
    cursor.execute("UPDATE classes SET visitor = ? WHERE date = ? AND napr = ? AND coach = ? AND visitor = '-'",
        (visitor, date, napr, coach))


prob_create()

# Удаление данных
#cursor.execute("DELETE FROM classes")

# Вывод таблицы с расписанием
#cursor.execute("SELECT * FROM classes")
#print(cursor.fetchall())

database.commit()
database.close()


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Тест')

# bot.polling(none_stop=True)
