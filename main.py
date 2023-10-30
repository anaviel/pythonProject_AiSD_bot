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
            visitor text,
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
        print(now, f"{date} {napr[:5]}")
        if now < datetime.strptime(f"{date} {napr[:5]}", "%d-%m-%Y %H:%M"):
            rasp_list_available.append(f"🤍{napr}, тренер: {coach}")
    for row in rows_unavailable:
        napr, coach = row
        if now < datetime.strptime(napr[:5], "%H:%M"):
            rasp_list_unavailable.append(f"🤍{napr}, тренер: {coach} (❌На данное занятие мест уже нет!)")
    return rasp_list_available, rasp_list_unavailable


# Удаление данных
#cursor.execute("DELETE FROM classes")

# Удаление таблицы
#cursor.execute("DROP TABLE subscription_inf")

# для себя
# cursor.execute("DELETE FROM classes WHERE rowid = (SELECT MAX(rowid) FROM classes)")

# Заполнение таблицы
"""
insert_rasp('01-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('01-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('01-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('01-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('01-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('01-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('01-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('02-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('02-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('02-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('02-11-2023', '12:00 Растяжка', 'Иванова Александра Михайловна')
insert_rasp('02-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02-11-2023', '14:00 Йога', 'Смирнова Юлия Валерьевна')
insert_rasp('02-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('02-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('02-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
insert_rasp('02-11-2023', '16:00 Пилатес', 'Кузнецова Екатерина Александровна')
"""


# Вывод таблицы с расписанием
cursor.execute("SELECT * FROM classes")
print(cursor.fetchall())

# Вывод таблицы с пробными занятиями
# cursor.execute("SELECT * FROM prob_classes")
# print(cursor.fetchall())


cursor.execute("SELECT * FROM subscription_inf")
print(cursor.fetchall())


class Admin:
    def __init__(self, user_id):
        self.user_id = user_id

    # "Добавление расписания"
    def add_rasp(self, message, date, napr, coach):
        insert_rasp(date, napr, coach)
        bot.send_message(message.chat.id,
                         f"В расписание добавилась запись со следующими параметрами:\nДата: {date}\nНаправление: {napr}\nТренер: {coach}")

    # "Абонементы"
    def subscription(self, message):
        subscription(message)

    # "Обновить прайс-лист"
    def update_price_list(self, message):
        update_price_list(message)


class User:
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


name = ''
var = 1269188609
var2 = 961443903


@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id

    if user_id == var:
        markup1 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Добавить расписание')
        button2 = types.KeyboardButton('Абонементы')
        button3 = types.KeyboardButton('Обновить прайс-лист')
        markup1.row(button1, button2, button3)
        bot.send_message(message.chat.id, 'Добро пожаловать, администратор!)', reply_markup=markup1)
        if name == '':
            bot.send_message(message.chat.id,
                             'Перед тем, как начать пользоваться ботом, пожалуйста, укажите свои полные фамилию, имя и отчество.')
            bot.register_next_step_handler(message, new_name)
    else:
        markup2 = types.ReplyKeyboardMarkup(resize_keyboard=True)
        button1 = types.KeyboardButton('Записаться')
        button3 = types.KeyboardButton('Отменить запись')
        button5 = types.KeyboardButton('Личный кабинет')
        button6 = types.KeyboardButton('Помощь')
        markup2.row(button1, button3, button5, button6)
        bot.send_message(message.chat.id, 'Бот для фитнес-студии', reply_markup=markup2)
        if name == '':
            bot.send_message(message.chat.id,
                             'Перед тем, как начать пользоваться ботом, пожалуйста, укажите свои полные фамилию, имя и отчество.')
            bot.register_next_step_handler(message, new_name)


@bot.message_handler(content_types=['text'])
def menu(message):
    user_id = message.from_user.id
    # если боту написал пользователь
    if user_id != var:
        user = User(user_id)
        if message.text == 'Записаться':
            user.sign_up_for_training(message)
        elif message.text == 'Отменить запись':
            user.cancel_registration_for_training(message)
        elif message.text == 'Личный кабинет':
            user.personal_account(message)
        elif message.text == 'Помощь':
            user.help(message)
    # если боту написал админ
    elif user_id == var:
        admin = Admin(user_id)
        if message.text == 'Добавить расписание':
            bot.send_message(message.chat.id, 'Введите сообщение в формате:\nдд-мм-гг_Направление_Тренер')
            bot.register_next_step_handler(message, lambda msg: admin.add_rasp(msg, msg.text.split('_')[0],
                                                                               msg.text.split('_')[1],
                                                                               msg.text.split('_')[2]))
        elif message.text == 'Абонементы':
            admin.subscription(message)
        elif message.text == 'Обновить прайс-лист':
            bot.send_message(message.chat.id, 'Пожалуйста, отправьте изображение обновлённого прайс-листа.')
            bot.register_next_step_handler(message, admin.update_price_list)


@bot.callback_query_handler(func=lambda callback: 'add_subscription' in callback.data)
def callback_add_subscription(callback):
    bot.send_message(callback.message.chat.id,
                     f'Введите ФИО нового посетителя и количество пополняемых занятий через запятую.\n\nПример: <b><i>Иванова Екатерина Александровна, 30</i></b>',
                     parse_mode='HTML')
    bot.register_next_step_handler(callback.message, add_subscription, callback)


@bot.callback_query_handler(func=lambda callback: 'replenish_subscription' in callback.data)
def callback_replenish_subscription(callback):
    bot.send_message(callback.message.chat.id,
                     'Введите ФИО посетителя, пополнившего абонемент, и количество приобретённых занятий через запятую.\n\nПример: <b><i>Иванова Екатерина Александровна, 30</i></b>',
                     parse_mode='HTML')
    bot.register_next_step_handler(callback.message, replenish_subscription, callback)


@bot.callback_query_handler(func=lambda callback: 'date-napr_' in callback.data)
def callback_cancel(callback):
    global name
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
                     f'Запись на {date}, "{napr}" успешно отменена.\nНа баланс Вашего абонемента было возвращено одно занятие.')
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
    data_parts = callback.data.split('_')
    date = data_parts[1]
    napr = data_parts[2]
    global name
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


def new_name(message):
    global name
    name = message.text
    bot.send_message(message.chat.id, 'Ваше имя успешно сохранено.')


def is_user_enter(name, date, napr):
    cursor = database.cursor()
    cursor.execute("SELECT * FROM classes WHERE date = ? AND napr = ? AND visitor= ?", (date, napr, name))
    result = cursor.fetchall()
    return len(result) > 0


# функция, которая вызывается при нажатии пользователем на кнопку "Записаться"
def sign_up_for_training(message):
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


# функция, которая вызывается при нажатии пользователем на кнопку "Отметить запись"
def cancel_registration_for_training(message):
    visitor = name
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


# функция, которая вызывается при нажатии пользователем на кнопку "Помощь"
def help(message):
    bot.send_message(message.chat.id, '''Инструкция по пользованию кнопками:
            \n\n«Записаться» 
        При нажатии на данную кнопку, Вам будет предложено выбрать удобный для Вас день для записи, после чего Вы сможете выбрать желаемое направление.
        После выбора направления Вы автоматически будете записаны на занятие, при этом со счёта Вашего абонемента будет списано одно занятие. 
            \n\n«Отменить занятие» 
        Данная опция позволяет осуществить отмену записи. Вы увидите перечень занятий, на которые записаны, и сможете нажать на любое из них для удаления записи. 
        При этом на счёт Вашего абонемента будет возвращено одно занятие.
            \n\n«Личный кабинет» 
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
    button1 = types.InlineKeyboardButton('Добавить абонемент', callback_data='add_subscription')
    button2 = types.InlineKeyboardButton('Пополнить абонемент', callback_data='replenish_subscription')
    markup_subscription.add(button1, button2)
    cursor.execute("SELECT visitor FROM subscription_inf WHERE subscription > 0")
    kol = len(cursor.fetchall())
    bot.send_message(message.chat.id, f'Количество активных абонентов: {kol}', reply_markup=markup_subscription)


def add_subscription(message, callback):
    try:
        visitor, kol = message.text.split(', ')
        cursor.execute("INSERT INTO subscription_inf (visitor, subscription) VALUES (?, ?)", (visitor, kol))
        database.commit()
        cursor.execute("SELECT * FROM subscription_inf")
        print(cursor.fetchall())
    except:
        bot.send_message(message.chat.id, "Данные введены некорректно. Попробуйте снова.")
        callback_add_subscription(callback)


def replenish_subscription(message, callback):
    try:
        visitor, kol = message.text.split(', ')
        cursor.execute("SELECT subscription FROM subscription_inf WHERE visitor = ?",
                       (visitor,))
        result = cursor.fetchone()
        if result is None:
            bot.send_message(message.chat.id, "Посетитель с таким именем не найден")
        else:
            new_subscription = result[0] + int(kol)
            cursor.execute("UPDATE subscription_inf SET subscription = ? WHERE visitor = ?",
                           (new_subscription, visitor))
        database.commit()
        cursor.execute("SELECT * FROM subscription_inf")
        print(cursor.fetchall())
    except:
        bot.send_message(message.chat.id, "Данные введены некорректно. Попробуйте снова.")
        callback_add_subscription(callback)




bot.polling(none_stop=True)
