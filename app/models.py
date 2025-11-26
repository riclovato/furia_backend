from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    message = Column(String, index=True)
    user_id = Column(Integer, index=True)
    created_at = Column(DateTime, default=datetime.now)