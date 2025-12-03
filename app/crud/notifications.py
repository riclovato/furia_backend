from sqlalchemy.orm import Session
from app.models.notification import Notification
from app.schemas.notification import NotificationCreate, NotificationUpdate


# -------------------------
# Create
# -------------------------
def create_notification(db: Session, data: NotificationCreate):
    new_notification = Notification(
        user_id=data.user_id,
        message=data.message,
        team=data.team,
        status=data.status,
        created_at=data.created_at
    )
    db.add(new_notification)
    db.commit()
    db.refresh(new_notification)
    return new_notification


# -------------------------
# Read - Get all
# -------------------------
def get_notifications(db: Session, skip: int = 0, limit: int = 50):
    return db.query(Notification).offset(skip).limit(limit).all()


# -------------------------
# Read - Get by ID
# -------------------------
def get_notification_by_id(db: Session, notification_id: int):
    return db.query(Notification).filter(Notification.id == notification_id).first()


# -------------------------
# Update
# -------------------------
def update_notification(db: Session, notification_id: int, data: NotificationUpdate):
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        return None
    
    for key, value in data.dict(exclude_unset=True).items():
        setattr(notification, key, value)

    db.commit()
    db.refresh(notification)
    return notification


# -------------------------
# Delete
# -------------------------
def delete_notification(db: Session, notification_id: int):
    notification = get_notification_by_id(db, notification_id)
    if not notification:
        return None
    
    db.delete(notification)
    db.commit()
    return True
