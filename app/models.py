from sqlalchemy import Column, Integer, String, DateTime, BigInteger
from datetime import datetime
from app.database import Base

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    message = Column(String, index=True)
    user_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.now)



class TelegramUser(Base):
    __tablename__ = "telegram_users"

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(BigInteger, unique=True, index=True)
    username = Column(String)
    first_name = Column(String)
    last_name = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)