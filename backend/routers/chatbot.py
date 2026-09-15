from fastapi import APIRouter, Depends
from routers.auth import get_current_user

router = APIRouter()

@router.post("/chat")
async def chat_with_ai(current_user: dict = Depends(get_current_user)):
    return {"message": "AI chatbot response", "response": "How can I help with your medications?"}