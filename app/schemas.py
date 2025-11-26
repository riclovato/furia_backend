from pydantic import BaseModel

class NotificationCreate(BaseModel):
    title: str
    message: str
    user_id: int