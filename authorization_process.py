from bot_start import bot
from sqlalchemy import create_engine
from database_editing import SubscriptionInfo, Session

engine = create_engine('sqlite:///rasp.db', echo=False)


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
    session = Session()

    # Добавляем в таблицу с абонементами запись о новом пользователе
    user_id = message.from_user.id
    phone_number = message.text.split(' ')[0]
    visitor_name = ' '.join(message.text.split(' ')[1:])
    prob_inf = '-'
    subscription_ = 0
    # Используем ORM для добавления записи
    new_subscription = SubscriptionInfo(id=user_id, phone_number=phone_number, visitor=visitor_name,
                                        prob_inf=prob_inf, subscription=subscription_)
    session.add(new_subscription)
    session.commit()
    from main import NewUser
    new_user = NewUser(user_id)
    # показываем клавиатуру для нововго пользователя
    new_user.keyboard_new_user(message)

    session.close()


def check_number(message):
    # Авторизация по номеру
    session = Session()

    user_id = message.from_user.id
    phone_number = message.text

    # Используем ORM для выполнения SQL-запросов
    subscription_info = session.query(SubscriptionInfo).filter(SubscriptionInfo.phone_number
                                                               == str(phone_number)).first()

    if subscription_info:
        name_visitor = subscription_info.visitor

        if subscription_info.id != str(user_id):
            bot.send_message(message.chat.id, f'Ваш номер существует в базе, но Ваш аккаунт к нему не привязан. '
                                              f'Обратитесь к администратору за дальнейшей инструкцией.')
            return

        bot.send_message(message.chat.id, f'Здравствуйте, {name_visitor}! Вы успешно авторизовались.')

        if subscription_info.prob_inf == '+':
            from main import User
            user = User(user_id)
            # показываем клавиатуру для пользователя
            user.keyboard_user(message)
        else:
            from main import NewUser
            new_user = NewUser(user_id)
            # показываем клавиатуру для нового пользователя
            new_user.keyboard_new_user(message)
    else:
        bot.send_message(message.chat.id, 'К сожалению, номер не найден. Проверьте правильность введённых'
                                          'данных или обратитесь к службе поддержки.')
        from main import start
        start()

    session.close()
