from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class NotificationSubscription(Base):
    __tablename__ = "notification_subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String, index=True, nullable=False)
    active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    match_id = Column(String, unique=True, index=True, nullable=False)  # id gerado pelo bot (hash)
    opponent = Column(String, nullable=False)
    event = Column(String, nullable=True)
    start_time = Column(DateTime, nullable=True)  # armazenar em UTC
    link = Column(Text, nullable=True)
    format = Column(String, nullable=True)
    notified = Column(Boolean, default=False)  # se já enviou notificação de 1h
    created_at = Column(DateTime, default=datetime.utcnow)

class NotificationUser(Base):
    __tablename__ = "notification_users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
