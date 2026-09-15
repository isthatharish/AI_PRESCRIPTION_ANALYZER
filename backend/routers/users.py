from fastapi import APIRouter, Depends
from routers.auth import get_current_user

router = APIRouter()

@router.get("/profile")
async def get_profile(current_user: dict = Depends(get_current_user)):
    return {"message": "User profile", "user": current_user}