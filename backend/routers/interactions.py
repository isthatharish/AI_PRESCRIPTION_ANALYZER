from fastapi import APIRouter, Depends
from routers.auth import get_current_user

router = APIRouter()

@router.post("/check")
async def check_interactions(current_user: dict = Depends(get_current_user)):
    return {"message": "Drug interaction checking", "status": "safe"}