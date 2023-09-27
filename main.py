import telebot
import sqlite3

bot = telebot.TeleBot('6432420440:AAGQcNnopghQU9RWCRL_FwODBDUPIl9dTT8')
database = sqlite3.connect('rasp.db')

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, 'Тест')

bot.polling(none_stop=True)
