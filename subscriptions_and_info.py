import sqlite3
from telebot import types
from bot_start import bot
from registr_cancel_class import sign_up_for_training
from tabulate import tabulate
import matplotlib.pyplot as plt
from io import BytesIO
from dotenv import load_dotenv, find_dotenv
import os

load_dotenv(find_dotenv())

database = sqlite3.connect('rasp.db', check_same_thread=False)
cursor = database.cursor()

# токен для ЮKassa
payment_token = os.getenv('PAYMENT_TOKEN')


# функция, которая вызывается при нажатии пользователем на кнопку "Личный кабинет"
def personal_account(message):
    cursor = database.cursor()
    user_id = message.from_user.id
    cursor.execute("SELECT visitor FROM subscription_inf WHERE id = ?", (user_id,))
    name = ''.join(cursor.fetchone())
    cursor.execute("SELECT subscription FROM subscription_inf WHERE visitor = ?",
                   (name,))
    result = cursor.fetchone()[0]
    cursor.execute("SELECT date, napr FROM classes WHERE id = ? AND visitor = ?", (user_id, name))
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
                           caption=f'🤍Уважаемая, {name}!\n\n    Количество занятий на балансе Вашего абонемента: '
                                   f'{result}\n\n🎀Занятия, на которые Вы записаны:\n{classes}')
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
    markup_subscription = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Пополнить абонемент', callback_data='replenish_subscription')
    markup_subscription.add(button1)
    cursor.execute("SELECT visitor FROM subscription_inf WHERE subscription > 0")
    kol = len(cursor.fetchall())
    bot.send_message(message.chat.id, f'Количество активных абонементов: {kol}', reply_markup=markup_subscription)


@bot.callback_query_handler(func=lambda callback: 'replenish_subscription' in callback.data)
def callback_replenish_subscription(callback):
    bot.send_message(callback.message.chat.id,
                     'Введите номер телефона, ФИО посетителя, пополнившего абонемент, и количество '
                     'приобретённых занятий через запятую.\n\n'
                     'Пример: <b><i>+79213421431, Иванова Екатерина Александровна, 30</i></b>',
                     parse_mode='HTML')
    bot.register_next_step_handler(callback.message, replenish_subscription, callback)


def replenish_subscription(message, callback):
    try:
        phone_number, visitor, kol = message.text.split(', ')
        cursor.execute("SELECT subscription FROM subscription_inf WHERE phone_number = ? AND visitor = ?",
                       (phone_number, visitor))
        result = cursor.fetchone()
        if result is None:
            bot.send_message(message.chat.id, "Посетитель с такими данными не найден")
        else:
            cursor.execute("SELECT id FROM subscription_inf WHERE phone_number = ? AND visitor = ?",
                           (phone_number, visitor))
            user_id = ''.join(cursor.fetchone())
            bot.send_message(user_id, f"Уважаемая, {visitor}! Ваш абонемент был пополнен администратором. "
                                      f"В случае, если абонемент был приобретён впервые, перезапустите бот.")
            new_subscription = result[0] + int(kol)
            cursor.execute("UPDATE subscription_inf SET subscription = ? WHERE visitor = ?",
                           (new_subscription, visitor))
            bot.send_message(message.chat.id, "Абонемент пополнен.")
        database.commit()
        cursor.execute("SELECT * FROM subscription_inf")
    except:
        bot.send_message(message.chat.id, "Данные введены некорректно. Попробуйте снова.")
        callback_replenish_subscription(callback)


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
    new_user_id = message.chat.id
    cursor.execute("UPDATE subscription_inf SET prob_inf = '+', subscription = 1 WHERE id = ?", (new_user_id,))
    database.commit()
    bot.send_message(message.chat.id, 'Оплата прошла успешно. Ждём вас на пробном занятии в нашей студии!')
    from database_editing import prob_classes
    prob_classes(new_user_id)
    sign_up_for_training(message)


# функция, которая вызывается при нажатии админом на кнопку "Таблицы"
def display_tables(message):
    cursor.execute("SELECT * FROM classes")
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton('Расписание', callback_data='show_the_rasp')
    button2 = types.InlineKeyboardButton('Абонементы', callback_data='show_the_ab')
    button3 = types.InlineKeyboardButton('Пробные занятия', callback_data='show_the_prob')
    markup.add(button1, button2, button3)
    bot.send_message(message.chat.id, "Выберите таблицу:", reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: 'show_the_rasp' in callback.data)
def callback_show_the_rasp(callback):
    cursor.execute("SELECT date, napr, coach, visitor FROM classes")
    rows = cursor.fetchall()

    if rows:
        headers = ["Дата", "Направление", "Тренер", "Посетитель"]
        data = [list(row) for row in rows]
        table_rasp = tabulate(data, headers, tablefmt="pretty")

        with open("Расписание.txt", "w", encoding="utf-8") as file:
            file.write(table_rasp)

        with open("Расписание.txt", "rb") as file:
            bot.send_document(callback.message.chat.id, file)


@bot.callback_query_handler(func=lambda callback: 'show_the_ab' in callback.data)
def callback_show_the_ab(callback):
    cursor.execute("SELECT * FROM subscription_inf")
    rows_subscriptions = cursor.fetchall()

    if rows_subscriptions:
        headers_subscriptions = ["ID", "Посетитель", "Телефон", "Абонемент"]
        data_subscriptions = [list(row) for row in rows_subscriptions]
        table_subscriptions = tabulate(data_subscriptions, headers_subscriptions, tablefmt="pretty")

        with open("Абонементы.txt", "w", encoding="utf-8") as file:
            file.write(table_subscriptions)

        with open("Абонементы.txt", "rb") as file:
            bot.send_document(callback.message.chat.id, file)


@bot.callback_query_handler(func=lambda callback: 'show_the_prob' in callback.data)
def callback_show_the_prob(callback):
    cursor.execute("SELECT * FROM prob_classes")
    rows_prob = cursor.fetchall()

    if rows_prob:
        headers_prob = ["Дата", "ID", "Посетитель"]
        data_prob = [list(row) for row in rows_prob]
        table_prob = tabulate(data_prob, headers_prob, tablefmt="pretty")

        with open("Пробные занятия.txt", "w", encoding="utf-8") as file:
            file.write(table_prob)

        with open("Пробные занятия.txt", "rb") as file:
            bot.send_document(callback.message.chat.id, file)


def dashboard(message):

    loading_message = bot.send_message(message.chat.id, "Загрузка...")

    # Запрос для получения данных о загруженности тренеров
    cursor.execute("""
        SELECT coach, COUNT(visitor) as count
        FROM classes
        WHERE visitor != '-'
        GROUP BY coach
    """)
    data_with_visitor = cursor.fetchall()

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
    cursor.execute("""
        SELECT date_today, COUNT(visitor) as prob_count
        FROM prob_classes
        GROUP BY date_today
    """)
    data_prob = cursor.fetchall()

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
