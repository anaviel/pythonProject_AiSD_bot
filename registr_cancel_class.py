from sqlalchemy import create_engine, distinct
from datetime import datetime
from telebot import types
from bot_start import bot
from database_editing import Classes, SubscriptionInfo, Session


engine = create_engine('sqlite:///rasp.db', echo=False)

# Словарь для хранения текущей страницы
pages_registr = {}


# функция, которая вызывается при нажатии пользователем на кнопку "Записаться"
def sign_up_for_training(message, user_id=None):
    session = Session()

    if user_id is None:
        user_id = message.from_user.id
    subscription = session.query(SubscriptionInfo.subscription).filter_by(id=user_id).scalar()

    if subscription:
        if subscription > 0:
            dates_ = session.query(distinct(Classes.date)).all()
            dates = []
            for row in dates_:
                if row[0] not in dates:
                    dates.append(row[0])

            # Получение текущей страницы пользователя
            current_page = pages_registr.get(user_id, 0)

            # Количество элементов на одной странице
            items_per_page = 5
            start_index = current_page * items_per_page
            end_index = start_index + items_per_page

            # Формирование клавиатуры с датами на текущей странице
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            for date in dates[start_index:end_index]:
                butt = 'date:' + date
                button = types.InlineKeyboardButton(text=date, callback_data=butt)
                keyboard.add(button)

            # Добавление кнопок "Вперёд" и "Назад"
            if current_page > 0:
                prev_button = types.InlineKeyboardButton(text='Назад', callback_data='prev_page_3')
                keyboard.row(prev_button)
            if end_index < len(dates):
                next_button = types.InlineKeyboardButton(text='Вперёд', callback_data='next_page_3')
                keyboard.row(next_button)
            bot.send_message(message.chat.id, 'Выберите день:', reply_markup=keyboard)
        else:
            bot.send_message(message.chat.id,
                             "Вы не можете записаться на занятие, так как у вас закончился абонемент.\n"
                             "Вам необходимо обратиться к администратору в студии для его пополнения.")
    else:
        bot.send_message(message.chat.id, "Произошла ошибка. К сожалению, невозможно записаться на занятие.")

    session.close()


# Обработка нажатий кнопок "Вперёд" и "Назад"
@bot.callback_query_handler(func=lambda callback: callback.data in ['prev_page_3', 'next_page_3'])
def callback_pagination(callback):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    user_id = callback.from_user.id
    current_page = pages_registr.get(user_id, 0)

    if callback.data == 'prev_page_3':
        current_page = max(0, current_page - 1)
    elif callback.data == 'next_page_3':
        current_page += 1

    pages_registr[user_id] = current_page

    # Вызов функции, которая формирует и отправляет клавиатуру
    sign_up_for_training(callback.message, user_id)


@bot.callback_query_handler(func=lambda callback: 'date:' in callback.data)
def callback_dates_show(callback):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
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
    back_button = types.InlineKeyboardButton("Назад", callback_data="back_to_sign_up")
    markup.add(back_button)
    bot.send_message(callback.message.chat.id, rasp_str, reply_markup=markup)


@bot.callback_query_handler(func=lambda callback: "back_to_sign_up" in callback.data)
def callback_back(callback):
    user_id = callback.from_user.id
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    sign_up_for_training(callback.message, user_id)


def rasp_show(date):
    session = Session()

    now = datetime.now()

    rows_available = session.query(distinct(Classes.napr), Classes.coach).filter(
        Classes.date == str(date),
        Classes.id == '-',
        Classes.visitor == '-'
    ).all()

    full_classes = session.query(distinct(Classes.napr), Classes.coach).filter(
        Classes.date == str(date),
        Classes.id != '-',
        Classes.visitor != '-'
    ).all()

    rows_unavailable = list(set(full_classes) - set(rows_available))

    rasp_list_available = []
    rasp_list_unavailable = []

    for row in rows_available:
        napr, coach = row
        if now < datetime.strptime(f"{date} {napr[:5]}", "%d-%m-%Y %H:%M"):
            rasp_list_available.append(f"🤍{napr}, тренер: {coach}")

    for row in rows_unavailable:
        napr, coach = row
        full_date = date + ' ' + napr[:5]
        print(now, datetime.strptime(full_date, "%d-%m-%Y %H:%M"))
        if now < datetime.strptime(full_date, "%d-%m-%Y %H:%M"):
            rasp_list_unavailable.append(f"🤍{napr}, тренер: {coach} (❌На данное занятие мест уже нет!)")

    session.close()

    return rasp_list_available, rasp_list_unavailable


@bot.callback_query_handler(func=lambda callback: 'reg_' in callback.data)
def callback_reg(callback):
    session = Session()

    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    user_id = callback.from_user.id

    subscription = session.query(SubscriptionInfo).filter_by(id=user_id).first()

    if subscription and subscription.subscription > 0:
        data_parts = callback.data.split('_')
        date = data_parts[1]
        napr = data_parts[2]

        coach = (session.query(Classes.coach).filter_by(date=date, napr=napr).first())[0]

        from database_editing import update_visitor
        update_visitor(date, napr, coach, user_id, subscription.visitor)

        result = session.query(SubscriptionInfo.subscription).filter_by(id=user_id,
                                                                        visitor=subscription.visitor).scalar()
        new_subscription = result - 1

        session.query(SubscriptionInfo).filter_by(id=user_id, visitor=subscription.visitor).update({
            SubscriptionInfo.subscription: new_subscription
        })

        session.commit()

        bot.send_message(callback.message.chat.id,
                         f'Вы успешно записаны {date} на {napr}.\nС баланса Вашего абонемента было списано одно занятие.')
    else:
        bot.send_message(callback.message.chat.id, 'У вас недостаточно занятий на абонементе.')

    session.close()


def is_user_enter(id, date, napr):
    session = Session()

    result = session.query(Classes).filter_by(date=date, napr=napr, id=id).all()

    session.close()

    return len(result) > 0


# функция, которая вызывается при нажатии пользователем на кнопку "Отметить запись"
def cancel_registration_for_training(message):
    session = Session()

    user_id = message.from_user.id
    dates_napr_ = session.query(Classes.date, Classes.napr).filter_by(id=user_id).all()
    markup = types.InlineKeyboardMarkup()

    for date, napr in dates_napr_:
        butt = 'date-napr_' + date + '_' + napr
        name_butt = date + ' ' + napr
        button = types.InlineKeyboardButton(name_butt, callback_data=butt)
        markup.add(button)

    bot.send_message(message.chat.id, 'Какое направление хотите отменить?', reply_markup=markup)

    session.close()


@bot.callback_query_handler(func=lambda callback: 'date-napr_' in callback.data)
def callback_cancel(callback):
    session = Session()

    user_id = callback.from_user.id
    name = session.query(SubscriptionInfo.visitor).filter_by(id=user_id).scalar()
    date_napr = callback.data.split('_')
    date = date_napr[1]
    napr = date_napr[2]
    session.query(Classes).filter_by(date=date, napr=napr).update({
        Classes.id: '-',
        Classes.visitor: '-'
    })
    result = session.query(SubscriptionInfo.subscription).filter_by(id=user_id, visitor=name).scalar()
    new_subscription = result + 1
    session.query(SubscriptionInfo).filter_by(id=user_id, visitor=name).update({
        SubscriptionInfo.subscription: new_subscription
    })
    session.commit()
    bot.send_message(callback.message.chat.id,
                     f'Запись на {date}, "{napr}" успешно отменена.'
                     f'\nНа баланс Вашего абонемента было возвращено одно занятие.')

    session.close()

