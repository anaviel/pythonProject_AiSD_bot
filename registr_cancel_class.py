import sqlite3
from telebot import types
from datetime import datetime
from bot_start import bot


database = sqlite3.connect('rasp.db', check_same_thread=False)
cursor = database.cursor()


# функция, которая вызывается при нажатии пользователем на кнопку "Записаться"
def sign_up_for_training(message, user_id=None):
    cursor = database.cursor()
    if user_id is None:
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
    cursor = database.cursor()
    # Вывод расписания
    cursor.execute("SELECT DISTINCT napr, coach FROM classes WHERE date = ? AND id = '-' AND visitor = '-'", (date,))
    rows_available = cursor.fetchall()
    cursor.execute("SELECT DISTINCT napr, coach FROM classes WHERE date = ? AND id = '-' AND visitor != '-'", (date,))
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


@bot.callback_query_handler(func=lambda callback: 'reg_' in callback.data)
def callback_reg(callback):
    bot.delete_message(callback.message.chat.id, callback.message.message_id)
    cursor = database.cursor()
    user_id = callback.from_user.id
    cursor.execute("SELECT visitor FROM subscription_inf WHERE id = ?", (user_id,))
    name = ''.join(cursor.fetchone())
    data_parts = callback.data.split('_')
    date = data_parts[1]
    napr = data_parts[2]
    if is_user_enter(user_id, date, napr):
        bot.send_message(callback.message.chat.id, f'Вы уже записаны на занятие {date} ({napr}).')
    else:
        cursor.execute("SELECT coach FROM classes WHERE date = ? AND napr = ?", (date, napr))
        coach = ''.join(cursor.fetchone())
        from database_editing import update_visitor
        update_visitor(date, napr, coach, user_id, name, cursor, database)
        cursor.execute("SELECT subscription FROM subscription_inf WHERE id = ? AND visitor = ?", (user_id, name))
        result = cursor.fetchone()
        new_subscription = result[0] - 1
        cursor.execute("UPDATE subscription_inf SET subscription = ? WHERE id = ? AND visitor = ?", (new_subscription, user_id, name))
        database.commit()
        bot.send_message(callback.message.chat.id,
                         f'Вы успешно записаны {date} на {napr}.\nС баланса Вашего абонемента было списано одно занятие.')


def is_user_enter(id, date, napr):
    cursor = database.cursor()
    cursor.execute("SELECT * FROM classes WHERE date = ? AND napr = ? AND id = ?", (date, napr, id))
    result = cursor.fetchall()
    cursor.close()
    return len(result) > 0


# функция, которая вызывается при нажатии пользователем на кнопку "Отметить запись"
def cancel_registration_for_training(message):
    user_id = message.from_user.id
    cursor.execute("SELECT date, napr FROM classes WHERE id = ?", (user_id,))
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


@bot.callback_query_handler(func=lambda callback: 'date-napr_' in callback.data)
def callback_cancel(callback):
    user_id = callback.from_user.id
    cursor.execute("SELECT visitor FROM subscription_inf WHERE id = ?", (user_id,))
    name = ''.join(cursor.fetchone())
    date_napr = callback.data.split('_')
    date = date_napr[1]
    napr = date_napr[2]
    cursor.execute("UPDATE classes SET id = '-', visitor = '-' WHERE date = ? AND napr = ?",
                   (date, napr))
    cursor.execute("SELECT subscription FROM subscription_inf WHERE id = ? AND visitor = ?",
                   (user_id, name))
    result = cursor.fetchone()
    new_subscription = result[0] + 1
    cursor.execute("UPDATE subscription_inf SET subscription = ? WHERE id = ? AND visitor = ?",
                   (new_subscription, user_id, name))
    database.commit()
    bot.send_message(callback.message.chat.id,
                     f'Запись на {date}, "{napr}" успешно отменена.'
                     f'\nНа баланс Вашего абонемента было возвращено одно занятие.')
    cursor.execute("SELECT * FROM classes")



