from sqlalchemy.orm import Session
from app.models import Match
from app.schemas import MatchCreate
from datetime import datetime


def create_match(db: Session, data: MatchCreate):
    match = Match(
        match_id=data.match_id,
        opponent=data.opponent,
        event=data.event,
        start_time=data.start_time,
        link=data.link,
        format=data.format
    )
    db.add(match)
    db.commit()
    db.refresh(match)
    return match


def get_match_by_match_id(db: Session, match_id: str):
    return db.query(Match).filter(Match.match_id == match_id).first()


def get_future_matches(db: Session):
    now = datetime.utcnow()
    return db.query(Match).filter(
        Match.start_time > now
    ).all()


def mark_as_notified(db: Session, match_id: str):
    match = get_match_by_match_id(db, match_id)
    if not match:
        return None

    match.notified = True
    db.commit()
    db.refresh(match)
    return match
