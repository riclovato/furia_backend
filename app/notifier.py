# app/notifier.py
import os
import logging
from datetime import datetime, timedelta, timezone

import httpx
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from fastapi import FastAPI

from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.database import SessionLocal, engine  # seu session factory
from app.models import Match, NotificationSubscription  # ajuste se o módulo for diferente

logger = logging.getLogger("backend.notifier")
logger.setLevel(logging.INFO)

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")  # obrigatória
if not TELEGRAM_BOT_TOKEN:
    logger.warning("TELEGRAM_BOT_TOKEN não definido — o notifier não enviará mensagens.")

# Intervalo em segundos entre checagens (1 minuto por padrão)
CHECK_INTERVAL_SECONDS = int(os.getenv("NOTIFIER_INTERVAL_SECONDS", "60"))

# Quanto antes do início consideramos para enviar notificação (1 hora = 60 minutos)
NOTIFY_BEFORE_MINUTES = int(os.getenv("NOTIFY_BEFORE_MINUTES", "60"))

TELEGRAM_SEND_URL = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"


def _get_db() -> Session:
    """
    Retorna uma sessão SQLAlchemy. Use em blocos try/finally.
    """
    db = SessionLocal()
    return db


async def send_message_to_telegram(telegram_id: str, text: str, parse_mode: str = "HTML"):
    """
    Envia mensagem via HTTP para a API do Telegram (httpx Async).
    """
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Não há TELEGRAM_BOT_TOKEN definido — pulando envio.")
        return

    payload = {
        "chat_id": str(telegram_id),
        "text": text,
        "parse_mode": parse_mode,
        "disable_web_page_preview": True,
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            r = await client.post(TELEGRAM_SEND_URL, json=payload)
            r.raise_for_status()
            logger.info("Mensagem enviada para %s (status %s)", telegram_id, r.status_code)
            return r.json()
        except Exception as e:
            logger.exception("Erro ao enviar mensagem para %s: %s", telegram_id, e)
            raise


def _format_match_message(match: Match) -> str:
    """
    Gera o texto da notificação que iremos enviar.
    Espera que match.start_time esteja em UTC (ISO / datetime).
    """
    # start_time pode ser None (TBA)
    start_str = "⏰ A definir" if not match.start_time else \
        datetime.fromisoformat(match.start_time.replace("Z", "+00:00")).astimezone(timezone.utc).strftime("%d/%m %H:%M UTC")

    message = (
        f"🔔 <b>Partida em breve</b>\n\n"
        f"🏆 Evento: <b>{match.event or '—'}</b>\n"
        f"🆚 Adversário: <b>{match.opponent}</b>\n"
        f"{'📅 Data e hora: <b>' + start_str + '</b>\\n' if match.start_time else ''}"
        f"🔗 Link: {match.link or '—'}\n\n"
        f"Você receberá essa notificação 1 hora antes da partida — responda /unsubscribe no bot para parar."
    )
    return message


def _matches_to_notify(db: Session, now_utc: datetime):
    """
    Consulta partidas que devem ser notificadas:
    - notified == False
    - start_time is not None and start_time between now and now + NOTIFY_BEFORE_MINUTES
    Assumimos start_time salvo em ISO Z (UTC) ou como datetime no DB.
    """
    window_end = now_utc + timedelta(minutes=NOTIFY_BEFORE_MINUTES)

    # Se a coluna start_time for armazenada como timestamp sem timezone em DB, ajuste conforme sua model.
    stmt = select(Match).where(
        Match.notified == False,
        Match.start_time != None,
        Match.start_time >= now_utc,
        Match.start_time <= window_end
    )

    results = db.execute(stmt).scalars().all()
    return results


def _get_active_subscriptions(db: Session):
    """
    Retorna lista de NotificationSubscription com active=True
    """
    stmt = select(NotificationSubscription).where(NotificationSubscription.active == True)
    return db.execute(stmt).scalars().all()


async def check_and_send_notifications():
    """
    Função cron que:
    - busca partidas para notificar
    - busca usuários inscritos
    - envia mensagens e marca match.notified = True
    """
    now_utc = datetime.now(timezone.utc)
    logger.info("Notifier running — checando partidas entre %s e %s", now_utc, now_utc + timedelta(minutes=NOTIFY_BEFORE_MINUTES))

    db = _get_db()
    try:
        matches = _matches_to_notify(db, now_utc)
        if not matches:
            logger.debug("Nenhuma partida para notificar no momento.")
            return

        subs = _get_active_subscriptions(db)
        if not subs:
            logger.info("Nenhum usuário inscrito — pulando envios.")
            return

        # Enviar mensagem para cada usuário para cada partida encontrada
        for match in matches:
            text = _format_match_message(match)
            for sub in subs:
                try:
                    await send_message_to_telegram(sub.telegram_id, text)
                except Exception as e:
                    # não falhar todo o loop se um envio falhar
                    logger.exception("Falha enviando notificação para %s: %s", sub.telegram_id, e)

            # Depois de tentar enviar para todos os inscritos, marcar a partida como notificada
            try:
                stmt = update(Match).where(Match.id == match.id).values(notified=True)
                db.execute(stmt)
                db.commit()
                logger.info("Marcado match.id=%s como notified=True", match.id)
            except Exception:
                db.rollback()
                logger.exception("Erro marcando partida %s como notificada", match.id)

    except Exception:
        logger.exception("Erro durante check_and_send_notifications")
    finally:
        db.close()


def setup_notifier(app: FastAPI):
    """
    Registra o scheduler nos eventos de startup/shutdown do FastAPI.
    Use no seu main: setup_notifier(app)
    """
    scheduler = AsyncIOScheduler()

    # Trigger: a cada CHECK_INTERVAL_SECONDS
    trigger = IntervalTrigger(seconds=CHECK_INTERVAL_SECONDS)

    scheduler.add_job(check_and_send_notifications, trigger, id="matches_notifier", coalesce=True, max_instances=1)
    logger.info("Job 'matches_notifier' adicionado: interval %s seconds", CHECK_INTERVAL_SECONDS)

    @app.on_event("startup")
    async def _start_scheduler():
        if not scheduler.running:
            scheduler.start()
            logger.info("Notifier scheduler iniciado")

    @app.on_event("shutdown")
    async def _stop_scheduler():
        if scheduler.running:
            scheduler.shutdown()
            logger.info("Notifier scheduler parado")
