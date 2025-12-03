from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class SubscriptionCreate(BaseModel):
    telegram_id: str

class SubscriptionResponse(BaseModel):
    id: int
    telegram_id: str
    active: bool

    class Config:
        orm_mode = True

class MatchCreate(BaseModel):
    match_id: str
    opponent: str
    event: Optional[str] = None
    start_time: Optional[datetime] = None  # enviar em ISO 8601 UTC
    link: Optional[str] = None
    format: Optional[str] = None

class MatchList(BaseModel):
    matches: List[MatchCreate]

class NotificationUserCreate(BaseModel):
    email: EmailStr

    class Config:
        from_attributes = True
