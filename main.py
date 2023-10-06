import telebot
import sqlite3

bot = telebot.TeleBot('6432420440:AAGQcNnopghQU9RWCRL_FwODBDUPIl9dTT8')

#Создание БД с расписанием
database = sqlite3.connect('rasp.db')
#Создание курсора
cursor = database.cursor()

def rasp_create():
    #Создание таблицы с расписанием
    cursor.execute("""CREATE TABLE IF NOT EXISTS classes (
        date text,
        napr text,
        coach text,
        visitor text
    )""")

def prob_create():
    #Создание таблицы с оплаченными пробными занятиями
    cursor.execute("""CREATE TABLE IF NOT EXISTS prob_classes (
        date_today text,
        napr text,
        coach text,
        visitor text
    )""")

prob_create()

#Вывод таблицы с расписанием
#cursor.execute("SELECT * FROM classes")
#print(cursor.fetchall())

database.commit()
database.close()



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Тест')


#bot.polling(none_stop=True)
