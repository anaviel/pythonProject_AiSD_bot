import telebot
import sqlite3

bot = telebot.TeleBot('6432420440:AAGQcNnopghQU9RWCRL_FwODBDUPIl9dTT8')

#Создание БД с расписанием
database = sqlite3.connect('rasp.db')
#Создание курсора
cursor = database.cursor()

def rasp_create():
    #Создание таблицы (таблица уже создана, эту функцию больше вызывать не надо)
    cursor.execute("""CREATE TABLE IF NOT EXISTS articles (
        date text,
        napr text,
        coach text,
        visitor text
    )""")


#Вывод БД
#cursor.execute("SELECT * FROM articles")
#print(cursor.fetchall())

database.commit()
database.close()



@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Тест')


bot.polling(none_stop=True)
