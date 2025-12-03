from fastapi import FastAPI
from app.routes import notifications
from app.database import engine, Base
from app.routes import webhook
from app.routes import status
from app.routes import alerts

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(notifications.router)
app.include_router(webhook.router)
app.include_router(status.router)
app.include_router(alerts.router)
