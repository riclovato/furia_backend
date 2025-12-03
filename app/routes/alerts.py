from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Notification
from app.schemas import NotificationCreate

router = APIRouter(prefix="/alert", tags=["Alerts"])

@router.post("/")
async def register_alert(alert: NotificationCreate, db: Session = Depends(get_db)):
    new_alert = Notification(
        title=alert.title,
        message=alert.message,
        user_id=alert.user_id
    )

    db.add(new_alert)
    db.commit()
    db.refresh(new_alert)

    return {
        "message": "Alert registered successfully",
        "alert": new_alert
    }
