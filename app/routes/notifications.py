from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Notification
from app.schemas import NotificationCreate

router = APIRouter(
    prefix="/notifications",
    tags=["Notifications"]
)

@router.post("/")
def create_notification(notification: NotificationCreate, db: Session = Depends(get_db)):
    new_notification = Notification(
        title=notification.title,
        message=notification.message,
        user_id=notification.user_id
    )

    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    
    return {
        "message": "Notification created successfully",
        "notification": new_notification
    }
