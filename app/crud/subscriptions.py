from sqlalchemy.orm import Session
from app.models import NotificationSubscription
from app.schemas import SubscriptionCreate


def create_subscription(db: Session, data: SubscriptionCreate):
    subscription = NotificationSubscription(
        telegram_id=data.telegram_id,
        active=True
    )
    db.add(subscription)
    db.commit()
    db.refresh(subscription)
    return subscription


def get_subscription_by_telegram_id(db: Session, telegram_id: str):
    return db.query(NotificationSubscription).filter(
        NotificationSubscription.telegram_id == telegram_id
    ).first()


def deactivate_subscription(db: Session, telegram_id: str):
    subscription = get_subscription_by_telegram_id(db, telegram_id)
    if not subscription:
        return None

    subscription.active = False
    db.commit()
    db.refresh(subscription)
    return subscription
