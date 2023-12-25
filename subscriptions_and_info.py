from sqlalchemy import create_engine, func
from dotenv import load_dotenv, find_dotenv
import os
from database_editing import Classes, SubscriptionInfo, ProbClasses, Session
from telebot import types
from bot_start import bot
from registr_cancel_class import sign_up_for_training
from tabulate import tabulate
import matplotlib.pyplot as plt
from io import BytesIO

load_dotenv(find_dotenv())

engine = create_engine('sqlite:///rasp.db', echo=False)

# Токен для ЮKassa
payment_token = os.getenv('PAYMENT_TOKEN')


# функция, которая вызывается при нажатии пользователем на кнопку "Личный кабинет"
def personal_account(message):
    session = Session()
    user_id = message.from_user.id

    # Используем SQLAlchemy для выполнения запросов к базе данных
    name = session.query(SubscriptionInfo.visitor).filter_by(id=user_id).scalar()
    result = session.query(SubscriptionInfo.subscription).filter_by(visitor=name).scalar()
    dates_napr = session.query(Classes.date, Classes.napr).filter_by(id=user_id, visitor=name).all()

    classes = ''
    for date, napr in dates_napr:
        classes += f'\n    {date}  {napr}\n'

    image_file = os.listdir("images")
    if image_file:
        image_path = os.path.join("images", image_file[0])
        with open(image_path, 'rb') as photo:
            bot.send_photo(
                message.chat.id,
                photo,
                caption=f'🤍Уважаемая, {name}!\n\n    Количество занятий на балансе Вашего абонемента: '
                        f'{result}\n\n🎀Занятия, на которые Вы записаны:\n{classes}'
            )

    session.close()


# функция, которая вызывается при нажатии пользователем на кнопку "Помощь"
def help_(message):
    bot.send_message(message.chat.id, '''Инструкция по пользованию кнопками:
            \n\n🤍«Записаться»🤍 
        При нажатии на данную кнопку, Вам будет предложено выбрать удобный для Вас день для записи, после чего Вы сможете выбрать желаемое направление. 
        После выбора направления Вы автоматически будете записаны на занятие, при этом со счёта Вашего абонемента будет списано одно занятие. 
            \n\n🤍«Отменить занятие»🤍 
        Данная опция позволяет осуществить отмену записи. Вы увидите перечень занятий, на которые записаны, и сможете нажать на любое из них для удаления записи. 
        При этом на счёт Вашего абонемента будет возвращено одно занятие.
            \n\n🤍«Личный кабинет»🤍 
        При нажатии на данную кнопку Вы сможете посмотреть перечень занятий, на которые записались, а также баланс Вашего абонемента.
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
    session = Session()
    active_subscriptions = session.query(SubscriptionInfo.visitor).filter(SubscriptionInfo.subscription > 0).all()
    kol = len(active_subscriptions)
    markup_subscription = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Пополнить абонемент', callback_data='replenish_subscription')
    markup_subscription.add(button1)
    bot.send_message(message.chat.id, f'Количество активных абонементов: {kol}', reply_markup=markup_subscription)

    session.close()


@bot.callback_query_handler(func=lambda callback: 'replenish_subscription' in callback.data)
def callback_replenish_subscription(callback):
    bot.send_message(callback.message.chat.id,
                     'Введите номер телефона, ФИО посетителя, пополнившего абонемент, и количество '
                     'приобретённых занятий через запятую.\n\n'
                     'Пример: <b><i>+79213421431, Иванова Екатерина Александровна, 30</i></b>',
                     parse_mode='HTML')
    bot.register_next_step_handler(callback.message, replenish_subscription, callback)


def replenish_subscription(message, callback):
    session = Session()

    try:
        phone_number, visitor, kol = message.text.split(', ')
        subscription_info = session.query(SubscriptionInfo).filter_by(phone_number=phone_number,
                                                                      visitor=visitor).first()

        if subscription_info is None:
            bot.send_message(message.chat.id, "Посетитель с такими данными не найден")
        else:
            user_id = subscription_info.id
            bot.send_message(user_id, f"Уважаемая, {visitor}! Ваш абонемент был пополнен администратором. "
                                      f"В случае, если абонемент был приобретён впервые, перезапустите бот.")
            new_subscription = subscription_info.subscription + int(kol)
            subscription_info.subscription = new_subscription
            session.commit()
            bot.send_message(message.chat.id, "Абонемент пополнен.")

    except Exception as e:
        bot.send_message(message.chat.id, f"Данные введены некорректно. Попробуйте снова. Ошибка: {e}")
        callback_replenish_subscription(callback)

    finally:
        session.close()


# функция, которая вызывается при нажатии пользователем на кнопку "Записаться на пробное занятие"
def trial_training(message):
    bot.send_message(message.chat.id, 'Предлагаем приобрести пробное занятие по выгодной цене. '
                                      '\n\nСразу после оплаты у Вас появится возможность записаться на занятие.'
                                      '\n\n🤍Подробности уточняйте у администратора студии.')
    bot.send_invoice(message.chat.id, 'Пробное занятие', 'Покупка пробного занятия', 'invoice', payment_token, 'RUB',
                     [types.LabeledPrice('Покупка пробного занятия', 400 * 100)])


@bot.pre_checkout_query_handler(func=lambda query: True)
def process_pre_checkout_query(pre_checkout_query: types.PreCheckoutQuery):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


# Обработчик успешного платежа
@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    session = Session()

    new_user_id = message.chat.id
    subscription_info = session.query(SubscriptionInfo).filter_by(id=new_user_id).first()
    subscription_info.prob_inf = '+'
    subscription_info.subscription = 1
    session.commit()
    bot.send_message(new_user_id, 'Оплата прошла успешно. Ждём вас на пробном занятии в нашей студии!')
    from database_editing import prob_classes
    prob_classes(new_user_id)
    sign_up_for_training(message)

    session.close()


# функция, которая вызывается при нажатии админом на кнопку "Таблицы"
def display_tables(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Расписание', callback_data='show_the_rasp')
    button2 = types.InlineKeyboardButton('Абонементы', callback_data='show_the_ab')
    button3 = types.InlineKeyboardButton('Пробные занятия', callback_data='show_the_prob')
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, "Выберите таблицу:", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: 'show_the_rasp' in callback.data)
def callback_show_the_rasp(callback):
    session = Session()
    classes_data = session.query(Classes.date, Classes.napr, Classes.coach, Classes.visitor).all()

    if classes_data:
        headers = ["Дата", "Направление", "Тренер", "Посетитель"]
        data = [list(row) for row in classes_data]
        table_rasp = tabulate(data, headers, tablefmt="pretty")

        with open("Расписание.txt", "w", encoding="utf-8") as file:
            file.write(table_rasp)

        with open("Расписание.txt", "rb") as file:
            bot.send_document(callback.message.chat.id, file)

    session.close()


@bot.callback_query_handler(func=lambda callback: 'show_the_ab' in callback.data)
def callback_show_the_ab(callback):
    session = Session()

    subscriptions_data = session.query(Classes.date, Classes.napr, Classes.coach, Classes.visitor).all()

    if subscriptions_data:
        headers_subscriptions = ["ID", "Посетитель", "Телефон", "Абонемент"]
        data_subscriptions = [list(row) for row in subscriptions_data]
        table_subscriptions = tabulate(data_subscriptions, headers_subscriptions, tablefmt="pretty")

        with open("Абонементы.txt", "w", encoding="utf-8") as file:
            file.write(table_subscriptions)

        with open("Абонементы.txt", "rb") as file:
            bot.send_document(callback.message.chat.id, file)

    session.close()


@bot.callback_query_handler(func=lambda callback: 'show_the_prob' in callback.data)
def callback_show_the_prob(callback):
    session = Session()

    prob_data = session.query(Classes.date, Classes.napr, Classes.coach, Classes.visitor).all()

    if prob_data:
        headers_prob = ["Дата", "ID", "Посетитель"]
        data_prob = [list(row) for row in prob_data]
        table_prob = tabulate(data_prob, headers_prob, tablefmt="pretty")

        with open("Пробные занятия.txt", "w", encoding="utf-8") as file:
            file.write(table_prob)

        with open("Пробные занятия.txt", "rb") as file:
            bot.send_document(callback.message.chat.id, file)

    session.close()


def dashboard(message):

    loading_message = bot.send_message(message.chat.id, "Загрузка...")

    session = Session()

    # Запрос для получения данных о загруженности тренеров
    data_with_visitor = session.query(Classes.coach, func.count(Classes.visitor)
                                      .label('count')).filter(Classes.visitor != '-').group_by(Classes.coach).all()


    # Извлечение данных из результата запроса
    coaches = [row[0] for row in data_with_visitor]
    counts_with_visitor = [row[1] for row in data_with_visitor]

    # Создание первого графика (загруженность тренеров)
    fig1, ax1 = plt.subplots()
    ax1.bar(coaches, counts_with_visitor, color='green')
    ax1.set_xlabel('Тренеры')
    ax1.set_ylabel('Количество записавшихся')
    plt.title('Загруженность тренеров с учетом идентификатора посетителя')

    # Поворот имен тренеров для лучшей читаемости
    ax1.tick_params(axis='x', rotation=0)

    # Сохранение графика в байтовый объект
    image_stream1 = BytesIO()
    plt.savefig(image_stream1, format='png')
    image_stream1.seek(0)

    # Закрытие графика
    plt.close()

    # Запрос для получения данных о частоте приобретения пробных занятий по дням
    data_prob = session.query(ProbClasses.date_today, func.count(ProbClasses.visitor)
                              .label('prob_count')).group_by(ProbClasses.date_today).all()


    # Извлечение данных из результата запроса
    dates_prob = [row[0] for row in data_prob]
    prob_counts = [row[1] for row in data_prob]

    # Создание второго графика (частота пробных занятий по дням)
    fig2, ax2 = plt.subplots()
    ax2.plot(dates_prob, prob_counts, color='blue', marker='x')
    ax2.set_xlabel('Дни')
    ax2.set_ylabel('Частота пробных занятий')
    plt.title('Частота приобретения пробных занятий по дням')

    # Поворот дат для лучшей читаемости
    ax2.tick_params(axis='x', rotation=45)

    # Избегаем обрезания
    plt.tight_layout()

    # Сохранение второго графика в байтовый объект
    image_stream2 = BytesIO()
    plt.savefig(image_stream2, format='png')
    image_stream2.seek(0)

    # Закрытие второго графика
    plt.close()

    # Отправка графика как фотографии
    bot.send_photo(message.chat.id, photo=image_stream1)

    # Удаляем предыдущее сообщение о загрузке
    bot.delete_message(message.chat.id, loading_message.message_id)

    # Отправка второго графика как фотографии
    bot.send_photo(message.chat.id, photo=image_stream2)

    session.close()
