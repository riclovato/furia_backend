from fastapi import FastAPI
from app.routes import notifications
from app.database import Base, engine

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(notifications.router)