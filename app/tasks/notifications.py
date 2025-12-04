from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models import Match, NotificationSubscription
import httpx
import os

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


async def check_matches_and_notify():
    db: Session = SessionLocal()

    try:
        now = datetime.utcnow()

        # Buscar partidas futuras que ainda não foram notificadas
        matches = (
            db.query(Match)
            .filter(Match.start_time != None)
            .filter(Match.notified == False)
            .all()
        )

        for match in matches:
            if match.start_time - timedelta(hours=1) <= now < match.start_time:
                
                # pegar usuários inscritos
                users = db.query(NotificationSubscription).filter_by(active=True).all()

                for user in users:

                    text = (
                        f"⏰ <b>Partida em 1 hora!</b>\n\n"
                        f"🏆 Evento: {match.event}\n"
                        f"🆚 Adversário: {match.opponent}\n"
                        f"⏰ Horário: {match.start_time.strftime('%d/%m/%Y %H:%M')} (UTC)\n"
                        f"🔗 {match.link}"
                    )

                    async with httpx.AsyncClient() as client:
                        await client.post(
                            TELEGRAM_URL,
                            json={
                                "chat_id": user.telegram_id,
                                "text": text,
                                "parse_mode": "HTML",
                                "disable_web_page_preview": True
                            }
                        )

                # marcar como notificado
                match.notified = True
                db.commit()

    except Exception as e:
        print("Erro ao checar notificações:", e)

    finally:
        db.close()
