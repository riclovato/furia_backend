from sqlalchemy.orm import Session
from app.models import NotificationUser
from app.schemas import NotificationUserCreate


def create_notification_user(db: Session, data: NotificationUserCreate):
    user = NotificationUser(email=data.email)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str):
    return db.query(NotificationUser).filter(
        NotificationUser.email == email
    ).first()
