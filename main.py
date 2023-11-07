import telebot
from telebot import types
import os
from delete_records_daily import *

bot = telebot.TeleBot('6432420440:AAGQcNnopghQU9RWCRL_FwODBDUPIl9dTT8')

# Создание БД с расписанием
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


def subscription_create():
    # Создание таблицы с информацией об абонементах
    cursor.execute("""CREATE TABLE IF NOT EXISTS subscription_inf (
            id text,
            phone_number text,
            visitor text,
            prob_inf text,
            subscription int
        )""")


def insert_rasp(date, napr, coach, visitor='-'):
    # Добавление расписания
    cursor.execute("INSERT INTO classes (date, napr, coach, visitor) VALUES (?, ?, ?, ?)", (date, napr, coach, visitor))
    database.commit()


def update_visitor(date, napr, coach, visitor):
    cursor = database.cursor()
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
    cursor.execute("INSERT INTO prob_classes (date_today, date, napr, coach, visitor) VALUES (?, ?, ?, ?, ?)",
                   (date_today, date, napr, coach, visitor))
    database.commit()


def rasp_show(date):
    cursor = database.cursor()
    # Вывод расписания
    cursor.execute("SELECT DISTINCT napr, coach FROM classes WHERE date = ? AND visitor = '-'", (date,))
    rows_available = cursor.fetchall()
    cursor.execute("SELECT DISTINCT napr, coach FROM classes WHERE date = ? AND visitor != '-'", (date,))
    rows_unavailable = cursor.fetchall()
    rasp_list_available = []
    rasp_list_unavailable = []
    now = datetime.now()
    for row in rows_available:
        napr, coach = row
        if now < datetime.strptime(f"{date} {napr[:5]}", "%d-%m-%Y %H:%M"):
            rasp_list_available.append(f"🤍{napr}, тренер: {coach}")
    for row in rows_unavailable:
        napr, coach = row
        if now < datetime.strptime(napr[:5], "%H:%M"):
            rasp_list_unavailable.append(f"🤍{napr}, тренер: {coach} (❌На данное занятие мест уже нет!)")
    return rasp_list_available, rasp_list_unavailable


# Удаление данных
# cursor.execute("DELETE FROM classes")

# Удаление таблицы
# cursor.execute("DROP TABLE subscription_inf")

# для себя
# cursor.execute("DELETE FROM classes WHERE rowid = (SELECT MAX(rowid) FROM classes)")

# Заполнение таблицы
"""
insert_rasp('04-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('04-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('04-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('04-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('04-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('04-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('04-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('04-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('04-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('04-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('04-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('04-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('04-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('04-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('04-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('05-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('05-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('05-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('05-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('05-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('05-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('05-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('05-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('05-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('05-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('05-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('05-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('05-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
"""

# Вывод таблицы с расписанием
cursor.execute("SELECT * FROM classes")
print(cursor.fetchall())

# Вывод таблицы с пробными занятиями
# cursor.execute("SELECT * FROM prob_classes")
# print(cursor.fetchall())

# cursor.execute("UPDATE subscription_inf SET prob_inf = '+' WHERE id = 961443903")
# cursor.execute("UPDATE subscription_inf SET prob_inf = '+' WHERE id = 1269188609")
# cursor.execute("UPDATE subscription_inf SET subscription = '0' WHERE id = 1269188609")
cursor.execute("SELECT * FROM subscription_inf")
print(cursor.fetchall())

database.commit()


# класс для админов
class Admin:
    _admin_id_1: int = 1269188609
    _admin_id_2: int = 9614439031
    admin_used: int

    def __init__(self, user_id):
        if (user_id == self._admin_id_1) or (user_id == self._admin_id_2):
            self.admin_used = user_id
        else:
            self.admin_used = 0

    # "Добавление расписания"
    def add_rasp(self, message, date, napr, coach):
        insert_rasp(date, napr, coach)
        bot.send_message(message.chat.id,
                         f"В расписание добавилась запись со следующими параметрами:\n"
                         f"Дата: {date}\nНаправление: {napr}\nТренер: {coach}")

    # "Редактировать расписание"
    def edit_rasp(self, message):
        edit_rasp(message)

    # "Абонементы"
    def subscription(self, message):
        subscription(message)

    # "Обновить прайс-лист"
    def update_price_list(self, message):
        update_price_list(message)

    # клавиатура для админа
    def keyboard_admin(self, message):
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
    def sign_up_for_training(self, message):
        sign_up_for_training(message)

    # "Отменить занятие"
    def cancel_registration_for_training(self, message):
        cancel_registration_for_training(message)

    # "Личный кабинет"
    def personal_account(self, message):
        personal_account(message)

    # "Помощь"
    def help(self, message):
        help(message)

    # клавиатура для пользователя
    def keyboard_user(self, message):
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

    # "Оформить пробное занятие"
    # def ...(self, message):
    #    ...

    # "Личный кабинет"
    # def personal_account(self, message):
    #    personal_account(message)

    # клавиатура для нового пользователя
    # def keyboard_new_user(self, message):
    #    ...

    def keyboard_new_user(self, message):
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


def authorization(message):
    bot.send_message(message.chat.id, 'Добро пожаловать в бот нашей фитнес-студии. '
                                      'Вы зарегистрированы? (Да/Нет)')
    bot.register_next_step_handler(message, check_visitor)


def check_visitor(message):
    # Регистрация/авторизация пользователя
    if message.text.lower() == 'нет':
        bot.send_message(message.chat.id, 'Для регистрации, пожалуйста, введите свой номер телефона, '
                                          'а также Ваше ФИО в формате:\n\n  '
                                          '+7YYYXXXXXXX Фамилия Имя Отчество')
        bot.register_next_step_handler(message, add_subscript)
    if message.text.lower() == 'да':
        bot.send_message(message.chat.id, 'Для авторизации, пожалуйста, введите свой номер телефона '
                                          'в формате:\n\n  +7YYYXXXXXXX')
        bot.register_next_step_handler(message, check_number)


def add_subscript(message):
    # Добавляем в таблицу с абонементами запись о новом пользователе
    user_id = message.from_user.id
    phone_number = message.text.split(' ')[0]
    visitor_name = ' '.join(message.text.split(' ')[1:])
    prob_inf = '-'
    subscription_ = 0
    cursor.execute("INSERT INTO subscription_inf "
                   "(id, phone_number, visitor, prob_inf, subscription) VALUES (?, ?, ?, ?, ?)",
                   (user_id, phone_number, visitor_name, prob_inf, subscription_))
    database.commit()
    new_user = NewUser(user_id)
    # показываем клавиатуру для нововго пользователя
    new_user.keyboard_new_user(message)


def check_number(message):
    # Авторизация по номеру
    user_id = message.from_user.id
    phone_number = message.text
    cursor.execute("SELECT visitor FROM subscription_inf WHERE phone_number = ?", (phone_number,))
    name_visitor = ''.join(cursor.fetchone())
    if name_visitor:
        cursor.execute("SELECT id FROM subscription_inf WHERE visitor = ? AND phone_number = ?",
                       (name_visitor, phone_number))
        if ''.join(cursor.fetchone()) != user_id:
            cursor.execute("UPDATE subscription_inf SET id = ? WHERE visitor = ? AND phone_number = ?",
                           (user_id, name_visitor, phone_number))
        bot.send_message(message.chat.id, f'Здравствуйте, {name_visitor}! Вы успешно авторизовались.')
        cursor.execute("SELECT prob_inf FROM subscription_inf WHERE id = ?",
                       (user_id,))
        if ''.join(cursor.fetchone()) == '+':
            user = User(user_id)
            # показываем клавиатуру для пользователя
            user.keyboard_user(message)
        else:
            new_user = NewUser(user_id)
            # показываем клавиатуру для пользователя
            new_user.keyboard_new_user(message)
    else:
        bot.send_message(message.chat.id, 'К сожалению, номер не найден. Проверьте правильность введённых'
                                          'данных или обратитесь к службе поддержки.')
        start()


@bot.callback_query_handler(func=lambda callback: 'replenish_subscription' in callback.data)
def callback_replenish_subscription(callback):
    bot.send_message(callback.message.chat.id,
                     'Введите номер телефона, ФИО посетителя, пополнившего абонемент, и количество '
                     'приобретённых занятий через запятую.\n\n'
                     'Пример: <b><i>+79213421431, Иванова Екатерина Александровна, 30</i></b>',
                     parse_mode='HTML')
    bot.register_next_step_handler(callback.message, replenish_subscription, callback)


@bot.callback_query_handler(func=lambda callback: 'delete_a_training' in callback.data)
def callback_delete_a_training(callback):
    # получение всех дат и направлений занятий
    cursor.execute("SELECT date, napr FROM classes")
    data = cursor.fetchall()
    # создание списка дат
    dates = []
    for row in data:
        if row[0] not in dates:
            dates.append(row[0])
    # создание клавиатуры с датами
    keyboard = types.InlineKeyboardMarkup()
    for date in dates:
        button = types.InlineKeyboardButton(text=date, callback_data='delete_class_date_' + date)
        keyboard.add(button)

    # отправка сообщения с выбором даты
    bot.send_message(callback.message.chat.id, "Выберете дату, на которую хотели бы отменить занятие:",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: 'delete_class_date_' in callback.data)
def callback_delete_class_date(callback):
    date = callback.data.split('_')[3]
    # получение направления
    cursor.execute("SELECT napr FROM classes WHERE date=?", (date,))
    data = cursor.fetchall()

    # создание клавиатуры с направлениями
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for row in data:
        if row[0] not in buttons:
            buttons.append(row[0])
            button = types.InlineKeyboardButton(text=row[0], callback_data='delete_class_napr_' + date + '_' + row[0])
            keyboard.add(button)

    # отправка сообщения с выбором направления
    bot.send_message(callback.message.chat.id, "Какое направление вы хотите удалить?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: 'delete_class_napr_' in callback.data)
def callback_delete_class_napr(callback):
    data = callback.data.split('_')
    date = data[3]
    napr = data[4]
    # удаление занятий
    cursor.execute("DELETE FROM classes WHERE date=? AND napr=?", (date, napr))
    database.commit()
    # отправка сообщения об успешном удалении
    bot.send_message(callback.message.chat.id, f'Занятие на {date} по направлению {napr} успешно удалено.')


@bot.callback_query_handler(func=lambda callback: 'replace_a_training' in callback.data)
def callback_replace_a_training(callback):
    # получение всех дат и направлений занятий
    cursor.execute("SELECT date, napr FROM classes")
    data = cursor.fetchall()
    # создание списка дат
    dates = []
    for row in data:
        if row[0] not in dates:
            dates.append(row[0])
    # создание клавиатуры с датами
    keyboard = types.InlineKeyboardMarkup()
    for date in dates:
        button = types.InlineKeyboardButton(text=date, callback_data='replace_class_date_' + date)
        keyboard.add(button)

    # отправка сообщения с выбором даты
    bot.send_message(callback.message.chat.id, "Выберете дату, на которую хотели бы заменить занятие:",
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: 'replace_class_date_' in callback.data)
def callback_replace_class_date(callback):
    date = callback.data.split('_')[3]
    # получение направления
    cursor.execute("SELECT napr FROM classes WHERE date=?", (date,))
    data = cursor.fetchall()

    # создание клавиатуры с направлениями
    keyboard = types.InlineKeyboardMarkup()
    buttons = []
    for row in data:
        if row[0] not in buttons:
            buttons.append(row[0])
            button = types.InlineKeyboardButton(text=row[0], callback_data='replace_class_napr_' + date + '_' + row[0])
            keyboard.add(button)

    # отправка сообщения с выбором направления
    bot.send_message(callback.message.chat.id, "Какое направление вы хотите заменить?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda callback: 'replace_class_napr_' in callback.data)
def callback_replace_class_napr(callback):
    data, napr = callback.data.split('_')[3:]
    cursor.execute("SELECT * FROM classes WHERE date=? AND napr=?", (data, napr))
    rows = cursor.fetchall()
    print(rows)
    if len(rows) == 0:
        bot.send_message(callback.message.chat.id, "Не найдено занятий на эту дату и направление")
        return
    bot.send_message(callback.message.chat.id,
                     "Введите новые данные в формате 'дд-мм-гггг_новое направление_новый тренер'")
    bot.register_next_step_handler(callback.message, replace_classes, rows, data, napr)


@bot.callback_query_handler(func=lambda callback: 'date-napr_' in callback.data)
def callback_cancel(callback):
    user_id = callback.from_user.id
    cursor.execute("SELECT visitor FROM subscription_inf WHERE id = ?", (user_id,))
    name = ''.join(cursor.fetchone())
    date_napr = callback.data.split('_')
    date = date_napr[1]
    napr = date_napr[2]
    cursor.execute("SELECT coach FROM classes WHERE date = ? AND napr = ?", (date, napr))
    coach = ''.join(cursor.fetchone())
    cursor.execute("UPDATE classes SET visitor = '-' WHERE date = ? AND napr = ? AND coach = ?",
                   (date, napr, coach))
    cursor.execute("SELECT subscription FROM subscription_inf WHERE visitor = ?",
                   (name,))
    result = cursor.fetchone()
    new_subscription = result[0] + 1
    cursor.execute("UPDATE subscription_inf SET subscription = ? WHERE visitor = ?",
                   (new_subscription, name))
    database.commit()
    bot.send_message(callback.message.chat.id,
                     f'Запись на {date}, "{napr}" успешно отменена.'
                     f'\nНа баланс Вашего абонемента было возвращено одно занятие.')
    cursor.execute("SELECT * FROM classes")
    print(cursor.fetchall())


@bot.callback_query_handler(func=lambda callback: 'date:' in callback.data)
def callback_dates_show(callback):
    markup = types.InlineKeyboardMarkup()
    date = callback.data.split(':')[1]
    rasp_list_available, rasp_list_unavailable = rasp_show(date)
    if not rasp_list_available:
        bot.send_message(callback.message.chat.id, "🛏️ На сегодня занятий больше нет.")
        return
    rasp_str = f'Информация о направлениях на {date}:\n\n'
    for string in rasp_list_available:
        rasp_str += string
        rasp_str += '\n'
    rasp_str = rasp_str + '➖\n'
    for string in rasp_list_unavailable:
        rasp_str += string
        rasp_str += '\n'
    rasp_str += '\nВыберите направление, на которое хотели бы записаться:'
    for i in rasp_list_available:
        napr = i.split(',')[0][1:]
        reg = 'reg_' + date + '_' + napr
        button = types.InlineKeyboardButton(napr, callback_data=reg)
        markup.add(button)
    bot.send_message(callback.message.chat.id, rasp_str, reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: 'reg_' in callback.data)
def callback_reg(callback):
    cursor = database.cursor()
    user_id = callback.from_user.id
    cursor.execute("SELECT visitor FROM subscription_inf WHERE id = ?", (user_id,))
    name = ''.join(cursor.fetchone())
    data_parts = callback.data.split('_')
    date = data_parts[1]
    napr = data_parts[2]
    if is_user_enter(name, date, napr):
        bot.send_message(callback.message.chat.id, f'Вы уже записаны на занятие {date} ({napr}).')
    else:
        cursor.execute("SELECT coach FROM classes WHERE date = ? AND napr = ?", (date, napr))
        coach = ''.join(cursor.fetchone())
        update_visitor(date, napr, coach, name)
        cursor.execute("SELECT subscription FROM subscription_inf WHERE visitor = ?", (name,))
        result = cursor.fetchone()
        new_subscription = result[0] - 1
        cursor.execute("UPDATE subscription_inf SET subscription = ? WHERE visitor = ?", (new_subscription, name))
        database.commit()
        bot.send_message(callback.message.chat.id,
                         f'Вы успешно записаны {date} на {napr}.\nС баланса Вашего абонемента было списано одно занятие.')


def is_user_enter(name, date, napr):
    cursor = database.cursor()
    cursor.execute("SELECT * FROM classes WHERE date = ? AND napr = ? AND visitor= ?", (date, napr, name))
    result = cursor.fetchall()
    cursor.close()
    return len(result) > 0


# функция, которая вызывается при нажатии пользователем на кнопку "Записаться"
def sign_up_for_training(message):
    cursor = database.cursor()
    user_id = message.from_user.id
    cursor.execute("SELECT subscription FROM subscription_inf WHERE id = ?", (user_id,))
    sub = cursor.fetchone()
    if sub:
        if sub[0] > 0:
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
            cursor.close()
        else:
            bot.send_message(message.chat.id,
                             "Вы не можете записаться на занятие, так как у вас закончился абонемент.\n"
                             "Вам необходимо обратиться к администратору в студии для его пополнения.")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка. К сожалению, невозможно записаться на занятие.")


# функция, которая вызывается при нажатии пользователем на кнопку "Отметить запись"
def cancel_registration_for_training(message):
    user_id = message.from_user.id
    cursor.execute("SELECT visitor FROM subscription_inf WHERE id = ?", (user_id,))
    visitor = ''.join(cursor.fetchone())
    cursor.execute("SELECT date, napr FROM classes WHERE visitor = ?", (visitor,))
    markup = types.InlineKeyboardMarkup()
    dates_napr_ = cursor.fetchall()
    dates_napr = []
    for d_n in dates_napr_:
        dates_napr.append(d_n)
    for d_n in dates_napr:
        date = d_n[0]
        napr = d_n[1]
        butt = 'date-napr_' + date + '_' + napr
        name_butt = date + ' ' + napr
        button = types.InlineKeyboardButton(name_butt, callback_data=butt)
        markup.add(button)
    bot.send_message(message.chat.id, 'Какое направление хотите отменить?', reply_markup=markup)


# функция, которая вызывается при нажатии пользователем на кнопку "Личный кабинет"
def personal_account(message):
    cursor = database.cursor()
    user_id = message.from_user.id
    cursor.execute("SELECT visitor FROM subscription_inf WHERE id = ?", (user_id,))
    name = ''.join(cursor.fetchone())
    cursor.execute("SELECT subscription FROM subscription_inf WHERE visitor = ?",
                   (name,))
    result = cursor.fetchone()[0]
    cursor.execute("SELECT date, napr FROM classes WHERE visitor = ?", (name,))
    dates_napr_ = cursor.fetchall()
    dates_napr = []
    for d_n in dates_napr_:
        dates_napr.append(d_n)
    classes = ''
    for d_n in dates_napr:
        date = d_n[0]
        napr = d_n[1]
        classes = classes + '\n' + '    ' + date + '  ' + napr + '\n'
    image_file = os.listdir("images")
    if image_file:
        image_path = os.path.join("images", image_file[0])
        with open(image_path, 'rb') as photo:
            bot.send_photo(message.chat.id, photo,
                           caption=f'🤍Уважаемая, {name}!\n\n    Количество занятий на балансе Вашего абонемента: {result}\n\n🎀Занятия, на которые Вы записаны:\n{classes}')
    cursor.close()


# функция, которая вызывается при нажатии пользователем на кнопку "Помощь"
def help(message):
    bot.send_message(message.chat.id, '''Инструкция по пользованию кнопками:
            \n\n🤍«Записаться»🤍 
        При нажатии на данную кнопку, Вам будет предложено выбрать удобный для Вас день для записи, после чего Вы сможете выбрать желаемое направление.
        После выбора направления Вы автоматически будете записаны на занятие, при этом со счёта Вашего абонемента будет списано одно занятие. 
            \n\n🤍«Отменить занятие»🤍 
        Данная опция позволяет осуществить отмену записи. Вы увидите перечень занятий, на которые записаны, и сможете нажать на любое из них для удаления записи. 
        При этом на счёт Вашего абонемента будет возвращено одно занятие.
            \n\n🤍«Личный кабинет»🤍 
        При нажатии на данную кнопку Вы сможете посмотреть перечень занятий, на которые записались, а также баланс Вашего абонемента. 
        Если Вы собираетесь посетить студию впервые, то для Вас появится возможность оформить и оплатить пробное занятие. 
            ''')


# функция, которая вызывается при нажатии админом на кнопку "Обновить прайс-лист"
def update_price_list(message):
    file_info = bot.get_file(message.photo[-1].file_id)
    file_name = f"images/{file_info.file_id}.jpg"
    if os.listdir("images"):
        os.remove(os.path.join("images", os.listdir("images")[0]))
    downloaded_file = bot.download_file(file_info.file_path)
    with open(file_name, 'wb') as new_file:
        new_file.write(downloaded_file)
    bot.send_message(message.chat.id, "Прайс-лист успешно обновлён.")


# функция, которая вызывается при нажатии админом на кнопку "Абонементы"
def subscription(message):
    cursor.execute("SELECT * FROM subscription_inf")
    print(cursor.fetchall())
    markup_subscription = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Пополнить абонемент', callback_data='replenish_subscription')
    markup_subscription.add(button1)
    cursor.execute("SELECT visitor FROM subscription_inf WHERE subscription > 0")
    kol = len(cursor.fetchall())
    bot.send_message(message.chat.id, f'Количество активных абонементов: {kol}', reply_markup=markup_subscription)


# функция, которая вызывается при нажатии админом на кнопку "Редактировать расписание"
def edit_rasp(message):
    cursor.execute("SELECT * FROM classes")
    print(cursor.fetchall())
    markup_edit_rasp = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Удалить занятие', callback_data='delete_a_training')
    button2 = types.InlineKeyboardButton('Заменить занятие', callback_data='replace_a_training')
    markup_edit_rasp.add(button1, button2)
    bot.send_message(message.chat.id, "Выберите действие:", reply_markup=markup_edit_rasp)


# функция, которая вызывается при замене занятия админом
def replace_classes(message, rows, data, napr):
    new_data, new_napr, new_coach = message.text.split('_')
    for row in rows:
        cursor.execute("UPDATE classes SET date=?, napr=?, coach=? WHERE date=? AND napr=?",
                       (new_data, new_napr, new_coach, data, napr))
    database.commit()
    bot.send_message(message.chat.id, "Данные обновлены!")


def replenish_subscription(message, callback):
    try:
        phone_number, visitor, kol = message.text.split(', ')
        cursor.execute("SELECT subscription FROM subscription_inf WHERE phone_number = ? AND visitor = ?",
                       (phone_number, visitor))
        result = cursor.fetchone()
        if result is None:
            bot.send_message(message.chat.id, "Посетитель с таким именем не найден")
        else:
            new_subscription = result[0] + int(kol)
            cursor.execute("UPDATE subscription_inf SET subscription = ? WHERE visitor = ?",
                           (new_subscription, visitor))
            bot.send_message(message.chat.id, "Абонемент пополнен.")
        database.commit()
        cursor.execute("SELECT * FROM subscription_inf")
        print(cursor.fetchall())
    except:
        bot.send_message(message.chat.id, "Данные введены некорректно. Попробуйте снова.")
        callback_replenish_subscription(callback)


def delete_a_training(message, callback):
    ...


def replace_a_training(message, callback):
    ...


bot.polling(none_stop=True)
