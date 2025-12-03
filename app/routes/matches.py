from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import Match
from app.schemas import MatchList, MatchCreate
from datetime import datetime

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.post("/save")
def save_matches(payload: MatchList, db: Session = Depends(get_db)):
    saved = []
    for m in payload.matches:
        # Verifica se já existe pela match_id
        existing = db.query(Match).filter_by(match_id=m.match_id).first()
        if existing:
            # Atualiza campos caso tenham mudado (ex.: horário)
            if m.opponent:
                existing.opponent = m.opponent
            if m.event is not None:
                existing.event = m.event
            if m.link is not None:
                existing.link = m.link
            if m.format is not None:
                existing.format = m.format
            if m.start_time is not None:
                existing.start_time = m.start_time
            db.commit()
            db.refresh(existing)
            saved.append(existing)
            continue

        new = Match(
            match_id=m.match_id,
            opponent=m.opponent,
            event=m.event,
            start_time=m.start_time,
            link=m.link,
            format=m.format
        )
        db.add(new)
        db.commit()
        db.refresh(new)
        saved.append(new)

    return {"message": "matches saved", "count": len(saved)}
