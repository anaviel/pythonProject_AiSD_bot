import telebot
import threading
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())
bot = telebot.TeleBot(os.getenv('TOKEN'))


# Функция для запуска бота в отдельном потоке
def polling_thread():
    bot.polling(none_stop=True)


# Запускаем бот в отдельном потоке
polling = threading.Thread(target=polling_thread)
polling.start()