from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import NotificationUserCreate
from app.crud.notification_users import (
    create_notification_user,
    get_user_by_email
)

router = APIRouter(prefix="/notification-users", tags=["Notification Users"])


@router.post("/")
def register_user(data: NotificationUserCreate, db: Session = Depends(get_db)):
    existing = get_user_by_email(db, data.email)
    if existing:
        return {"message": "User already registered", "user": existing}

    user = create_notification_user(db, data)
    return {"message": "User registered", "user": user}
