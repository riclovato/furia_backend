from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import MatchCreate
from app.crud.matches import (
    create_match,
    get_future_matches,
    get_match_by_match_id
)

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.post("/")
def add_match(data: MatchCreate, db: Session = Depends(get_db)):
    existing = get_match_by_match_id(db, data.match_id)

    if existing:
        return {"message": "Match already exists", "match": existing}

    match = create_match(db, data)
    return {"message": "Match added", "match": match}


@router.get("/future")
def list_future_matches(db: Session = Depends(get_db)):
    matches = get_future_matches(db)
    return {"matches": matches}
