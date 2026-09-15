from fastapi import APIRouter, Depends
from routers.auth import get_current_user

router = APIRouter()

@router.get("/nearby")
async def find_nearby_pharmacies(current_user: dict = Depends(get_current_user)):
    return {"message": "Nearby pharmacies", "pharmacies": []}