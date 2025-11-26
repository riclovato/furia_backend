from fastapi import FastAPI
from app.routes import notifications
from app.database import engine, Base

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(notifications.router)