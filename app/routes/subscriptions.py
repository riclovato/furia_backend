from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import SubscriptionCreate, SubscriptionResponse
from app.crud.subscriptions import (
    create_subscription,
    get_subscription_by_telegram_id,
    deactivate_subscription
)

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions"])


@router.post("/", response_model=SubscriptionResponse)
def subscribe(data: SubscriptionCreate, db: Session = Depends(get_db)):
    existing = get_subscription_by_telegram_id(db, data.telegram_id)

    if existing:
        if existing.active:
            return existing  # já está ativado
        # se existe, mas está desativado → reativa
        existing.active = True
        db.commit()
        db.refresh(existing)
        return existing

    # cria novo
    subscription = create_subscription(db, data)
    return subscription


@router.post("/deactivate/{telegram_id}")
def unsubscribe(telegram_id: str, db: Session = Depends(get_db)):
    result = deactivate_subscription(db, telegram_id)
    if not result:
        return {"error": "User not found"}

    return {"message": "Subscription deactivated"}
