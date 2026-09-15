from fastapi import APIRouter, Depends
from routers.auth import get_current_user

router = APIRouter()

@router.get("/")
async def get_notifications(current_user: dict = Depends(get_current_user)):
    return {"message": "User notifications", "notifications": []}