from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import NotificationSubscription
from app.schemas import SubscriptionCreate, SubscriptionResponse

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.post("/subscribe", response_model=SubscriptionResponse)
def subscribe(sub: SubscriptionCreate, db: Session = Depends(get_db)):
    # evitar duplicatas: reativar se existir
    existing = db.query(NotificationSubscription).filter_by(telegram_id=sub.telegram_id).first()
    if existing:
        existing.active = True
        db.commit()
        db.refresh(existing)
        return existing

    new = NotificationSubscription(telegram_id=sub.telegram_id, active=True)
    db.add(new)
    db.commit()
    db.refresh(new)
    return new

@router.post("/unsubscribe", response_model=SubscriptionResponse)
def unsubscribe(sub: SubscriptionCreate, db: Session = Depends(get_db)):
    existing = db.query(NotificationSubscription).filter_by(telegram_id=sub.telegram_id).first()
    if not existing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Subscription not found")

    existing.active = False
    db.commit()
    db.refresh(existing)
    return existing
