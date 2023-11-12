import telebot
import threading

bot = telebot.TeleBot('6432420440:AAGQcNnopghQU9RWCRL_FwODBDUPIl9dTT8')


# Функция для запуска бота в отдельном потоке
def polling_thread():
    bot.polling(none_stop=True)


# Запускаем бот в отдельном потоке
polling = threading.Thread(target=polling_thread)
polling.start()