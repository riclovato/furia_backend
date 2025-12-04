from fastapi import FastAPI
from app.routes import notifications
from app.database import engine, Base
from app.routes import webhook
from app.routes import status
from app.routes import alerts
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.tasks.notifications import check_matches_and_notify


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

scheduler = AsyncIOScheduler()
scheduler.add_job(check_matches_and_notify, "interval", minutes=1)
scheduler.start()
