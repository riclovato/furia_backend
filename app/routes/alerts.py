from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Match, NotificationSubscription
from datetime import datetime, timedelta
import httpx
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"

router = APIRouter(prefix="/alerts", tags=["Alerts"])

@router.post("/send_pending")
def send_pending_alerts(db: Session = Depends(get_db)):
    """
    Envia alertas para partidas que começam daqui a 1 hora e ainda não foram marcadas como `notified`.
    Útil para testar manualmente. Em produção, agende essa função para rodar a cada minuto.
    """
    now = datetime.utcnow()
    target_start = now + timedelta(hours=1)

    # Procurar partidas cujo start_time esteja entre now e target_start
    matches = db.query(Match).filter(
        Match.notified == False,
        Match.start_time != None,
        Match.start_time <= target_start,
        Match.start_time > now
    ).all()

    if not matches:
        return {"message": "No matches to notify", "count": 0}

    subscribers = db.query(NotificationSubscription).filter_by(active=True).all()
    if not subscribers:
        return {"message": "No subscribers", "count": 0}

    sent = 0
    # Enviar via Telegram (sincrono aqui para simplificar - em produção use async)
    with httpx.Client() as client:
        for match in matches:
            text = (
                f"⏰ Notificação: FURIA joga em 1 hora!\n\n"
                f"Adversário: {match.opponent}\n"
                f"Evento: {match.event or '—'}\n"
                f"Início: {match.start_time.isoformat()} UTC\n"
                f"Link: {match.link or '—'}"
            )
            for sub in subscribers:
                try:
                    resp = client.post(TELEGRAM_API_URL, json={"chat_id": sub.telegram_id, "text": text})
                    resp.raise_for_status()
                    sent += 1
                except Exception as e:
                    # Se falhar ao enviar (usuário bloqueou o bot, id inválido, etc.), desativa assinatura
                    try:
                        sub.active = False
                        db.commit()
                    except:
                        db.rollback()
                    continue

            # marca como notificado
            match.notified = True
            db.commit()

    return {"message": "Alerts sent", "matches_notified": len(matches), "messages_sent": sent}
