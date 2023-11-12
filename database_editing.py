import sqlite3
from datetime import datetime

database = sqlite3.connect('rasp.db', check_same_thread=False)
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


def update_visitor(date, napr, coach, visitor, cursor, database):
    # Замена 4-го параметра посетилеля на реального человека, когда он записывается
    cursor.execute("SELECT rowid FROM classes WHERE date = ? AND napr = ? AND coach = ? AND visitor = '-'",
                   (date, napr, coach))
    row = cursor.fetchone()
    cursor.execute("UPDATE classes SET visitor = ? WHERE rowid = ?",
                   (visitor, row[0]))
    cursor.execute("SELECT * FROM classes")
    database.commit()


def prob_classes(date, napr, coach, visitor):
    # Добавление информации о записи на пробное занятие в таблицу
    date_today = datetime.now().date()
    cursor.execute("INSERT INTO prob_classes (date_today, date, napr, coach, visitor) VALUES (?, ?, ?, ?, ?)",
                   (date_today, date, napr, coach, visitor))
    database.commit()


