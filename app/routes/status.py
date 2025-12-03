from fastapi import APIRouter

router = APIRouter(prefix="/status", tags=["Status"])

@router.get("/")
async def status():
    return {"status": "online"}
