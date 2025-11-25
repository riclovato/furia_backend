from fastapi import APIRouter

router = APIRouter(prefix="/notifications")

@router.get("/")
def root():
    return {"message": "Notifications API is running!"}