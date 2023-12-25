import sqlite3
from datetime import datetime
from sqlalchemy import create_engine, Column, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///rasp.db', echo=False)
Base = declarative_base()
Session = sessionmaker(bind=engine)


class Classes(Base):
    __tablename__ = 'classes'
    date = Column(String)
    napr = Column(String)
    coach = Column(String)
    id = Column(String, primary_key=True)
    visitor = Column(String)


class ProbClasses(Base):
    __tablename__ = 'prob_classes'
    date_today = Column(String)
    id = Column(String, primary_key=True)
    visitor = Column(String)


class SubscriptionInfo(Base):
    __tablename__ = 'subscription_inf'
    id = Column(String, primary_key=True)
    phone_number = Column(String)
    visitor = Column(String)
    prob_inf = Column(String)
    subscription = Column(String)


def insert_rasp(date, napr, coach, id='-', visitor='-'):
    # Добавление расписания
    session = Session()

    new_class = Classes(date=date, napr=napr, coach=coach, id=id, visitor=visitor)
    session.add(new_class)
    session.commit()

    session.close()


def update_visitor(date, napr, coach, id, visitor):
    # Замена 4-го параметра посетилеля на реального человека, когда он записывается
    database = sqlite3.connect('rasp.db', check_same_thread=False)
    cursor = database.cursor()
    cursor.execute("SELECT rowid FROM classes WHERE date = ? AND napr = ? AND coach = ? AND id = '-' AND visitor = '-'",
                   (date, napr, coach))
    row = cursor.fetchone()
    cursor.execute("UPDATE classes SET id = ?, visitor = ? WHERE rowid = ?",
                   (id, visitor, row[0]))
    cursor.execute("SELECT * FROM classes")
    database.commit()


def prob_classes(user_id):
    # Добавление информации о записи на пробное занятие в таблицу
    session = Session()

    subscription_info = session.query(SubscriptionInfo.visitor).filter(SubscriptionInfo.id == str(user_id)).first()
    if subscription_info:
        visitor = subscription_info[0]
        date_today = datetime.now().date()
        new_prob_class = ProbClasses(date_today=date_today, id=user_id, visitor=visitor)
        session.add(new_prob_class)
        session.commit()

    session.close()
