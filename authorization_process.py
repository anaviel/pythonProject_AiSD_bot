import sqlite3
from bot_start import bot


database = sqlite3.connect('rasp.db', check_same_thread=False)
cursor = database.cursor()


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
    from main import NewUser
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
        id_ = ''.join(cursor.fetchone())
        if id_ != str(user_id):
            bot.send_message(message.chat.id, f'Ваш номер существует в базе, но Ваш аккаунт к нему не привязан. '
                                              f'Обратитесь к администратору за дальнейшей инструкцией.')
        bot.send_message(message.chat.id, f'Здравствуйте, {name_visitor}! Вы успешно авторизовались.')
        cursor.execute("SELECT prob_inf FROM subscription_inf WHERE id = ?",
                       (user_id,))
        from main import User, NewUser
        if ''.join(cursor.fetchone()) == '+':
            user = User(user_id)
            # показываем клавиатуру для пользователя
            user.keyboard_user(message)
        else:
            new_user = NewUser(user_id)
            # показываем клавиатуру для нового пользователя
            new_user.keyboard_new_user(message)
    else:
        bot.send_message(message.chat.id, 'К сожалению, номер не найден. Проверьте правильность введённых'
                                          'данных или обратитесь к службе поддержки.')
        from main import start
        start()
