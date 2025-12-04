from fastapi import FastAPI
from app.routes import notifications
from app.database import engine, Base
from app.routes import webhook
from app.routes import status
from app.routes import alerts
from flask import Flask

Base.metadata.create_all(bind=engine)
flask_app = Flask(__name__)

@flask_app.route('/health')
def health():
    return {"status": "ok"}

@flask_app.route('/')
def home():
    return "🟡⚫ FURIA Bot Backend está online! ⚫🟡", 200

def run_flask():
    flask_app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 8080)))

app = FastAPI()

app.include_router(notifications.router)
app.include_router(webhook.router)
app.include_router(status.router)
app.include_router(alerts.router)
