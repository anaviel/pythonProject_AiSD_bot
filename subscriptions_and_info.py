import sqlite3
import os
from telebot import types
from bot_start import bot

database = sqlite3.connect('rasp.db', check_same_thread=False)
cursor = database.cursor()

# токен для PayMaster
#payment_token = '1744374395:TEST:76270d537750431c42bb'

# токен для ЮKassa
payment_token = '381764678:TEST:71355'


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


@bot.callback_query_handler(func=lambda callback: 'replenish_subscription' in callback.data)
def callback_replenish_subscription(callback):
    bot.send_message(callback.message.chat.id,
                     'Введите номер телефона, ФИО посетителя, пополнившего абонемент, и количество '
                     'приобретённых занятий через запятую.\n\n'
                     'Пример: <b><i>+79213421431, Иванова Екатерина Александровна, 30</i></b>',
                     parse_mode='HTML')
    bot.register_next_step_handler(callback.message, replenish_subscription, callback)


# функция, которая вызывается при нажатии пользователем на кнопку "Записаться на пробное занятие"
def trial_training(message):
    bot.send_invoice(message.chat.id, 'Пробное занятие', 'Покупка пробного занятия', 'invoice', payment_token, 'RUB',
                     [types.LabeledPrice('Покупка пробного занятия', 400 * 100)])


# Обработчик успешного платежа
@bot.message_handler(content_types=['successful_payment'])
def successful_payment(message):
    new_user_id = message.chat.id
    cursor.execute("UPDATE subscription_inf SET prob_inf = '+' WHERE id = ?", (new_user_id,))
    bot.send_message(message.chat.id, 'Оплата прошла успешно. Ждём вас на пробном занятии в нашей студии!')
