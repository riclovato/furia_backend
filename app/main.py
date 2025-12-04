from fastapi import FastAPI
from app.routes import notifications
from app.database import engine, Base
from app.routes import webhook
from app.routes import status
from app.routes import alerts


Base.metadata.create_all(bind=engine)


app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/")
async def home():
    return "🟡⚫ FURIA Bot Backend está online! ⚫🟡"

app.include_router(notifications.router)
app.include_router(webhook.router)
app.include_router(status.router)
app.include_router(alerts.router)
