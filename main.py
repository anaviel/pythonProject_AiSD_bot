from database_editing import *
from authorization_process import *
from rasp_editing import *
from registr_cancel_class import *
from subscriptions_and_info import *
from bot_start import *
from delete_records_daily import *


database = sqlite3.connect('rasp.db', check_same_thread=False)
cursor = database.cursor()


# Вывод таблицы с расписанием и абонементами
cursor.execute("SELECT * FROM classes")
print(cursor.fetchall())
cursor.execute("SELECT * FROM subscription_inf")
print(cursor.fetchall())
cursor.execute("SELECT * FROM prob_classes")
print(cursor.fetchall())



#cursor.execute("UPDATE subscription_inf SET prob_inf = '-', subscription = 0 WHERE id = 1269188609")
#cursor.execute("SELECT * FROM subscription_inf")
#print(cursor.fetchall())
#cursor.execute("UPDATE classes SET visitor = '-' WHERE visitor = 'Маркова Анастасия Андреевна'")
database.commit()


# класс для админов
class Admin:
    _admin_id_1: int = 12691886091
    _admin_id_2: int = 961443903
    admin_used: int

    def __init__(self, user_id):
        if (user_id == self._admin_id_1) or (user_id == self._admin_id_2):
            self.admin_used = user_id
        else:
            self.admin_used = 0

    # "Добавление расписания"
    @staticmethod
    def add_rasp(message, date, napr, coach):
        for _ in range(5):
            insert_rasp(date, napr, coach)
        bot.send_message(message.chat.id,
                         f"В расписание добавилась запись со следующими параметрами:\n"
                         f"Дата: {date}\nНаправление: {napr}\nТренер: {coach}")

    # "Редактировать расписание"
    @staticmethod
    def edit_rasp(message):
        edit_rasp(message)

    # "Абонементы"
    @staticmethod
    def subscription(message):
        subscription(message)

    # "Обновить прайс-лист"
    @staticmethod
    def update_price_list(message):
        update_price_list(message)

    # клавиатура для админа
    @staticmethod
    def keyboard_admin(message):
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Добавить расписание')
        button2 = types.KeyboardButton('Редактировать расписание')
        button3 = types.KeyboardButton('Абонементы')
        button4 = types.KeyboardButton('Обновить прайс-лист')
        markup1.row(button1, button2)
        markup1.row(button3, button4)
        bot.send_message(message.chat.id, 'Добро пожаловать, администратор!', reply_markup=markup1)


# класс для пользователей, которые посещают студию
class User:
    user_id: int

    def __init__(self, user_id):
        self.user_id = user_id

    # "Записаться"
    @staticmethod
    def sign_up_for_training(message):
        sign_up_for_training(message)

    # "Отменить занятие"
    @staticmethod
    def cancel_registration_for_training(message):
        cancel_registration_for_training(message)

    # "Личный кабинет"
    @staticmethod
    def personal_account(message):
        personal_account(message)

    # "Помощь"
    @staticmethod
    def help(message):
        help(message)

    # клавиатура для пользователя
    @staticmethod
    def keyboard_user(message):
        markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Записаться')
        button2 = types.KeyboardButton('Отменить запись')
        button3 = types.KeyboardButton('Личный кабинет')
        button4 = types.KeyboardButton('Помощь')
        markup2.row(button1, button2)
        markup2.row(button3, button4)
        bot.send_message(message.chat.id, 'Добро пожаловать в бот фитнес-студии.', reply_markup=markup2)


# класс для новых пользователей, которые первый раз придут в студию
class NewUser:
    new_user_id: int

    def __init__(self, user_id):
        self.new_user_id = user_id

    # "Записаться на пробное занятие"
    @staticmethod
    def trial_training(message):
        trial_training(message)

    # клавиатура для нового пользователя
    @staticmethod
    def keyboard_new_user(message):
        markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Записаться на пробное занятие')
        button2 = types.KeyboardButton('Личный кабинет')
        button3 = types.KeyboardButton('Помощь')
        markup2.row(button1)
        markup2.row(button2, button3)
        bot.send_message(message.chat.id, 'Бот для фитнес-студии', reply_markup=markup2)


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    admin = Admin(user_id)
    # если боту написал один из админов
    if admin.admin_used == user_id:
        # показываем клавиатуру для него
        admin.keyboard_admin(message)
    # если боту написал не админ, а пользователь
    elif admin.admin_used == 0:
        authorization(message)


@bot.message_handler(content_types=['text'])
def menu(message):
    user_id = message.from_user.id
    admin = Admin(user_id)
    # если боту написал админ
    if admin.admin_used == user_id:
        if message.text == 'Добавить расписание':
            bot.send_message(message.chat.id, 'Введите сообщение в формате:\nдд-мм-гггг_Направление_Тренер')
            bot.register_next_step_handler(message, lambda msg: admin.add_rasp(msg, msg.text.split('_')[0],
                                                                               msg.text.split('_')[1],
                                                                               msg.text.split('_')[2]))
        elif message.text == 'Редактировать расписание':
            admin.edit_rasp(message)
        elif message.text == 'Абонементы':
            admin.subscription(message)
        elif message.text == 'Обновить прайс-лист':
            bot.send_message(message.chat.id, 'Пожалуйста, отправьте изображение обновлённого прайс-листа.')
            bot.register_next_step_handler(message, admin.update_price_list)
    # если боту написал пользователь
    else:
        user = User(user_id)
        if message.text == 'Записаться':
            user.sign_up_for_training(message)
        elif message.text == 'Отменить запись':
            user.cancel_registration_for_training(message)
        elif message.text == 'Личный кабинет':
            user.personal_account(message)
        elif message.text == 'Помощь':
            user.help(message)

    if message.text == 'Записаться на пробное занятие':
        new_user = NewUser(user_id)
        new_user.trial_training(message)
