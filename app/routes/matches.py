from fastapi import APIRouter

router = APIRouter(prefix="/matches", tags=["Matches"])

@router.get("/")
async def get_matches():
    # Por enquanto, mock (pode ligar ao seu scraping depois)
    matches = [
        {
            "team1": "FURIA",
            "team2": "G2",
            "time": "2025-11-29 18:00 UTC",
            "event": "BLAST Premier"
        },
        {
            "team1": "FURIA",
            "team2": "NAVI",
            "time": "2025-12-03 16:00 UTC",
            "event": "IEM Global"
        }
    ]

    return {"matches": matches}
